# Support Agent with Memory

A customer support agent that remembers every customer across contacts —
past orders, past tickets, and stated preferences — instead of starting
from zero on every conversation.

## The problem

Generic support agents (and most support reps working off a ticket queue)
treat every conversation as the first one. Customers repeat themselves,
agents re-ask the same clarifying questions, and preferences learned in
one ticket vanish by the next.

## How memory is used

This agent uses [Hindsight](https://github.com/vectorize-io/hindsight) as
its memory layer, with **one memory bank per customer**:

- **Retain** — after every exchange, the conversation is written back into
  that customer's memory bank, so it accumulates over time (see
  `agent.py::respond`).
- **Recall** — before generating a reply, the agent queries Hindsight for
  memories relevant to the customer's current message (past orders,
  tickets, and preferences) and injects them into the prompt.
- Because memory is scoped per customer, the agent can hold context for
  *any number* of customers simultaneously without them bleeding into
  each other.

The result: on a customer's first-ever contact the agent behaves like any
generic support bot. On their second contact — even days later — it already
knows their order number, what went wrong last time, and how they like to
be helped.

## Project structure

```
data/customers.py    # synthetic customer backstories (orders, past tickets)
seed_memory.py        # one-time script: retains each customer's backstory
agent.py               # the retain/recall loop + Groq LLM call
app.py                  # Streamlit chat UI for the live demo
```

## Running it

1. Copy `.env.example` to `.env` and fill in your Hindsight and Groq API keys.
2. `pip install -r requirements.txt`
3. `python seed_memory.py` — seeds each demo customer's memory bank.
4. `streamlit run app.py` — opens the chat UI. Pick a customer from the
   sidebar and start chatting.

## The demo moment

Message the agent as a customer with something generic like *"Hi, I have an
issue with my order"* — the agent will already reference their actual order
number, prior ticket, and preference (e.g. replacement over refund) without
you telling it anything. That's the memory working.
