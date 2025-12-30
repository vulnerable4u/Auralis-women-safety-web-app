

import os
import numpy as np
import pickle

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
# CONFIG

N_MFCC = 13
SEQ_LEN = 40   # frames per sequence
EMOTIONS = [
    "neutral",
    "happiness",
    "sadness",
    "anger",
    "fear",
    "situational_arousal"
]


# LSTM EMOTION MODEL

class LSTMEmotionModel:

    def __init__(self, model_path="models/emotion_model.keras"):
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.emotions = EMOTIONS
        self.is_trained = False

        self.load_model()


    # SYNTHETIC SEQUENCE DATA (FOR DEMO / BOOTSTRAP)

    def generate_sequence_data(self, samples=1200):
        X, y = [], []

        for idx, emotion in enumerate(self.emotions):
            for _ in range(samples // len(self.emotions)):
                seq = np.random.normal(0, 0.4, (SEQ_LEN, N_MFCC))

                if emotion == "fear":
                    seq[:, :4] += np.linspace(0.3, 1.5, SEQ_LEN).reshape(-1, 1)

                elif emotion == "anger":
                    seq[:, :3] += np.linspace(0.2, 1.2, SEQ_LEN).reshape(-1, 1)

                elif emotion == "sadness":
                    seq[:, :4] -= np.linspace(0.1, 0.6, SEQ_LEN).reshape(-1, 1)

                elif emotion == "happiness":
                    seq[:, :4] += np.linspace(0.1, 0.7, SEQ_LEN).reshape(-1, 1)

                elif emotion == "situational_arousal":
                    seq += np.random.normal(0, 1.0, (SEQ_LEN, N_MFCC))

                X.append(seq)
                y.append(idx)

        return np.array(X), np.array(y)

  
    # MODEL ARCHITECTURE

    def build_model(self):
        model = Sequential([
            LSTM(64, return_sequences=True, input_shape=(SEQ_LEN, N_MFCC)),
            Dropout(0.3),
            LSTM(32),
            Dropout(0.3),
            Dense(32, activation="relu"),
            Dense(len(self.emotions), activation="softmax")
        ])

        model.compile(
            optimizer="adam",
            loss="categorical_crossentropy",
            metrics=["accuracy"]
        )

        self.model = model

 
    # TRAINING

    def train(self, X,y, retrain=False):
        if X is None or y is None:
            raise ValueError("Explicit training data required (real dataset expected).")
        if self.is_trained and not retrain:
            print("LSTM model already trained.")
            return

        print("Training LSTM Emotion Model...")

        if X is None or y is None:
            X, y = self.generate_sequence_data()

        # Normalize MFCCs globally
        X_flat = X.reshape(-1, N_MFCC)
        X_flat = self.scaler.fit_transform(X_flat)
        X = X_flat.reshape(-1, SEQ_LEN, N_MFCC)

        y_cat = to_categorical(y, num_classes=len(self.emotions))

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_cat, test_size=0.2, random_state=42
        )

        self.build_model()

        es = EarlyStopping(
            monitor="val_loss",
            patience=10,
            restore_best_weights=True
        )

        self.model.fit(
            X_train,
            y_train,
            validation_data=(X_test, y_test),
            epochs=40,
            batch_size=32,
            callbacks=[es],
            verbose=1
        )

        self.is_trained = True
        self.save_model()


    # PREDICTION
 
    def predict(self, mfcc_sequence):
        
        """
        mfcc_sequence shape: (SEQ_LEN, 13)
        """
        
        if self.model is None or not self.is_trained:
            return self.safe_fallback()

        mfcc_sequence = np.array(mfcc_sequence, dtype=float)

        if mfcc_sequence.shape != (SEQ_LEN, N_MFCC):
            return self.safe_fallback()

        seq = self.scaler.transform(mfcc_sequence)
        seq = seq.reshape(1, SEQ_LEN, N_MFCC)

        probs = self.model.predict(seq, verbose=0)[0]
        idx = int(np.argmax(probs))
        if float(probs[idx])<0.6:
            return self.safe_fallback()
        emotion=self.emotions[idx]
        if emotion=="situational_arousal":
            emotion="neutral"
        return {
            "emotion": emotions,
            "confidence": float(probs[idx]),
            "probabilities": {
                self.emotions[i]: float(probs[i]) for i in range(len(probs))
            }
        }

    # SAFE FALLBACK

    def safe_fallback(self):
        return {
            "emotion": "neutral",
            "confidence": 0.3,
            "probabilities": {e: 0.0 for e in self.emotions}
        }

    # SAVE / LOAD
   
    def save_model(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)

    # Save TensorFlow model properly
        self.model.save(self.model_path)

    # Save scaler separately
        with open(self.model_path.replace(".keras", "_scaler.pkl"), "wb") as f:
            pickle.dump(self.scaler, f)


    def load_model(self):
        if not os.path.exists(self.model_path):
            return False

        self.model = load_model(self.model_path)

        scaler_path = self.model_path.replace(".keras", "_scaler.pkl")
        if os.path.exists(scaler_path):
            with open(scaler_path, "rb") as f:
                self.scaler = pickle.load(f)

        self.is_trained = True
        return True


# Factory function to get emotion model instance
def get_emotion_model():
    """Factory function to get LSTM emotion model instance."""
    return LSTMEmotionModel()

