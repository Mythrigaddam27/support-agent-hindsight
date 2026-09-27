"""
The core support agent loop.

For every customer message:
  1. RECALL relevant memories about this customer from Hindsight
  2. Inject that context into the LLM prompt
  3. Generate a response with Groq
  4. RETAIN the new exchange back into Hindsight, so the agent keeps
     learning across the conversation and across future contacts

This is intentionally one small, readable loop -- the point of the demo
is the memory behavior, not agent complexity.
"""

import os
from dotenv import load_dotenv
from hindsight_client import Hindsight
from groq import Groq

from seed_memory import bank_id_for

load_dotenv()

hindsight = Hindsight(
    base_url=os.environ["HINDSIGHT_BASE_URL"],
    api_key=os.environ["HINDSIGHT_API_KEY"],
)

groq = Groq(api_key=os.environ["GROQ_API_KEY"])
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")

SYSTEM_PROMPT = """You are a customer support agent for an e-commerce brand.
You have access to this customer's memory: past orders, past tickets, and
their stated preferences. Use that context naturally -- don't say "according
to my memory" or "I recall that". Just act like a support rep who has read
the customer's file before picking up the phone.

If the memory context below is empty, this is a brand-new customer -- ask
the standard clarifying questions you'd ask anyone.

Be concise and helpful. Match the customer's stated preferences (e.g. if
they prefer short numbered steps, give short numbered steps; if they prefer
replacements over refunds, offer a replacement first).
"""


def respond(customer_id: str, customer_name: str, message: str) -> str:
    bank_id = bank_id_for(customer_id)

    # 1. RECALL -- pull relevant memory before responding
    recall_result = hindsight.recall(
        bank_id=bank_id,
        query=message,
    )
    memory_context = "\n".join(f"- {m.text}" for m in recall_result.results)

    # 2 & 3. Build the prompt and generate a response
    user_prompt = f"""Customer: {customer_name} (id: {customer_id})

Relevant memory about this customer:
{memory_context if memory_context else "(no memory yet -- new customer)"}

Customer's message:
{message}
"""

    completion = groq.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    reply = completion.choices[0].message.content

    # 4. RETAIN -- store this exchange so future contacts remember it too
    hindsight.retain(
        bank_id=bank_id,
        content=f"Customer {customer_name} said: \"{message}\". Support replied: \"{reply}\"",
    )

    return reply


if __name__ == "__main__":
    # Quick manual smoke test from the command line
    cid = input("Customer ID (e.g. cust_1042): ").strip()
    name = input("Customer name: ").strip()
    while True:
        msg = input(f"\n{name}: ")
        if msg.lower() in ("quit", "exit"):
            break
        answer = respond(cid, name, msg)
        print(f"\nAgent: {answer}")
