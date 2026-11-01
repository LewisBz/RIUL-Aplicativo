import re
import unicodedata
from collections.abc import Callable


def slugify(text: str, max_length: int = 80) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return (slug or "item")[:max_length].strip("-")


def unique_slug(text: str, exists: Callable[[str], bool], max_length: int = 80) -> str:
    base = slugify(text, max_length - 6)
    candidate, counter = base, 2
    while exists(candidate):
        candidate = f"{base}-{counter}"
        counter += 1
    return candidate
