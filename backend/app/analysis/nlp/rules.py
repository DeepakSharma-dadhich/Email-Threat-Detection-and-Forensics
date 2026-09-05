CATEGORY_PATTERNS = {

    "urgency": [
        r"\burgent\b",
        r"\bimmediately\b",
        r"\basap\b",
        r"\bwithin\s+\d+\s*(?:hours?|minutes?)\b",
        r"\bact now\b",
        r"\bexpires? today\b",
        r"\bfinal warning\b",
    ],

    "credential_request": [
        r"\bverify (?:your )?(?:account|identity|password)\b",
        r"\bconfirm (?:your )?(?:login|credentials|password)\b",
        r"\benter (?:your )?(?:password|credentials|otp|one[- ]time password)\b",
        r"\bsign in to (?:verify|continue|avoid)\b",
    ],

    "financial_request": [
        r"\bwire transfer\b",
        r"\bbank transfer\b",
        r"\bpayment (?:is )?due\b",
        r"\bupdate (?:your )?bank\b",
        r"\bgift cards?\b",
        r"\binvoice\b",
        r"\bbeneficiary\b",
    ],

    "threat_pressure": [
        r"\baccount (?:will be|has been) (?:suspended|locked|closed)\b",
        r"\blegal action\b",
        r"\bpenalty\b",
        r"\bservice will be terminated\b",
    ],

    "secrecy": [
        r"\bconfidential\b",
        r"\bdo not tell\b",
        r"\bkeep this between us\b",
        r"\bdo not contact\b",
    ],

    "impersonation_bec": [
        r"\b(?:ceo|cfo|director|manager|boss)\b.*\b(?:need|request|transfer|payment)\b",
        r"\bare you available\b.*\b(?:quick task|favor)\b",
        r"\bchange of bank details\b",
    ],

    "link_action": [
        r"\bclick (?:here|the link|below)\b",
        r"\bopen the link\b",
        r"\buse the link\b",
        r"\blogin here\b",
    ],
}