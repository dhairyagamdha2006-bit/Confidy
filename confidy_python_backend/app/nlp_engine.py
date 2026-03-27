from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple
import math
import re

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_embedder = SentenceTransformer(MODEL_NAME)
_sentiment = SentimentIntensityAnalyzer()


HEDGE_PATTERNS = [
    r"\bmaybe\b",
    r"\bkind of\b",
    r"\bsort of\b",
    r"\bi guess\b",
    r"\bjust\b",
    r"\bprobably\b",
    r"\bnot sure\b",
    r"\bif you want\b",
    r"\bsorry\b",
    r"\bi hope\b",
    r"\bi think maybe\b",
]

POWER_PATTERNS = [
    r"\bi want\b",
    r"\bi will\b",
    r"\blet'?s\b",
    r"\blet me\b",
    r"\bdefinitely\b",
    r"\babsolutely\b",
    r"\bfor sure\b",
    r"\bi'm going to\b",
    r"\bwant to grab\b",
    r"\bwant to join\b",
]

FOLLOW_UP_PATTERNS = [
    r"\bwhat about you\b",
    r"\bhow about you\b",
    r"\btell me more\b",
    r"\bhow did you\b",
    r"\bwhat got you into\b",
    r"\bwhat do you like about\b",
    r"\bhow long have you\b",
    r"\bwhat made you\b",
]

GROWTH_PATTERNS = [
    r"\blearn\b",
    r"\bpractice\b",
    r"\bnext time\b",
    r"\btry again\b",
    r"\bmove on\b",
    r"\bit's okay\b",
    r"\bexperience\b",
    r"\bdata\b",
]

CATASTROPHE_PATTERNS = [
    r"\bhopeless\b",
    r"\bworst\b",
    r"\bnever\b",
    r"\balways\b",
    r"\bgive up\b",
    r"\bterrible\b",
    r"\bruined\b",
    r"\bhate myself\b",
]

STRONG_OPENERS = [
    "You seem interesting. What got you into that?",
    "That book looks good. What are you reading?",
    "You seem like you have great taste in music. What are you listening to lately?",
    "You have a calm vibe. Are you always this relaxed?",
    "That looked fun. How did you get into it?",
    "You seem fun to talk to. Want to grab coffee sometime?",
    "I noticed your energy from across the room. What are you celebrating tonight?",
]

WEAK_OPENERS = [
    "hey",
    "hi",
    "sup",
    "um hi maybe",
    "sorry to bother you",
    "i do not know what to say",
    "hello there",
]

STRONG_REWRITES = [
    "You seem interesting. What got you into that?",
    "I noticed your energy. What are you up to today?",
    "You have a good vibe. Are you always this easy to talk to?",
    "That caught my attention. How did you get into it?",
    "You seem fun. Want to keep talking over coffee sometime?",
]


@dataclass
class AnalyzeResult:
    opening: int
    flow: int
    rejection: int
    mindset: int
    overall: int
    badge: str
    reasons: Dict[str, List[str]]
    rewrite_suggestion: str
    emotional_tone: Dict[str, float]
    confidence_signals: Dict[str, int]



def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())



def _filter_user_messages(messages: List[Dict]) -> List[str]:
    out: List[str] = []
    for m in messages:
        role = str(m.get("role", "")).lower()
        content = _normalize_text(str(m.get("content", "")))
        if role == "user" and content and not content.startswith("[SYSTEM"):
            out.append(content)
    return out



def _count_patterns(text: str, patterns: List[str]) -> int:
    lowered = text.lower()
    return sum(1 for p in patterns if re.search(p, lowered))



def _semantic_similarity(text: str, examples: List[str]) -> float:
    if not text.strip():
        return 0.0
    vectors = _embedder.encode([text] + examples)
    query = vectors[0:1]
    refs = vectors[1:]
    sims = cosine_similarity(query, refs)[0]
    return float(max(sims)) if len(sims) else 0.0



def _emotion_profile(text: str) -> Dict[str, float]:
    s = _sentiment.polarity_scores(text)
    lowered = text.lower()
    anxiety = min(1.0, (_count_patterns(lowered, [r"\bnervous\b", r"\bafraid\b", r"\bworried\b", r"\bscared\b", r"\bwhat if\b"]) * 0.22) + max(0.0, 0.25 - s["compound"] * 0.1))
    confidence = min(1.0, (_count_patterns(lowered, POWER_PATTERNS) * 0.18) + max(0.0, s["compound"] * 0.6))
    warmth = min(1.0, (_count_patterns(lowered, [r"\blove\b", r"\bfun\b", r"\binteresting\b", r"\bgood\b", r"\bgreat\b"]) * 0.12) + max(0.0, s["pos"] * 0.8))
    negativity = min(1.0, max(0.0, s["neg"] * 1.2))
    return {
        "confidence": round(confidence, 3),
        "warmth": round(warmth, 3),
        "anxiety": round(anxiety, 3),
        "negativity": round(negativity, 3),
    }



def _clamp(value: float, low: int = 0, high: int = 100) -> int:
    return int(max(low, min(high, round(value))))



def _badge_from_score(score: int) -> str:
    if score >= 70:
        return f"🟢 Strong ({score}/100)"
    if score >= 45:
        return f"🟡 Mixed ({score}/100)"
    return f"🔴 Needs Work ({score}/100)"



def score_latest_message(latest_message: str, conversation: List[Dict], scenario: str) -> AnalyzeResult:
    latest = _normalize_text(latest_message)
    user_messages = _filter_user_messages(conversation) + ([latest] if latest else [])
    return _score_core(user_messages, scenario=scenario, latest_message=latest)



def score_session(messages: List[Dict], scenario: str) -> AnalyzeResult:
    user_messages = _filter_user_messages(messages)
    latest = user_messages[-1] if user_messages else ""
    return _score_core(user_messages, scenario=scenario, latest_message=latest)



def _score_core(user_messages: List[str], scenario: str, latest_message: str) -> AnalyzeResult:
    if not user_messages:
        empty = {"opening": ["No user message yet."], "flow": ["Need more conversation."], "rejection": ["Need more data."], "mindset": ["Need more language data."]}
        return AnalyzeResult(15, 8, 5, 20, 12, _badge_from_score(12), empty, "Try a more specific, curious opener.", _emotion_profile(""), {"hedges": 0, "power_phrases": 0})

    latest_lower = latest_message.lower()
    joined = " ".join(user_messages).lower()
    first = user_messages[0].lower()

    strong_sem = _semantic_similarity(latest_message or user_messages[-1], STRONG_OPENERS)
    weak_sem = _semantic_similarity(latest_message or user_messages[-1], WEAK_OPENERS)

    opening = 35 + strong_sem * 35 - weak_sem * 18
    opening_reasons: List[str] = []
    if "?" in (latest_message or user_messages[0]):
        opening += 10
        opening_reasons.append("Your opener shows curiosity with a question.")
    if len((latest_message or user_messages[0]).split()) >= 5:
        opening += 8
        opening_reasons.append("It has enough detail to feel intentional, not lazy.")
    if _count_patterns(latest_lower or first, HEDGE_PATTERNS) > 0:
        opening -= 12
        opening_reasons.append("Hesitant wording weakens the first impression.")
    if strong_sem >= 0.55:
        opening_reasons.append("Semantically, it resembles stronger social openers.")
    elif weak_sem >= 0.55:
        opening_reasons.append("It is too close to generic openers like 'hey' or 'hi'.")
    if not opening_reasons:
        opening_reasons.append("It is serviceable, but it could be more specific and direct.")
    opening = _clamp(opening)

    question_count = sum(1 for m in user_messages if "?" in m)
    ratio = question_count / max(1, len(user_messages))
    follow_ups = _count_patterns(joined, FOLLOW_UP_PATTERNS)
    avg_len = sum(len(m.split()) for m in user_messages) / max(1, len(user_messages))
    flow = 30
    flow_reasons: List[str] = []
    if 0.25 <= ratio <= 0.75:
        flow += 18
        flow_reasons.append("Your question balance feels conversational rather than one-sided.")
    elif ratio < 0.2:
        flow -= 10
        flow_reasons.append("You need more curiosity and follow-up questions.")
    else:
        flow -= 4
        flow_reasons.append("Too many questions can feel interrogative.")
    flow += min(18, follow_ups * 7)
    if follow_ups:
        flow_reasons.append("You used follow-up style language that keeps momentum alive.")
    if avg_len >= 10:
        flow += 10
        flow_reasons.append("Your replies are developed enough to move the interaction forward.")
    elif avg_len < 4:
        flow -= 12
        flow_reasons.append("Very short messages make the flow feel flat.")
    flow = _clamp(flow)
    if not flow_reasons:
        flow_reasons.append("Flow is acceptable, but you can create more back-and-forth momentum.")

    hedges = _count_patterns(joined, HEDGE_PATTERNS)
    powers = _count_patterns(joined, POWER_PATTERNS)
    emotion = _emotion_profile(joined)
    mindset = 42 + powers * 8 - hedges * 7 + emotion["confidence"] * 18 - emotion["anxiety"] * 14
    mindset_reasons: List[str] = []
    if hedges:
        mindset_reasons.append("Hedging words like 'maybe' or 'I guess' make you sound less certain.")
    if powers:
        mindset_reasons.append("You use assertive phrases that signal confidence and intent.")
    if emotion["anxiety"] > 0.45:
        mindset_reasons.append("The emotional framing still sounds a bit tense or approval-seeking.")
    if emotion["confidence"] > 0.45:
        mindset_reasons.append("Your wording carries a stronger, more grounded frame.")
    if not mindset_reasons:
        mindset_reasons.append("Your mindset language is neutral; stronger intent words would help.")
    mindset = _clamp(mindset)

    rejection = 45
    rejection_reasons: List[str] = []
    if scenario == "rejection":
        growth_hits = _count_patterns(joined, GROWTH_PATTERNS)
        catastrophe_hits = _count_patterns(joined, CATASTROPHE_PATTERNS)
        rejection += growth_hits * 10
        rejection -= catastrophe_hits * 12
        if growth_hits:
            rejection_reasons.append("You frame setbacks as learning, which shows resilience.")
        if catastrophe_hits:
            rejection_reasons.append("Catastrophic language suggests the rejection feels too personal.")
    else:
        if emotion["anxiety"] < 0.35:
            rejection += 8
            rejection_reasons.append("Your tone suggests you can tolerate uncertainty reasonably well.")
        else:
            rejection -= 8
            rejection_reasons.append("Your wording shows outcome-anxiety that could hurt resilience.")
    if not rejection_reasons:
        rejection_reasons.append("Resilience looks average; stronger reframing would improve this skill.")
    rejection = _clamp(rejection)

    overall = _clamp((opening * 0.3) + (flow * 0.25) + (mindset * 0.25) + (rejection * 0.2))
    badge = _badge_from_score(overall)

    rewrite = suggest_rewrite(latest_message or user_messages[-1], scenario, opening, mindset)

    return AnalyzeResult(
        opening=opening,
        flow=flow,
        rejection=rejection,
        mindset=mindset,
        overall=overall,
        badge=badge,
        reasons={
            "opening": opening_reasons,
            "flow": flow_reasons,
            "rejection": rejection_reasons,
            "mindset": mindset_reasons,
        },
        rewrite_suggestion=rewrite,
        emotional_tone=emotion,
        confidence_signals={"hedges": hedges, "power_phrases": powers},
    )



def suggest_rewrite(message: str, scenario: str, opening_score: int, mindset_score: int) -> str:
    text = _normalize_text(message)
    if not text:
        return STRONG_REWRITES[0]

    strong_sem = _semantic_similarity(text, STRONG_REWRITES)
    if opening_score >= 75 and mindset_score >= 70 and strong_sem >= 0.58:
        return text

    if scenario == "texting":
        return "You seem easy to talk to. What are you usually up to when you're not texting people like me?"
    if scenario == "rejection":
        return "That one did not land, but I can learn from it and make my next move cleaner."
    if opening_score < 45:
        return "You seem interesting. What got you into that?"
    if mindset_score < 45:
        return "You seem fun to talk to. Want to keep this going over coffee sometime?"
    return "That caught my attention. How did you get into it?"



def build_session_summary(messages: List[Dict], scenario: str) -> Dict:
    analysis = score_session(messages, scenario)
    strengths: List[str] = []
    weaknesses: List[str] = []

    if analysis.opening >= 65:
        strengths.append("Your opener is specific enough to create real interest.")
    else:
        weaknesses.append("Your opening still needs more specificity and directness.")

    if analysis.flow >= 60:
        strengths.append("You create decent conversational momentum with your replies.")
    else:
        weaknesses.append("You need stronger follow-up questions to keep the exchange moving.")

    if analysis.mindset >= 60:
        strengths.append("Your wording sounds more grounded and self-assured.")
    else:
        weaknesses.append("Hedging language is weakening your confidence frame.")

    if analysis.rejection >= 60:
        strengths.append("Your language shows healthy resilience around uncertain outcomes.")
    else:
        weaknesses.append("Your emotional framing still sounds too outcome-dependent.")

    next_drill = "Practice three direct openers and remove one hedge phrase from each."
    if analysis.flow < analysis.opening:
        next_drill = "Ask one follow-up question after every answer in your next session."
    elif analysis.mindset < 50:
        next_drill = "Rewrite your last two messages without 'maybe', 'just', or 'I guess'."

    return {
        "scores": {
            "opening": analysis.opening,
            "flow": analysis.flow,
            "rejection": analysis.rejection,
            "mindset": analysis.mindset,
            "overall": analysis.overall,
        },
        "badge": analysis.badge,
        "strengths": strengths[:3],
        "weaknesses": weaknesses[:3],
        "rewrite_suggestion": analysis.rewrite_suggestion,
        "next_drill": next_drill,
        "reasons": analysis.reasons,
        "emotional_tone": analysis.emotional_tone,
        "confidence_signals": analysis.confidence_signals,
    }
