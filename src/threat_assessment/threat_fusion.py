

import time
import math
from src.context_engine.context_engine import ContextEngine


# GLOBAL STATE (persistent across calls)


current_threat_score = 0.0
current_threat_state = "SAFE"

_latch_active = False
_latch_expires_at = 0.0

# ------------------ NEW (SAFE, STATEFUL) -----------------
_context_engine = ContextEngine()



# TUNABLE PARAMETERS


# Temporal behavior
ALPHA_BASE = 0.92
ALPHA_LATCH = 0.995
GAMMA = 1.5

# Attention sharpness
BETA = 4.0

# Emergency latch
LATCH_THREAT_LEVEL = 0.70
LATCH_DURATION = 10.0

# Thresholds
THRESH_SPEECH_SCORE = 0.35
THRESH_CONFIDENCE = 0.70
THRESH_KEYWORD = 0.25



# UTILITY


def _clip(x, lo, hi):
    return max(lo, min(x, hi))



# MAIN FUSION FUNCTION


def fuse_threat_signals(
    speech_score,
    motion_score,
    speech_confidence,
    emotion,
    keyword_score=0.0,
    motion_quality=0.6,
    asr_confidence=0.5,

    # -------- NEW (OPTIONAL, NON-BREAKING) --------
    frame=None,
    motion_blob_count=0,
    near_police=False,
    near_hospital=False,
    public_place=True
    # ---------------------------------------------
):
    """
    Combines speech, motion, keyword, and contextual signals
    into a unified threat score.
    """

    global current_threat_score, current_threat_state
    global _latch_active, _latch_expires_at

    now = time.time()

    # -----------------------------------------------------
    # 1. RELIABILITY ESTIMATION
    # -----------------------------------------------------
    r_speech = _clip(0.25 + 0.75 * speech_confidence, 0.30, 0.99)
    r_motion = _clip(0.30 + 0.70 * motion_quality, 0.20, 0.99)
    r_keyword = _clip(0.30 + 0.70 * asr_confidence, 0.25, 0.95)

    # -----------------------------------------------------
    # 2. ATTENTION WEIGHTS (SOFTMAX)
    # -----------------------------------------------------
    w_s = math.exp(BETA * r_speech)
    w_m = math.exp(BETA * r_motion)
    w_k = math.exp(BETA * r_keyword)

    w_sum = w_s + w_m + w_k + 1e-9
    w_s, w_m, w_k = w_s / w_sum, w_m / w_sum, w_k / w_sum

    # -----------------------------------------------------
    # 3. BEHAVIORAL FUSION
    # -----------------------------------------------------
    b_s = speech_score * r_speech
    b_m = motion_score * r_motion
    b_k = keyword_score * r_keyword

    fused_raw = (w_s * b_s) + (w_m * b_m) + (w_k * b_k)
    fused_norm = (w_s * r_speech) + (w_m * r_motion) + (w_k * r_keyword) + 1e-9
    fused_score = _clip(fused_raw / fused_norm, 0.0, 1.0)

    # ================== NEW CONTEXT MODULATION ==================
    context_score = _context_engine.compute_context_score(
        frame=frame,
        motion_blob_count=motion_blob_count,
        motion_intensity=motion_score,
        near_police=near_police,
        near_hospital=near_hospital,
        public_place=public_place
    )

    # Context modulates but NEVER overrides behavior
    fused_score = _clip(
        0.70 * fused_score + 0.30 * context_score,
        0.0,
        1.0
    )
    

    # -----------------------------------------------------
    # 4. SPEECH-PRIORITY EMERGENCY LATCH (UNCHANGED)
    # -----------------------------------------------------
    if not _latch_active:
        if (
            emotion == "fear"
            and speech_confidence >= THRESH_CONFIDENCE
            and speech_score >= THRESH_SPEECH_SCORE
            and keyword_score >= THRESH_KEYWORD
        ):
            _latch_active = True
            _latch_expires_at = now + LATCH_DURATION
            current_threat_score = max(
                current_threat_score, LATCH_THREAT_LEVEL
            )

    if _latch_active and now >= _latch_expires_at:
        _latch_active = False

    # -----------------------------------------------------
    # 5. ADAPTIVE TEMPORAL SMOOTHING (UNCHANGED)
    # -----------------------------------------------------
    if _latch_active:
        alpha_eff = ALPHA_LATCH
    else:
        alpha_eff = 1.0 - (1.0 - ALPHA_BASE) * (1.0 + GAMMA * fused_score)
        alpha_eff = _clip(alpha_eff, 0.85, 0.99)

    current_threat_score = (
        alpha_eff * current_threat_score
        + (1.0 - alpha_eff) * fused_score
    )

    if _latch_active:
        current_threat_score = max(
            current_threat_score, LATCH_THREAT_LEVEL
        )

    current_threat_score = _clip(current_threat_score, 0.0, 1.0)

    # -----------------------------------------------------
    # 6. STATE UPDATE (UNCHANGED)
    # -----------------------------------------------------
    current_threat_state = get_threat_state(current_threat_score)

    return current_threat_score, current_threat_state



# STATE MAPPING (UNCHANGED)


def get_threat_state(score):
    if score >= 0.85:
        return "CRITICAL"
    elif score >= 0.60:
        return "HIGH"
    elif score >= 0.25:
        return "MEDIUM"
    else:
        return "SAFE"
