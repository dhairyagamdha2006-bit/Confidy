import json
import re

def handler(event, context):
    if event.get("httpMethod") != "POST":
        return {"statusCode": 405, "body": "Method Not Allowed"}

    try:
        body = json.loads(event.get("body") or "{}")
        messages = body.get("messages", [])
        scenario = body.get("scenario", "approach")

        user_messages = [
            m["content"] for m in messages
            if m.get("role") == "user" and not m.get("content", "").startswith("[SYSTEM")
        ]

        if not user_messages:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"opening": 15, "flow": 8, "rejection": 5, "mindset": 20, "overall": 12})
            }

        scores = {
            "opening": score_opening_lines(user_messages),
            "flow": score_conversation_flow(user_messages),
            "rejection": score_rejection_resilience(user_messages, scenario),
            "mindset": score_mindset_frame(user_messages),
        }
        scores["overall"] = int(sum(scores.values()) / len(scores))

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps(scores)
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


def score_opening_lines(messages):
    """Score how strong the user's opening messages are."""
    if not messages:
        return 0

    first = messages[0].lower().strip()
    score = 20  # base score

    # Good signals
    if "?" in first:
        score += 20  # asks a question — shows curiosity
    if any(w in first for w in ["you", "your"]):
        score += 15  # other-focused — not self-absorbed
    if len(first.split()) >= 5:
        score += 10  # not too short
    if len(first.split()) <= 25:
        score += 10  # not too long
    if any(w in first for w in ["notice", "noticed", "saw", "love", "like", "interesting"]):
        score += 10  # specific observation — shows attentiveness
    if any(w in first for w in ["hey", "hi", "excuse me", "sorry to"]):
        score += 5   # has a greeting

    # Bad signals
    weak_openers = ["um", "uh", "like", "so i was", "i don't know", "maybe"]
    score -= sum(8 for w in weak_openers if w in first)

    if len(first.split()) < 3:
        score -= 20  # too short — lazy opener
    if first in ["hey", "hi", "hello", "sup", "hey there"]:
        score -= 15  # generic one-word opener

    return max(0, min(100, score))


def score_conversation_flow(messages):
    """Score how well the user keeps conversation alive."""
    if len(messages) < 2:
        return 10  # not enough data yet

    score = 30
    question_count = sum(1 for m in messages if "?" in m)
    total = len(messages)

    # Good question ratio (40-70% of messages have questions)
    ratio = question_count / total
    if 0.3 <= ratio <= 0.7:
        score += 25
    elif ratio < 0.2:
        score -= 10  # not asking enough questions
    elif ratio > 0.8:
        score -= 5   # too many questions feels like interrogation

    # Check for follow-up signals
    follow_up_words = ["tell me more", "what do you", "how did", "why did", "what about", "really?", "interesting"]
    follow_ups = sum(1 for m in messages for w in follow_up_words if w in m.lower())
    score += min(20, follow_ups * 7)

    # Check for self-disclosure (good — builds rapport)
    self_words = ["i also", "me too", "same here", "i love", "i think", "i feel"]
    self_disc = sum(1 for m in messages for w in self_words if w in m.lower())
    score += min(15, self_disc * 5)

    # Penalise very short messages (under 4 words)
    short_msgs = sum(1 for m in messages if len(m.split()) < 4)
    score -= short_msgs * 5

    return max(0, min(100, score))


def score_rejection_resilience(messages, scenario):
    """Score emotional resilience and mindset around rejection."""
    if scenario != "rejection":
        # For non-rejection scenarios, look for confidence language
        score = 40
        confident_phrases = ["i will", "i want to", "let me", "i am", "i can", "definitely", "absolutely"]
        nervous_phrases = ["what if they", "what if i", "scared", "nervous", "afraid", "worried", "what if"]
        all_text = " ".join(messages).lower()
        score += min(30, sum(8 for p in confident_phrases if p in all_text))
        score -= min(30, sum(8 for p in nervous_phrases if p in all_text))
        return max(0, min(100, score))

    # Rejection scenario — look for healthy reframing
    score = 20
    all_text = " ".join(messages).lower()

    growth_words = ["learn", "data", "practice", "next time", "okay", "fine", "move on", "try again", "experience"]
    score += min(40, sum(8 for w in growth_words if w in all_text))

    catastrophe_words = ["ruined", "terrible", "worst", "never", "always", "hate myself", "hopeless", "give up"]
    score -= min(30, sum(10 for w in catastrophe_words if w in all_text))

    # Reward longer responses (more processing = more resilience)
    avg_len = sum(len(m.split()) for m in messages) / max(1, len(messages))
    if avg_len > 15:
        score += 20
    elif avg_len > 8:
        score += 10

    return max(0, min(100, score))


def score_mindset_frame(messages):
    """Score overall confidence mindset and framing."""
    if not messages:
        return 20

    all_text = " ".join(messages).lower()
    score = 30

    # Power words — confident, assertive language
    power_words = ["i want", "i will", "let us", "let's", "i decided", "i chose", "i am going", "absolutely", "definitely", "for sure"]
    score += min(30, sum(6 for w in power_words if w in all_text))

    # Victim/weak frame words
    weak_words = ["i can't", "i could not", "maybe", "kind of", "sort of", "i guess", "i just", "if they let me", "i hope they"]
    score -= min(30, sum(6 for w in weak_words if w in all_text))

    # Filler word penalty
    fillers = [" um ", " uh ", " like ", " literally ", " basically "]
    filler_count = sum(all_text.count(f) for f in fillers)
    score -= min(20, filler_count * 4)

    # Reward specificity — longer, more detailed messages show engagement
    avg_words = sum(len(m.split()) for m in messages) / max(1, len(messages))
    if avg_words >= 12:
        score += 15
    elif avg_words >= 7:
        score += 8

    return max(0, min(100, score))
