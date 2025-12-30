"""
Real-time Audio Capture Module
Handles microphone input for threat detection system
"""

import numpy as np
import threading
import time
import queue
from collections import deque

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("Warning: pyaudio not available. Using simulated audio input.")


class AudioRecorder:
    """Real-time audio recorder with configurable buffer management"""
    
    def __init__(self, 
                 sample_rate=16000,
                 chunk_size=1024,
                 channels=1,
                 format_width=2,
                 buffer_duration=3.0):
        """
        Initialize audio recorder
        
        Args:
            sample_rate: Audio sample rate (Hz) - 16kHz for MFCC compatibility
            chunk_size: Number of frames per buffer
            channels: Number of audio channels (1 for mono)
            format_width: Bytes per sample (2 for 16-bit)
            buffer_duration: Buffer duration in seconds for processing
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.channels = channels
        self.format_width = format_width
        self.buffer_duration = buffer_duration
        self.buffer_frames = int(buffer_duration * sample_rate / chunk_size)
        
        # Audio stream state
        self.stream = None
        self.audio = None
        self.is_recording = False
        self.recording_thread = None
        
        # Audio buffer for processing
        self.audio_buffer = deque(maxlen=self.buffer_frames)
        self.buffer_lock = threading.Lock()
        
        # Processing queue
        self.processing_queue = queue.Queue(maxsize=10)
        
        # Initialize pyaudio if available
        if PYAUDIO_AVAILABLE:
            try:
                self.audio = pyaudio.PyAudio()
                print(f"AudioRecorder initialized: {sample_rate}Hz, {channels}ch, {chunk_size} frames")
            except Exception as e:
                print(f"Failed to initialize PyAudio: {e}")
                self.audio = None
        else:
            print("Using simulated audio input (pyaudio not available)")
    
    def start_recording(self):
        """Start real-time audio recording"""
        if self.is_recording:
            return True
        
        if not PYAUDIO_AVAILABLE or self.audio is None:
            # Use simulated audio for testing
            self.is_recording = True
            self.recording_thread = threading.Thread(target=self._simulated_recording_loop, daemon=True)
            self.recording_thread.start()
            print("Started simulated audio recording")
            return True
        
        try:
            # Real audio recording
            self.stream = self.audio.open(
                format=self.audio.get_format_from_width(self.format_width),
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.is_recording = True
            self.recording_thread = threading.Thread(target=self._recording_loop, daemon=True)
            self.recording_thread.start()
            
            print("Started real audio recording")
            return True
            
        except Exception as e:
            print(f"Failed to start audio recording: {e}")
            return False
    
    def stop_recording(self):
        """Stop audio recording"""
        self.is_recording = False
        
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
            self.stream = None
        
        if self.audio:
            try:
                self.audio.terminate()
            except:
                pass
            self.audio = None
        
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=1.0)
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback for real-time audio processing"""
        if status:
            print(f"Audio callback status: {status}")
        
        # Convert audio data to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        
        # Normalize to float32 range [-1, 1]
        audio_float = audio_data.astype(np.float32) / 32768.0
        
        with self.buffer_lock:
            self.audio_buffer.append(audio_float)
        
        return (None, pyaudio.paContinue)
    
    def _recording_loop(self):
        """Main recording loop for real audio"""
        print("Real audio recording thread started")
        
        while self.is_recording:
            try:
                # Get latest audio from buffer
                with self.buffer_lock:
                    if len(self.audio_buffer) >= 5:  # At least 5 chunks
                        # Combine recent chunks for processing
                        recent_audio = np.concatenate(list(self.audio_buffer)[-5:])
                
                # Put audio data in processing queue
                if not self.processing_queue.full():
                    self.processing_queue.put(recent_audio.copy(), block=False)
                
                time.sleep(0.01)  # Small delay to prevent busy waiting
                
            except Exception as e:
                print(f"Error in recording loop: {e}")
                time.sleep(0.1)
        
        print("Real audio recording thread stopped")
    
    def _simulated_recording_loop(self):
        """Simulated audio recording for testing when pyaudio unavailable"""
        print("Simulated audio recording thread started")
        
        while self.is_recording:
            try:
                # Generate simulated audio (silent with occasional speech-like patterns)
                t = time.time()
                freq = 440  # A4 note
                amplitude = 0.1
                
                # Add some variation to simulate speech patterns
                if int(t) % 7 < 3:  # 3 seconds of "speech", 4 seconds silence
                    # Simulated speech pattern
                    wave = amplitude * np.sin(2 * np.pi * freq * np.linspace(0, 0.5, self.chunk_size))
                    # Add some noise to make it more realistic
                    wave += 0.02 * np.random.normal(0, 1, self.chunk_size)
                else:
                    # Mostly silence with minimal noise
                    wave = 0.01 * np.random.normal(0, 1, self.chunk_size)
                
                # Add to buffer
                with self.buffer_lock:
                    self.audio_buffer.append(wave)
                
                # Put in processing queue
                if not self.processing_queue.full():
                    self.processing_queue.put(wave.copy(), block=False)
                
                time.sleep(0.01)
                
            except Exception as e:
                print(f"Error in simulated recording loop: {e}")
                time.sleep(0.1)
        
        print("Simulated audio recording thread stopped")
    
    def get_audio_data(self, duration_seconds=1.0):
        """
        Get audio data for specified duration
        
        Args:
            duration_seconds: Duration of audio to retrieve
            
        Returns:
            numpy array of audio samples
        """
        required_frames = int(duration_seconds * self.sample_rate)
        
        with self.buffer_lock:
            # Combine all available audio in buffer
            if len(self.audio_buffer) > 0:
                combined_audio = np.concatenate(list(self.audio_buffer))
            else:
                return np.zeros(required_frames)
        
        # Return the most recent audio, padded or trimmed as needed
        if len(combined_audio) >= required_frames:
            return combined_audio[-required_frames:]
        else:
            # Pad with zeros if not enough audio
            padding = required_frames - len(combined_audio)
            return np.pad(combined_audio, (0, padding), mode='constant')
    
    def get_processing_audio(self):
        """
        Get audio data from processing queue
        
        Returns:
            numpy array of audio samples or None if no data available
        """
        try:
            return self.processing_queue.get_nowait()
        except queue.Empty:
            return None
    
    def is_audio_available(self):
        """Check if audio data is available for processing"""
        return not self.processing_queue.empty()
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.stop_recording()
