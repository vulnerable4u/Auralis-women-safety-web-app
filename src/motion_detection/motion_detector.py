"""
Adaptive Motion Detection Module (FINAL)
Dynamic, fusion-safe motion scoring (0–1)
Optimized for multimodal threat engines
"""

import cv2
import numpy as np
from collections import deque


class MotionDetector:
    """
    Device-agnostic motion detection using adaptive background modeling.
    Designed for web-based deployments (mobile, tablet, laptop cameras).
    """

    def __init__(
        self,
        shadow_removal: bool = True,
        min_area_ratio: float = 0.001,     # LOWERED for human motion
        sensitivity: float = 1.0,
        history: int = 200,
        var_threshold: int = 48,
        learning_rate: float = 0.003,
        smoothing_window: int = 4,         # REDUCED smoothing
    ):
        self.shadow_removal = shadow_removal
        self.min_area_ratio = min_area_ratio
        self.sensitivity = sensitivity
        self.learning_rate = learning_rate

        # Background subtractor
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=history,
            varThreshold=var_threshold,
            detectShadows=shadow_removal,
        )

        # Morphology kernel
        self.open_kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (3, 3)
        )

        # Motion score smoothing
        self.score_history = deque(maxlen=smoothing_window)

        # Warm-up control
        self._warmup_frames = 10            # REDUCED
        self._frame_count = 0
        self._initialized = False

    # ------------------------------------------------------------------

    def detect_motion(self, frame: np.ndarray):
        """
        Detect motion in a video frame.

        Args:
            frame: BGR frame from OpenCV capture

        Returns:
            motion_score (float): Stable value between 0 and 1
            fg_mask (np.ndarray): Clean foreground mask
        """

        if frame is None:
            return 0.03, None  # non-zero baseline

        self._frame_count += 1

        # Background subtraction
        fg_mask = self.background_subtractor.apply(
            frame, learningRate=self.learning_rate
        )

        # Warm-up phase (DO NOT return zero)
        if self._frame_count < self._warmup_frames:
            return 0.05, fg_mask

        self._initialized = True

        # Shadow removal
        if self.shadow_removal:
            fg_mask[fg_mask == 127] = 0

        # Noise reduction
        fg_mask = cv2.medianBlur(fg_mask, 5)
        fg_mask = cv2.morphologyEx(
            fg_mask, cv2.MORPH_OPEN, self.open_kernel
        )

        # Motion area computation
        motion_pixels = cv2.countNonZero(fg_mask)
        frame_area = frame.shape[0] * frame.shape[1]
        motion_ratio = motion_pixels / max(frame_area, 1)

        # Adaptive scoring
        if motion_ratio < self.min_area_ratio:
            raw_score = 0.0
        else:
            raw_score = (motion_ratio / self.min_area_ratio)
            raw_score *= self.sensitivity

            # Micro-motion amplification (critical)
            if 0.0 < raw_score < 0.15:
                raw_score *= 1.5

            raw_score = float(np.clip(raw_score, 0.0, 1.0))

        # Temporal smoothing with non-zero floor
        smoothed_score = self._smooth_score(raw_score)

        return smoothed_score, fg_mask

    # ------------------------------------------------------------------

    def _smooth_score(self, score: float) -> float:
        """
        Moving average smoothing with fusion-safe baseline.
        """
        self.score_history.append(score)
        return float(max(0.03, np.mean(self.score_history)))

    # ------------------------------------------------------------------

    def reset_background(self):
        """
        Reset background model.
        Use when:
        - Camera switches
        - Orientation changes
        - Sudden environment change
        """
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=200,
            varThreshold=48,
            detectShadows=self.shadow_removal,
        )
        self.score_history.clear()
        self._frame_count = 0
        self._initialized = False
