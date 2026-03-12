from typing import Tuple, List, Dict, Optional

# ── KEYWORD GROUPS ─────────────────────────────────────────────────────
KEYWORD_GROUPS: List[Dict] = [
    {
        "level": "critical",
        "score": -95,
        "words": [
            "suicide", "kill myself", "end my life", "want to die",
            "can't go on", "no reason to live", "self harm", "hurt myself",
            "take my life", "don't want to live", "wish i was dead",
            "better off dead", "end it all", "ending my life"
        ]
    },
    {
        "level": "high",
        "score": -75,
        "words": [
            "hopeless", "worthless", "nobody cares", "give up",
            "can't take it", "hate myself", "empty inside",
            "don't want to wake up", "no point", "life is meaningless",
            "nothing matters", "completely alone", "no hope"
        ]
    },
    {
        "level": "medium",
        "score": -50,
        "words": [
            "so tired", "exhausted", "anxious", "scared", "alone",
            "depressed", "crying", "can't sleep", "overwhelmed",
            "stressed", "panic", "lost", "broken", "miserable",
            "sad", "upset", "frustrated", "i hate", "falling apart"
        ]
    },
    {
        "level": "mild_negative",
        "score": -25,
        "words": [
            "worried", "nervous", "difficult", "hard", "confused",
            "tired", "bored", "annoyed", "pressure", "tense"
        ]
    },
    {
        "level": "neutral",
        "score": 0,
        "words": [
            "okay", "fine", "alright", "not bad", "normal", "usual"
        ]
    },
    {
        "level": "positive",
        "score": 40,
        "words": [
            "happy", "good", "great", "better", "calm", "love",
            "thankful", "grateful", "hopeful", "excited", "motivated",
            "joy", "peaceful", "content", "proud", "optimistic"
        ]
    },
    {
        "level": "very_positive",
        "score": 70,
        "words": [
            "amazing", "wonderful", "fantastic", "much better",
            "feeling good", "excellent", "blessed", "thriving"
        ]
    }
]

INDIAN_CRISIS_HELPLINES = [
    {"name": "iCall",               "number": "9152987821",   "hours": "Mon–Sat 8AM–10PM"},
    {"name": "Vandrevala Foundation","number": "1860-2662-345","hours": "24/7"},
    {"name": "NIMHANS",             "number": "080-46110007", "hours": "24/7"},
    {"name": "iCall WhatsApp",      "number": "9152987821",   "hours": "WhatsApp available"},
]


def analyse_sentiment(text: str) -> Tuple[float, str]:
    """
    Returns (score, level).
    Score: -100 (most negative) to +100 (most positive).
    Level: critical | high | medium | mild_negative | neutral | positive | very_positive
    """
    lower = text.lower()
    total_score = 0.0
    matched_any = False
    highest_severity = None
    highest_severity_score = 0

    for group in KEYWORD_GROUPS:
        for word in group["words"]:
            if word in lower:
                total_score += group["score"]
                matched_any = True
                # Track most severe match
                if abs(group["score"]) > abs(highest_severity_score):
                    highest_severity = group["level"]
                    highest_severity_score = group["score"]

    if not matched_any:
        return 0.0, "neutral"

    # Clamp
    total_score = max(-100.0, min(100.0, total_score))

    # Determine label from clamped score
    level = _score_to_level(total_score)
    return round(total_score, 1), level


def _score_to_level(score: float) -> str:
    if score >= 40:  return "positive"
    if score >= -20: return "neutral"
    if score >= -50: return "mild_negative"
    if score >= -65: return "medium"
    if score >= -85: return "high"
    return "critical"


def is_crisis(level: str) -> bool:
    return level in ("critical", "high")


def get_helplines() -> List[Dict]:
    return INDIAN_CRISIS_HELPLINES


def get_bot_reply(score: float, level: str, history: Optional[List[Dict]] = None) -> str:
    # Basic replies
    replies = {
        "critical": (
            "I'm really concerned about what you just shared. "
            "Please know that you matter deeply, and help is available right now. "
            "A trained counsellor can support you — will you reach out? 🙏💙"
        ),
        "high": (
            "What you're feeling sounds really painful, and I don't want you "
            "to carry this alone. You deserve support. A caring counsellor can "
            "help — would you like their number? 💙"
        ),
        "medium": (
            "It sounds like you're going through something really tough right now. "
            "I'm here with you. Have you tried the breathing exercise? "
            "It can help calm your nervous system 🫁"
        ),
        "mild_negative": (
            "That sounds stressful. It's okay to feel this way — "
            "you're not alone in facing these challenges. "
            "What's been weighing on you the most? 💙"
        ),
        "neutral": (
            "Thank you for sharing. I'm here to listen — "
            "feel free to tell me more about how you're feeling. 🤍"
        ),
        "positive": (
            "That's wonderful to hear! 😊 "
            "What's been making you feel this way? "
            "It's great to celebrate the good moments."
        ),
        "very_positive": (
            "I love hearing that! 🌟 "
            "Keep nurturing that positive energy — you deserve it!"
        ),
    }

    base_reply = replies.get(level, replies["neutral"])

    # History-aware enhancements
    if history and len(history) > 0:
        # Check if the user has been consistently negative
        recent_user_msgs = [m for m in history if m.get("role") == "user"][-3:]
        recent_levels = [m.get("sentiment_level") for m in recent_user_msgs if m.get("sentiment_level")]
        
        is_consistently_down = all(l in ("critical", "high", "medium", "mild_negative") for l in recent_levels)
        
        if is_consistently_down and level in ("critical", "high", "medium", "mild_negative"):
            base_reply = "I've noticed you've been having a really tough time lately. " + base_reply
        elif any(l in ("positive", "very_positive") for l in recent_levels) and level in ("mild_negative", "medium"):
            base_reply = "I'm sorry to see things have taken a bit of a turn. You were feeling better earlier — we can get back there. " + base_reply
        
        # Keyword-specific guidance from history
        historical_text = " ".join([m.get("content", "").lower() for m in recent_user_msgs])
        if "exam" in historical_text and level in ("medium", "mild_negative"):
            base_reply = "I know you've been worried about exams. " + base_reply
        elif "alone" in historical_text or "lonely" in historical_text:
            base_reply = "Remember what we talked about earlier — you don't have to face this alone. " + base_reply

    return base_reply
