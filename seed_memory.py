"""
Seed each customer's Hindsight memory bank with their backstory.

Run this ONCE before the demo. It retains each customer's past orders,
tickets, and preferences into their own memory bank (one bank per customer
keeps recall clean and avoids cross-customer leakage).

Usage:
    python seed_memory.py
"""

import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

from data.customers import CUSTOMERS

load_dotenv()

client = Hindsight(
    base_url=os.environ["HINDSIGHT_BASE_URL"],
    api_key=os.environ["HINDSIGHT_API_KEY"],
)

# Bump this (v3, v4, ...) to start every customer from clean memory banks.
BANK_VERSION = "v4"


def bank_id_for(customer_id: str) -> str:
    """One bank per customer -- keeps memory scoped and recall fast."""
    known_customer_ids = {customer["customer_id"] for customer in CUSTOMERS}
    if customer_id not in known_customer_ids:
        raise ValueError(f"Unknown customer ID: {customer_id}")
    return f"support-{BANK_VERSION}-{customer_id}"


def seed_customer(customer: dict) -> None:
    bank_id = bank_id_for(customer["customer_id"])
    print(f"Seeding memory for {customer['name']} ({bank_id})...")

    for event in customer["backstory_events"]:
        client.retain(bank_id=bank_id, content=event)

    print(f"  -> retained {len(customer['backstory_events'])} memories.")


if __name__ == "__main__":
    for customer in CUSTOMERS:
        seed_customer(customer)
    print("\nDone. Each customer's memory bank is ready for the demo.")