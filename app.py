"""
SupportMemory demo UI (animated).

Run with:  python -m streamlit run app.py

Pick a customer, chat, and watch the Hindsight panel. Turn on
"Compare with no-memory agent" to show the before/after side by side.
"""

import html
import time

import streamlit as st

from agent import respond, groq, GROQ_MODEL
from data.customers import CUSTOMERS

st.set_page_config(page_title="SupportMemory", page_icon="🧠", layout="wide")

TOP_N = 5  # how many recalled memories to show prominently

STYLE = """
<style>
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: none; }
}
@keyframes glow {
  0%   { box-shadow: 0 0 0 0 rgba(25,195,125,.55); }
  100% { box-shadow: 0 0 0 14px rgba(25,195,125,0); }
}
.mem-card {
  border-left: 3px solid #7c5cff;
  background: rgba(124,92,255,.10);
  padding: 8px 12px; margin: 6px 0; border-radius: 6px;
  animation: fadeUp .5s ease both;
}
.retained-card {
  border-left: 3px solid #19c37d;
  background: rgba(25,195,125,.10);
  padding: 8px 12px; margin: 10px 0 4px 0; border-radius: 6px;
  animation: fadeUp .5s ease both, glow 1.4s ease-out 1;
}
.col-tag { font-weight: 600; margin-bottom: 4px; }
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)


def respond_without_memory(customer_name: str, message: str) -> str:
    """Baseline agent: same LLM, no customer history."""
    completion = groq.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a customer support agent for an e-commerce "
                    "company. You have NO access to the customer's order "
                    "history or past tickets. Ask the clarifying questions "
                    "you need. Never promise refunds, replacements, "
                    "shipping, or compensation. Keep it concise."
                ),
            },
            {"role": "user", "content": f"Customer name: {customer_name}\n\n{message}"},
        ],
    )
    return completion.choices[0].message.content.strip()


def top_memories(memories: list[str], n: int = TOP_N) -> list[str]:
    """Dedupe (case-insensitive) and keep the first n."""
    seen, out = set(), []
    for m in memories:
        short = m.split(" | ")[0].strip()
        key = short.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(short)
        if len(out) == n:
            break
    return out


def typing(text: str, delay: float = 0.025):
    """Generator that streams text word by word."""
    for word in text.split(" "):
        yield word + " "
        time.sleep(delay)


def show_text(container, text: str, animate: bool) -> None:
    if animate:
        container.write_stream(typing(text))
    else:
        container.write(text)


def render_memory_panel(turn: dict, animate: bool) -> None:
    with st.expander(
        f"🧠 Hindsight: {len(turn['memories'])} memories recalled", expanded=True
    ):
        cards = "".join(
            f'<div class="mem-card" style="animation-delay:{i * 0.15}s">'
            f"{html.escape(m)}</div>"
            for i, m in enumerate(top_memories(turn["memories"]))
        )
        st.markdown(cards, unsafe_allow_html=True)

        if len(turn["memories"]) > TOP_N:
            with st.expander("Show all recalled memories"):
                for m in turn["memories"]:
                    st.caption(f"- {m}")

        delay = 0.15 * TOP_N + 0.2
        st.markdown(
            f'<div class="retained-card" style="animation-delay:{delay}s">'
            f"<b>✨ New experience retained</b><br>"
            f"{html.escape(turn['retained'])}</div>",
            unsafe_allow_html=True,
        )


def render_turn(turn: dict, compare: bool, animate: bool = False) -> None:
    with st.chat_message("user"):
        st.write(turn["message"])

    if compare:
        left, right = st.columns(2)
        with left:
            st.markdown('<div class="col-tag">Without memory</div>', unsafe_allow_html=True)
            box = st.container(border=True)
            show_text(box, turn["baseline"], animate)
        with right:
            st.markdown('<div class="col-tag">🧠 With Hindsight memory</div>', unsafe_allow_html=True)
            box = st.container(border=True)
            show_text(box, turn["reply"], animate)
    else:
        with st.chat_message("assistant"):
            show_text(st, turn["reply"], animate)

    render_memory_panel(turn, animate)


st.title("🧠 SupportMemory")
st.caption("A support agent that learns from every interaction using persistent Hindsight memory.")

customer_options = {c["name"]: c for c in CUSTOMERS}

with st.sidebar:
    st.header("Simulate a customer")
    selected_name = st.selectbox("Customer", list(customer_options.keys()))
    customer = customer_options[selected_name]
    st.caption(f"Customer ID: {customer['customer_id']}")
    compare = st.toggle("Compare with no-memory agent", value=True)
    st.divider()
    st.markdown(
        "**Try:** *Hi, I have an issue with my order*\n\n"
        "Then: *It's about the mixer grinder, the jar arrived damaged again*"
    )
    if st.button("Clear chat display"):
        st.session_state.pop(f"turns_{customer['customer_id']}", None)
        st.rerun()

key = f"turns_{customer['customer_id']}"
st.session_state.setdefault(key, [])

for turn in st.session_state[key]:
    render_turn(turn, compare, animate=False)

if prompt := st.chat_input(f"Message as {selected_name}..."):
    with st.status(
        "🧠 Hindsight: recalling memories → responding → retaining…", expanded=False
    ) as status:
        result = respond(customer["customer_id"], customer["name"], prompt)
        baseline = respond_without_memory(customer["name"], prompt) if compare else ""
        status.update(
            label=(
                f"✅ Recalled {len(result['memories'])} memories · "
                f"retained 1 new experience"
            ),
            state="complete",
        )

    turn = {
        "message": prompt,
        "reply": result["reply"],
        "memories": result["memories"],
        "retained": result["retained"],
        "baseline": baseline,
    }
    st.session_state[key].append(turn)
    render_turn(turn, compare, animate=True)