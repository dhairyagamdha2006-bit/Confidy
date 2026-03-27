from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import AnalyzeMessageRequest, ScoreSessionRequest, SessionSummaryRequest
from app.nlp_engine import score_latest_message, score_session, build_session_summary


app = FastAPI(title="Confidy NLP API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "service": "confidy-nlp", "docs": "/docs"}


@app.post("/analyze-message")
def analyze_message(payload: AnalyzeMessageRequest):
    result = score_latest_message(
        latest_message=payload.latest_message,
        conversation=[m.model_dump() for m in payload.conversation],
        scenario=payload.scenario,
    )
    return {
        "opening": result.opening,
        "flow": result.flow,
        "rejection": result.rejection,
        "mindset": result.mindset,
        "overall": result.overall,
        "badge": result.badge,
        "reasons": result.reasons,
        "rewrite_suggestion": result.rewrite_suggestion,
        "emotional_tone": result.emotional_tone,
        "confidence_signals": result.confidence_signals,
    }


@app.post("/score-session")
def score_session_endpoint(payload: ScoreSessionRequest):
    result = score_session(
        messages=[m.model_dump() for m in payload.messages],
        scenario=payload.scenario,
    )
    return {
        "opening": result.opening,
        "flow": result.flow,
        "rejection": result.rejection,
        "mindset": result.mindset,
        "overall": result.overall,
        "badge": result.badge,
        "reasons": result.reasons,
        "rewrite_suggestion": result.rewrite_suggestion,
        "emotional_tone": result.emotional_tone,
        "confidence_signals": result.confidence_signals,
    }


@app.post("/session-summary")
def session_summary(payload: SessionSummaryRequest):
    return build_session_summary(
        messages=[m.model_dump() for m in payload.messages],
        scenario=payload.scenario,
    )
