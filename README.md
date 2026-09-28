# SupportMemory

A customer support agent that remembers every customer across contacts, using [Hindsight](https://github.com/vectorize-io/hindsight) as its persistent memory layer.

A stateless support bot asks every customer to explain their problem from scratch. SupportMemory recalls the customer's orders, past tickets, and preferences before it answers, so a vague message like *"Hi, I have an issue with my order"* is enough for it to name the right orders and reference the previous issue.

## Before and after

Same customer, same LLM, same message. The only difference is memory.

| Without memory | With Hindsight memory |
|---|---|
| Asks for the order number, the item, a description, and the order date. | Names both orders on file (#ORD-88213 and #ORD-91765), mentions the cracked jar reported in August, and asks which order the issue is about. |

The demo UI shows both answers side by side, with the memories Hindsight recalled and the new experience it retained.

<!-- Add screenshots here: docs/before-after.png -->

## How Hindsight memory is used

Every customer message goes through one loop in `agent.py`:

1. **Recall.** The agent asks Hindsight for context relevant to this customer and this message (past orders, past issues, preferences).
2. **Apply policy.** Company support policy is kept separate from memory. Memory says what happened; policy says what the agent may promise.
3. **Generate.** The LLM (Groq, `openai/gpt-oss-120b`) answers using the recalled context.
4. **Retain.** A short factual summary of what the customer reported is written back to Hindsight.

Each customer has their own memory bank (`support-<version>-<customer_id>`), so one customer's history can never leak into another's conversation.

### Design decision: memory is not authorization

An early version retained the full exchange, including the agent's own reply. That is risky: if the agent ever said "I'll open a replacement request", that sentence would be stored and later recalled as if it were fact.

Two changes fixed this:

- **Retain only what the customer reported**, plus a note that no replacement, refund, shipping, or compensation should be treated as confirmed unless separately verified. The agent's own words are never stored.
- **Keep support policy separate from memory.** The system prompt lists what the agent may do (acknowledge, ask for a photo or address, explain the next step) and what it must not promise without a verified record.

## Project structure

```
agent.py           recall -> policy -> generate -> retain loop
app.py             Streamlit demo UI with a before/after comparison
seed_memory.py     seeds each demo customer's Hindsight memory bank
data/customers.py  sample customers with order and ticket history
```

## Run it

1. Create a Hindsight Cloud account and API key, and a Groq API key.
2. Create a `.env` file in the project root:

   ```
   HINDSIGHT_API_KEY=your-hindsight-key
   HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
   GROQ_API_KEY=your-groq-key
   GROQ_MODEL=openai/gpt-oss-120b
   ```

3. Install and seed:

   ```
   python -m pip install -r requirements.txt
   python seed_memory.py
   ```

4. Start the demo:

   ```
   python -m streamlit run app.py
   ```

5. Pick **Ananya Rao**, send *"Hi, I have an issue with my order"*, then *"It's about the mixer grinder, the jar arrived damaged again"*.

To reset every customer to a clean memory bank, change `BANK_VERSION` in `seed_memory.py` (for example `v2` to `v3`) and run `python seed_memory.py` again.

## Limitations

- Customers, orders, and tickets are sample data written for the demo.
- Support policy is a fixed block in the prompt. A production system would check real order and refund records before letting the agent promise anything.
- Tested by hand on a small number of conversations, not benchmarked.
- The Hindsight sync client is called from a short-lived worker thread per request to avoid event-loop conflicts with Streamlit.
