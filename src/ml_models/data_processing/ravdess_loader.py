import os
import librosa
import numpy as np

# CONFIG (must match your LSTM model)
SAMPLE_RATE = 22050
N_MFCC = 13
SEQ_LEN = 40


# RAVDESS emotion code mapping
# Filename format: 03-01-XX-...
RAVDESS_EMOTION_MAP = {
    "01": "neutral",
    "02": "neutral",              # calm → neutral
    "03": "happiness",
    "04": "sadness",
    "05": "anger",
    "06": "fear",
    "07": "anger",                # disgust → anger (closest)
    "08": "situational_arousal"   # surprised
}


# Your model emotion order (MUST match emotion_model.py)
MODEL_EMOTIONS = [
    "neutral",
    "happiness",
    "sadness",
    "anger",
    "fear",
    "situational_arousal"
]


def extract_mfcc_sequence(wav_path):
    """
    Extract MFCCs and normalize to fixed SEQ_LEN
    Output shape: (40, 13)
    """
    try:
        audio, _ = librosa.load(wav_path, sr=SAMPLE_RATE)

        mfcc = librosa.feature.mfcc(
            y=audio,
            sr=SAMPLE_RATE,
            n_mfcc=N_MFCC
        ).T  # (time, mfcc)

        # Pad or trim to SEQ_LEN
        if mfcc.shape[0] < SEQ_LEN:
            pad_width = SEQ_LEN - mfcc.shape[0]
            mfcc = np.pad(mfcc, ((0, pad_width), (0, 0)), mode="constant")
        else:
            mfcc = mfcc[:SEQ_LEN]

        return mfcc

    except Exception as e:
        print(f"Error processing {wav_path}: {e}")
        return None


def load_ravdess_data(dataset_path):
    """
    Loads RAVDESS dataset and returns:
    X → (samples, 40, 13)
    y → (samples,)
    """
    X, y = [], []

    for actor in sorted(os.listdir(dataset_path)):
        actor_path = os.path.join(dataset_path, actor)

        if not os.path.isdir(actor_path):
            continue

        for file in os.listdir(actor_path):
            if not file.endswith(".wav"):
                continue

            file_path = os.path.join(actor_path, file)

            # Extract emotion code from filename
            parts = file.split("-")
            if len(parts) < 3:
                continue

            emotion_code = parts[2]

            if emotion_code not in RAVDESS_EMOTION_MAP:
                continue

            emotion_label = RAVDESS_EMOTION_MAP[emotion_code]

            if emotion_label not in MODEL_EMOTIONS:
                continue

            mfcc_seq = extract_mfcc_sequence(file_path)
            if mfcc_seq is None:
                continue

            X.append(mfcc_seq)
            y.append(MODEL_EMOTIONS.index(emotion_label))

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int32)

    print(f"Loaded RAVDESS samples: {X.shape[0]}")
    print(f"Input shape: {X.shape}")
    print(f"Labels shape: {y.shape}")

    return X, y
