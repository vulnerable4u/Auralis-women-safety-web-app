"""
Enhanced Speech Analysis Module
Accurate audio threat detection using MFCC, normalization, and emotion scoring
"""

import numpy as np
import math


class SpeechDetector:
    """High-stability speech threat analysis using MFCC + emotion heuristics"""

    def __init__(self):
        # Threat & safety keywords
        self.keywords_threat = [
            'help', 'stop', 'no', 'danger', 'emergency',
            'scream', 'fear', 'scared', 'afraid', 'threat'
        ]
        self.keywords_safe = [
            'okay', 'fine', 'safe', 'good', 'alright', 'secure'
        ]

        # Emotion → Threat scaling
        self.emotion_weights = {
            'fear': 0.75,
            'anger': 0.65,
            'sadness': 0.45,
            'neutral': 0.10,
            'happiness': 0.05
        }

        # Smoothing buffers
        self.conf_history = []

    ###########################################################################
    #                              MFCC FEATURES
    ###########################################################################

    def extract_mfcc_features(self, signal, sample_rate=16000, n_mfcc=13):
        """Accurate MFCC pipeline with normalization, validation, and noise safety."""

        if signal is None or len(signal) < 200:
            return np.zeros(n_mfcc)

        # Remove DC offset
        signal = signal - np.mean(signal)

        # Pre-emphasis (boost high-frequency detail)
        signal = np.append(signal[0], signal[1:] - 0.97 * signal[:-1])

        # Framing
        frame_len = int(0.025 * sample_rate)
        frame_step = int(0.010 * sample_rate)

        if frame_len >= len(signal):
            return np.zeros(n_mfcc)

        frames = []
        for i in range(0, len(signal) - frame_len, frame_step):
            frame = signal[i:i + frame_len]
            frame *= np.hamming(frame_len)
            frames.append(frame)

        if not frames:
            return np.zeros(n_mfcc)

        frames = np.array(frames)

        # FFT → Power Spectrum
        NFFT = 512
        mag = np.abs(np.fft.rfft(frames, NFFT))
        pow_frames = (1.0 / NFFT) * (mag ** 2)

        # Mel Filterbank
        mel_fb = self._mel_filterbank(sample_rate, NFFT, n_filters=26)
        mel_energy = np.dot(pow_frames, mel_fb.T)
        mel_energy = np.maximum(mel_energy, np.finfo(float).eps)

        log_mel = np.log(mel_energy)

        # Apply DCT-II
        mfcc = self._dct(log_mel)[:, :n_mfcc]

        # Mean pooling to single MFCC vector
        mfcc_mean = np.mean(mfcc, axis=0)

        # Normalize for consistency across mic input levels
        mfcc_norm = (mfcc_mean - np.mean(mfcc_mean)) / (np.std(mfcc_mean) + 1e-10)

        return mfcc_norm

    def _mel_filterbank(self, sample_rate, n_fft, n_filters=26):
        """Mel filterbank generation with bounds-check safety"""

        def hz_to_mel(hz):
            return 2595 * np.log10(1 + hz / 700)

        def mel_to_hz(m):
            return 700 * (10 ** (m / 2595) - 1)

        low_mel = hz_to_mel(0)
        high_mel = hz_to_mel(sample_rate // 2)
        mel_points = np.linspace(low_mel, high_mel, n_filters + 2)
        hz_points = mel_to_hz(mel_points)

        bins = np.floor((n_fft + 1) * hz_points / sample_rate).astype(int)
        bins = np.clip(bins, 0, n_fft // 2)

        fb = np.zeros((n_filters, n_fft // 2 + 1))

        for i in range(1, n_filters + 1):
            left, center, right = bins[i - 1], bins[i], bins[i + 1]

            if center == left:
                continue
            if right == center:
                continue

            fb[i - 1, left:center] = (np.arange(left, center) - left) / (center - left)
            fb[i - 1, center:right] = (right - np.arange(center, right)) / (right - center)

        return fb

    def _dct(self, x):
        """Fast vectorized DCT-II"""
        N = x.shape[1]
        n = np.arange(N)
        k = np.arange(N)
        dct_mat = np.cos(np.pi * (n + 0.5)[:, None] * k / N)
        return x @ dct_mat

    ###########################################################################
    #                           EMOTION ANALYSIS
    ###########################################################################

    def analyze_emotion_from_mfcc(self, mfcc):
        """Emotion estimation using spectral energy and centroid heuristics."""

        if mfcc is None or len(mfcc) == 0:
            return "neutral", 0.2

        energy = np.sum(mfcc ** 2)
        abs_sum = np.sum(np.abs(mfcc)) + 1e-10
        centroid = np.sum(np.abs(mfcc) * np.arange(len(mfcc))) / abs_sum

        # Heuristic rules
        if energy > 2.0 and centroid > 7:
            emotion, raw = "fear", 0.90
        elif energy > 1.5 and centroid > 6:
            emotion, raw = "anger", 0.75
        elif energy < 0.5:
            emotion, raw = "neutral", 0.20
        else:
            emotion, raw = "sadness", 0.35

        # Smooth confidence to prevent jitter
        conf = self._smooth_conf(raw)
        return emotion, conf

    def _smooth_conf(self, conf):
        self.conf_history.append(conf)
        if len(self.conf_history) > 3:
            self.conf_history.pop(0)
        return float(np.mean(self.conf_history))

    ###########################################################################
    #                        THREAT SCORE COMPUTATION
    ###########################################################################

    def analyze_audio(self, audio, sr=16000, use_model=True):
        """Compute threat score from audio (MFCC + emotion model)"""

        if audio is None or len(audio) < 200:
            return 0.1, "neutral", 0.0

        mfcc = self.extract_mfcc_features(audio, sr)

        # Try ML model if available
        if use_model:
            try:
                from src.ml_models.emotion_model import get_emotion_model
                model = get_emotion_model()

                # Convert MFCC vector to LSTM sequence
                mfcc_seq = np.tile(mfcc, (model.SEQ_LEN, 1))
                result = model.predict(mfcc_seq)

                emotion = result["emotion"]
                conf = result["confidence"]

            except Exception:
                # Fallback heuristic (only if LSTM fails)
                emotion, conf = self.analyze_emotion_from_mfcc(mfcc)

        else:
            emotion, conf = self.analyze_emotion_from_mfcc(mfcc)

        base = self.emotion_weights.get(emotion, 0.10)
        conf=max(0.25,conf)
        score = base * conf

        return min(1.0, score), emotion, conf

    ###########################################################################
    #                         KEYWORD DETECTION
    ###########################################################################

    def detect_keywords(self, text):
        """Keyword-based threat scoring with balanced safe/threat detection."""

        if not isinstance(text, str):
            return 0.1

        text = text.lower()

        threats = sum(k in text for k in self.keywords_threat)
        safes = sum(k in text for k in self.keywords_safe)

        if threats > 0:
            return min(1.0, 0.4 + threats * 0.15)

        if safes > 0:
            return max(0.0, 0.1 - safes * 0.03)

        return 0.1  # neutral