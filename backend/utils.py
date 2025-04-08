import re
# Helpers
def extract_policy_number(text: str) -> str | None:
    match = re.search(r'\bP\d+\b', text.upper())
    return match.group(0) if match else None

def extract_claim_number(text: str) -> int | None:
    match = re.search(r'\b\d+\b', text)
    return int(match.group(0)) if match else None