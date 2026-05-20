import re

BLOCKED_KEYWORDS = ["DELETE", "DROP", "UPDATE", "INSERT", "TRUNCATE", "ALTER", "CREATE", "REPLACE"]


def validate_sql(sql: str) -> tuple[bool, str]:
    """
    Returns (is_valid, error_message).
    Only SELECT queries are allowed.
    """
    cleaned = sql.strip().upper()

    if not cleaned.startswith("SELECT"):
        return False, "Only SELECT queries are allowed."

    for keyword in BLOCKED_KEYWORDS:
        pattern = rf"\b{keyword}\b"
        if re.search(pattern, cleaned):
            return False, f"Query contains forbidden keyword: {keyword}"

    # Block semicolon-chained queries (multiple statements)
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    if len(statements) > 1:
        return False, "Multiple statements are not allowed."

    return True, ""