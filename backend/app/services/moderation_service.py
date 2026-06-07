import re

PROFANITY_PATTERNS = [
    r"\bputa\b", r"\bmerda\b", r"\bporra\b", r"\bcaralho\b", r"\bviado\b",
    r"\bbostinha\b", r"\bbosta\b", r"\bfilha?\s*da\s*puta\b", r"\bvadia\b",
    r"\bputa\s*que\s*pariu\b", r"\bidiota\b", r"\bestupido\b", r"\bcretino\b",
    r"\bimbecil\b", r"\botario\b", r"\bbabaca\b", r"\bartificial\b",
    r"\bshit\b", r"\bfuck\b", r"\bass\b", r"\bbitch\b", r"\bdamn\b",
]

_compiled = re.compile("|".join(PROFANITY_PATTERNS), re.IGNORECASE)

VIOLATION_RESPONSE = (
    "Desculpe, não consigo responder mensagens com linguagem inapropriada. "
    "Por favor, reformule sua pergunta de forma respeitosa."
)


class ModerationService:
    def contains_profanity(self, text: str) -> bool:
        return bool(_compiled.search(text))

    def get_violation_response(self) -> str:
        return VIOLATION_RESPONSE
