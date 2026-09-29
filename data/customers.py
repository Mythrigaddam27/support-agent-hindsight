"""
Synthetic customer data for the demo.

Each customer has a backstory: past orders, a prior support ticket, and a
quirk/preference. This is what we'll retain into Hindsight to seed memory
before the "second contact" demo moment.

Keep this realistic-looking (real-sounding names, order numbers, dates,
product names) -- that's what sells the demo.
"""

CUSTOMERS = [
    {
    "customer_id": "cust_1042",
    "name": "Ananya Rao",
    "email": "ananya.rao@gmail.com",
    "backstory_events": [
        "Ananya Rao (customer cust_1042) placed order #ORD-88213 on 2026-08-02 for a Bosch Series 6 mixer grinder, delivered 2026-08-06.",
        "On 2026-08-10, Ananya Rao contacted support because the mixer grinder's jar and lid were cracked on arrival. Support issued a free replacement jar, shipped 2026-08-12.",
        "Ananya Rao mentioned a strong preference for replacements over refunds because the appliance is needed quickly for a home bakery business.",
        "On 2026-09-01, Ananya Rao placed a second order #ORD-91765 for a set of 6 stainless steel mixing bowls.",
    ],
},
    {
        "customer_id": "cust_2078",
        "name": "Steven",
        "email": "steven@outlook.com",
        "backstory_events": [
            "Steven (customer cust_2078) placed order #ORD-77410 on 2026-07-15 for a Dell Inspiron 15 laptop, delivered 2026-07-20.",
            "On 2026-08-25, Steven contacted support reporting the laptop's battery was draining unusually fast. Support guided Steven through a BIOS power-plan reset, which resolved it.",
            "Steven noted that they are not very technical and get frustrated by long troubleshooting steps; they prefer short, numbered instructions over long explanations.",
            "On 2026-09-10, Steven contacted support again, this time about the laptop's Wi-Fi dropping intermittently.",
        ],
    },
    {
        "customer_id": "cust_3391",
        "name": "Max",
        "email": "max@yahoo.com",
        "backstory_events": [
            "Max (customer cust_3391) placed order #ORD-65029 on 2026-06-10 for a Samsung 55-inch QLED TV, delivered 2026-06-14.",
            "On 2026-06-18, Max contacted support because the TV remote was missing from the box. Support shipped a replacement remote at no cost.",
            "On 2026-07-30, Max contacted support again about a faint horizontal line on the screen. After troubleshooting, support arranged an on-site technician visit for 2026-08-03, which fixed a loose panel connector.",
            "Max mentioned working from home and needing at least 24 hours' notice before any technician visit.",
        ],
    },
]
