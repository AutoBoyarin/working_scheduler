import re

BAD_WORDS = {
    "trash_talk": ["дебил", "идиот", "лох", "урод", "мразь"],
    "politics": ["президент", "выборы", "путин", "байден", "митинг"],
    "crypto": ["крипта", "биткоин", "bitcoin", "ethereum", "eth", "nft"]
}

REPLACEMENTS = {
    "0": "о", "1": "и", "3": "е", "@": "а", "$": "с"
}

def normalize_text(text: str) -> str:
    text = text.lower()
    for k, v in REPLACEMENTS.items():
        text = text.replace(k, v)
    text = re.sub(r"[^a-zа-яё\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text

def moderate_text(text: str):
    normalized = normalize_text(text)
    detections = []

    for category, words in BAD_WORDS.items():
        for word in words:
            if word in normalized:
                detections.append({
                    "type": "text",
                    "category": category,
                    "value": word
                })

    return detections
