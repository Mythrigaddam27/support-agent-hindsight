"""
SupportMemory - Hindsight-powered customer support agent.

Flow:
1. RECALL relevant customer memories from Hindsight
2. Apply company support policy separately
3. Generate a personalized but policy-grounded response
4. RETAIN a factual interaction summary
5. Return recalled memories and retained experience for the UI
"""

import os
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from hindsight_client import Hindsight
from groq import Groq

from seed_memory import bank_id_for


load_dotenv()


# ---------------------------------------------------------
# CLIENTS
# ---------------------------------------------------------

def _hindsight_call(method: str, **kwargs):
    """
    Call a Hindsight client method safely from Streamlit.

    Streamlit runs the script in a fresh thread on every interaction, and the
    Hindsight sync client binds its web session to the first event loop that
    uses it. So we open a short-lived client inside a clean worker thread for
    each call, then close it.
    """
    def run():
        with Hindsight(
            base_url=os.environ["HINDSIGHT_BASE_URL"],
            api_key=os.environ["HINDSIGHT_API_KEY"],
        ) as client:
            return getattr(client, method)(**kwargs)

    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(run).result()

groq = Groq(
    api_key=os.environ["GROQ_API_KEY"]
)

GROQ_MODEL = os.environ.get(
    "GROQ_MODEL",
    "openai/gpt-oss-120b",
)


# ---------------------------------------------------------
# SUPPORT POLICY
# ---------------------------------------------------------
# Customer memory provides context.
# This policy controls what the agent is actually allowed to promise.

SUPPORT_POLICY = """
SUPPORT POLICY

The agent may:
- acknowledge the customer's issue
- reference verified customer/order history from memory
- ask for information needed to investigate an issue
- ask for a photo when damage needs verification
- ask the customer to confirm their delivery address when relevant
- explain the next support step

The agent must NOT promise or claim any of the following unless an
explicit company policy or verified operational record supplied in the
context authorizes it:
- free replacement
- express shipping
- same-day dispatch
- refunds
- discounts
- compensation
- tracking numbers
- guaranteed delivery dates
- completed operational actions

IMPORTANT:
Customer memory is context, NOT authorization.

For example, if memory says that a customer previously received a
replacement, that does not mean a new replacement has already been
approved.

If an action has not been explicitly confirmed, describe it as a
possible next step or ask for the information needed to proceed.
"""


# ---------------------------------------------------------
# SYSTEM PROMPT
# ---------------------------------------------------------

SYSTEM_PROMPT = f"""
You are SupportMemory, an AI customer support agent for an e-commerce
company.

Your key capability is persistent customer memory.

Before answering:
1. Read the relevant customer memories.
2. Identify which memories actually relate to the current issue.
3. Use those memories to personalize the response.
4. Follow the support policy below.

{SUPPORT_POLICY}

MEMORY RULES

- Memory provides customer context, not business authorization.
- Never treat an old AI-generated response as proof that an action has
  been approved or completed.
- Never invent company policies.
- Never invent operational actions.
- Never claim that a replacement, refund, shipment, or compensation has
  already been created unless that fact is explicitly verified.
- If information is missing, ask a clear follow-up question.
- If the customer reports a repeated problem, acknowledge the previous
  context so they do not have to repeat their entire history.
- Never say a replacement, refund, or shipment will be started,
  arranged, or processed. Say the photo and address will be used
  "to help determine the appropriate next step."
- Keep responses concise and practical.

Do not say:
"According to my memory..."
"I retrieved this from Hindsight..."
"My memory says..."

Instead, naturally use the customer's history as if you are a support
representative who already knows their account.
"""


# ---------------------------------------------------------
# RESPOND
# ---------------------------------------------------------

def respond(
    customer_id: str,
    customer_name: str,
    message: str,
) -> dict:

    bank_id = bank_id_for(customer_id)

    # -----------------------------------------------------
    # 1. RECALL CUSTOMER MEMORY
    # -----------------------------------------------------

    recall_query = f"""
Customer: {customer_name}
Customer ID: {customer_id}

Current issue:
{message}

Find customer-specific context relevant to this request, including:
- previous orders
- previous support issues
- repeated problems
- customer preferences
- relevant past interactions
"""

    recall_result = _hindsight_call(
        "recall",
        bank_id=bank_id,
        query=recall_query,
    )

    memories = []

    for memory in recall_result.results:
        text = getattr(memory, "text", None)

        if text:
            cleaned = text.strip()

            if cleaned:
                memories.append(cleaned)

    memory_context = "\n".join(
        f"- {memory}"
        for memory in memories
    )

    if not memory_context:
        memory_context = "(No relevant customer memory found.)"


    # -----------------------------------------------------
    # 2. BUILD LLM CONTEXT
    # -----------------------------------------------------

    user_prompt = f"""
CUSTOMER
Name: {customer_name}
ID: {customer_id}

RELEVANT HINDSIGHT MEMORY
{memory_context}

CURRENT CUSTOMER MESSAGE
{message}

Respond to the customer's current issue.

Use relevant customer history to make the response personalized.

Remember:
- Memory is customer context.
- Memory is NOT authorization for refunds, replacements,
  shipping promises, compensation, or other operational actions.
- Do not claim that an action has already happened unless it is
  explicitly verified.
"""


    # -----------------------------------------------------
    # 3. GENERATE RESPONSE
    # -----------------------------------------------------

    completion = groq.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )

    reply = completion.choices[0].message.content.strip()


    # -----------------------------------------------------
    # 4. RETAIN A FACTUAL EXPERIENCE
    # -----------------------------------------------------
    #
    # IMPORTANT:
    # Do NOT store the entire assistant response.
    # Otherwise an invented promise could become future memory.
    #

    retained_experience = (
        f"Customer {customer_name} ({customer_id}) reported: "
        f"\"{message}\". "
        f"Support interaction completed for this request. "
        f"No replacement, refund, shipping, compensation, or other "
        f"operational action should be treated as confirmed unless "
        f"separately verified."
    )

    _hindsight_call(
        "retain",
        bank_id=bank_id,
        content=retained_experience,
    )


    # -----------------------------------------------------
    # 5. RETURN DATA FOR STREAMLIT
    # -----------------------------------------------------

    return {
        "reply": reply,
        "memories": memories,
        "retained": retained_experience,
    }


# ---------------------------------------------------------
# COMMAND-LINE TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    cid = input(
        "Customer ID (e.g. cust_1042): "
    ).strip()

    name = input(
        "Customer name: "
    ).strip()

    while True:

        msg = input(
            f"\n{name}: "
        )

        if msg.lower() in ("quit", "exit"):
            break

        result = respond(
            cid,
            name,
            msg,
        )

        print("\n--- HINDSIGHT MEMORY ---")

        if result["memories"]:

            for memory in result["memories"]:
                print(f"- {memory}")

        else:
            print("- No relevant memory found.")

        print("\n--- AGENT ---")
        print(result["reply"])

        print("\n--- RETAINED EXPERIENCE ---")
        print(result["retained"])
