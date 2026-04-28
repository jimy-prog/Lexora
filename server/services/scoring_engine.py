def calculate_ielts_reading_band(raw_score: int) -> float:
    """Standard IELTS Reading Academic curve out of 40"""
    if raw_score >= 39: return 9.0
    if raw_score >= 37: return 8.5
    if raw_score >= 35: return 8.0
    if raw_score >= 33: return 7.5
    if raw_score >= 30: return 7.0
    if raw_score >= 27: return 6.5
    if raw_score >= 23: return 6.0
    if raw_score >= 19: return 5.5
    if raw_score >= 15: return 5.0
    if raw_score >= 13: return 4.5
    if raw_score >= 10: return 4.0
    if raw_score >= 8: return 3.5
    if raw_score >= 6: return 3.0
    if raw_score >= 4: return 2.5
    return 0.0

def calculate_ielts_listening_band(raw_score: int) -> float:
    """Standard IELTS Listening curve out of 40"""
    if raw_score >= 39: return 9.0
    if raw_score >= 37: return 8.5
    if raw_score >= 35: return 8.0
    if raw_score >= 32: return 7.5
    if raw_score >= 30: return 7.0
    if raw_score >= 26: return 6.5
    if raw_score >= 23: return 6.0
    if raw_score >= 18: return 5.5
    if raw_score >= 16: return 5.0
    if raw_score >= 13: return 4.5
    if raw_score >= 10: return 4.0
    if raw_score >= 8: return 3.5
    if raw_score >= 6: return 3.0
    if raw_score >= 4: return 2.5
    return 0.0

def calculate_band(raw_score: int, scope: str) -> float:
    if "Listening" in scope:
        return calculate_ielts_listening_band(raw_score)
    else:
        # Default to reading curve for now
        return calculate_ielts_reading_band(raw_score)

def normalize_text(text: str) -> str:
    """Normalizes answer text for gap fill comparison."""
    if not text:
        return ""
    # Lowercase, strip whitespace, remove multiple spaces
    text = text.lower().strip()
    import re
    text = re.sub(r'\s+', ' ', text)
    # Remove simple punctuation at ends if present
    text = text.strip('.!?,')
    return text
