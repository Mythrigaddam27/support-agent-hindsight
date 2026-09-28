"""
SupportMemory demo UI.

Run with:  python -m streamlit run app.py

Pick a customer, chat, and watch the Hindsight panel. Turn on
"Compare with no-memory agent" to show the before/after side by side.
"""

import streamlit as st

from agent import respond, groq, GROQ_MODEL
from data.customers import CUSTOMERS

st.set_page_config(page_title="SupportMemory", page_icon="🧠", layout="wide")

TOP_N = 5  # how many recalled memories to show prominently


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
        key = m.lower().split(" | ")[0].strip()
        if key in seen:
            continue
        seen.add(key)
        out.append(m.split(" | ")[0].strip())
        if len(out) == n:
            break
    return out


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


def render_turn(turn: dict) -> None:
    with st.chat_message("user"):
        st.write(turn["message"])

    if compare:
        left, right = st.columns(2)
        with left:
            st.markdown("**Without memory**")
            st.info(turn["baseline"])
        with right:
            st.markdown("**With Hindsight memory**")
            st.success(turn["reply"])
    else:
        with st.chat_message("assistant"):
            st.write(turn["reply"])

    with st.expander(
        f"🧠 Hindsight: {len(turn['memories'])} memories recalled", expanded=True
    ):
        for m in top_memories(turn["memories"]):
            st.markdown(f"- {m}")
        if len(turn["memories"]) > TOP_N:
            with st.expander("Show all recalled memories"):
                for m in turn["memories"]:
                    st.caption(f"- {m}")
        st.markdown("**✨ New experience retained**")
        st.caption(turn["retained"])


for turn in st.session_state[key]:
    render_turn(turn)

if prompt := st.chat_input(f"Message as {selected_name}..."):
    with st.spinner("Recalling context and thinking..."):
        result = respond(customer["customer_id"], customer["name"], prompt)
        baseline = respond_without_memory(customer["name"], prompt) if compare else ""

    turn = {
        "message": prompt,
        "reply": result["reply"],
        "memories": result["memories"],
        "retained": result["retained"],
        "baseline": baseline,
    }
    st.session_state[key].append(turn)
    render_turn(turn)
