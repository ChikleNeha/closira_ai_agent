"""
sop.py — SOP data source for Bloom Aesthetics Clinic.

This is the single source of truth the AI is allowed to answer from.
All stages load SOP text from here. The AI is explicitly instructed
never to answer from outside this data.
"""

SOP_TEXT = """
BUSINESS: Bloom Aesthetics Clinic
LOCATION: London, UK

HOURS:
- Monday to Saturday: 9:00 AM – 7:00 PM
- Sunday: Closed

SERVICES AND PRICING:
- Botox: from £200 per area
- Dermal Fillers: from £250 per area
- Free Consultation: available before any treatment, no obligation

BOOKING:
- Bookings can be made via WhatsApp or the clinic website
- 24-hour cancellation notice is required to avoid a cancellation fee
- Walk-ins are not accepted; appointments only

PAYMENTS:
- We accept card payments and bank transfers
- No cash payments
- A deposit may be required to secure a booking

AFTERCARE:
- Aftercare advice is provided after every treatment
- Follow-up appointments are available if needed
- Results vary per individual

ESCALATE IMMEDIATELY IF:
- Customer has a medical question or concern
- Customer is making a complaint
- Customer wants to negotiate pricing
- More than 2 questions in a row cannot be answered from this SOP
- Customer explicitly asks to speak to a human
- Customer expresses anger, frustration, or urgency

DO NOT answer questions about:
- Specific medical advice or contraindications
- Exact treatment outcomes or guarantees
- Staff names or qualifications (not in SOP)
- Any service not listed above
""".strip()


def get_sop() -> str:
    return SOP_TEXT
