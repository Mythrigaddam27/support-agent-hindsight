"""
Minimal Streamlit demo UI.

Run with:  streamlit run app.py

Pick a customer from the sidebar, chat with the agent, then switch to a
different "session" (or just refresh and pick the same customer again) to
show the before/after: the agent already knows their history.
"""

import streamlit as st
from agent import respond
from data.customers import CUSTOMERS

st.set_page_config(page_title="Support Agent (with memory)", page_icon="🧠")
st.title("🧠 Support Agent — powered by Hindsight memory")

customer_options = {c["name"]: c for c in CUSTOMERS}

with st.sidebar:
    st.header("Simulate a customer")
    selected_name = st.selectbox("Choose a customer", list(customer_options.keys()))
    customer = customer_options[selected_name]
    st.caption(f"Customer ID: {customer['customer_id']}")
    st.divider()
    st.markdown(
        "**Try this:** Ask a generic question first (e.g. *\"Hi, I have an "
        "issue with my order\"*) and watch the agent already reference their "
        "past order, ticket, and preferences -- without you telling it anything."
    )
    if st.button("Clear chat display"):
        st.session_state.pop(f"messages_{customer['customer_id']}", None)
        st.rerun()

session_key = f"messages_{customer['customer_id']}"
if session_key not in st.session_state:
    st.session_state[session_key] = []

for msg in st.session_state[session_key]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input(f"Message as {selected_name}..."):
    st.session_state[session_key].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Recalling context and thinking..."):
            reply = respond(customer["customer_id"], customer["name"], prompt)
        st.write(reply)

    st.session_state[session_key].append({"role": "assistant", "content": reply})
