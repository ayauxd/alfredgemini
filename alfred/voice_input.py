"""Voice input handling using Google AI speech recognition"""

import io
import wave
import queue
import threading
import numpy as np
import sounddevice as sd
from typing import Optional, Callable

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("Warning: google-generativeai not installed. Voice transcription limited.")

from .config import (
    API_KEY,
    SAMPLE_RATE,
    CHANNELS,
    CHUNK_SIZE,
    SILENCE_THRESHOLD,
    SILENCE_DURATION,
    AUDIO_CACHE
)


class VoiceInput:
    """Handles microphone capture and speech-to-text transcription."""

    def __init__(self):
        self.sample_rate = SAMPLE_RATE
        self.channels = CHANNELS
        self.chunk_size = CHUNK_SIZE
        self.silence_threshold = SILENCE_THRESHOLD
        self.silence_duration = SILENCE_DURATION

        self._audio_queue = queue.Queue()
        self._is_listening = False
        self._stream = None

        # Configure Gemini if available
        if GENAI_AVAILABLE and API_KEY:
            genai.configure(api_key=API_KEY)

    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio stream."""
        if status:
            print(f"Audio status: {status}")
        self._audio_queue.put(indata.copy())

    def _get_audio_level(self, audio_data: np.ndarray) -> float:
        """Calculate RMS level of audio."""
        return np.sqrt(np.mean(audio_data ** 2)) * 32768

    def listen(self,
               timeout: float = 10.0,
               on_start: Optional[Callable] = None,
               on_stop: Optional[Callable] = None) -> Optional[str]:
        """
        Listen for speech and return transcribed text.

        Args:
            timeout: Maximum listen time in seconds
            on_start: Callback when listening starts
            on_stop: Callback when listening stops

        Returns:
            Transcribed text or None if failed
        """
        if self._is_listening:
            print("Already listening")
            return None

        self._is_listening = True
        audio_chunks = []
        silence_chunks = 0
        has_speech = False

        try:
            if on_start:
                on_start()

            print("🎤 Listening...")

            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='int16',
                blocksize=self.chunk_size,
                callback=self._audio_callback
            ):
                chunks_per_second = self.sample_rate / self.chunk_size
                max_chunks = int(timeout * chunks_per_second)
                silence_chunks_needed = int(self.silence_duration * chunks_per_second)

                for _ in range(max_chunks):
                    if not self._is_listening:
                        break

                    try:
                        chunk = self._audio_queue.get(timeout=0.1)
                        audio_chunks.append(chunk)

                        level = self._get_audio_level(chunk)

                        if level > self.silence_threshold:
                            has_speech = True
                            silence_chunks = 0
                        else:
                            silence_chunks += 1

                        # Stop after silence if we had speech
                        if has_speech and silence_chunks >= silence_chunks_needed:
                            print("🔇 Silence detected, processing...")
                            break

                    except queue.Empty:
                        continue

            if on_stop:
                on_stop()

            if not audio_chunks or not has_speech:
                print("No speech detected")
                return None

            # Combine audio chunks
            audio_data = np.concatenate(audio_chunks)

            # Transcribe
            return self._transcribe(audio_data)

        except Exception as e:
            print(f"Listen error: {e}")
            return None
        finally:
            self._is_listening = False
            # Clear queue
            while not self._audio_queue.empty():
                try:
                    self._audio_queue.get_nowait()
                except queue.Empty:
                    break

    def _transcribe(self, audio_data: np.ndarray) -> Optional[str]:
        """Transcribe audio data to text using Gemini."""

        # Save to temporary WAV file
        audio_path = AUDIO_CACHE / "temp_input.wav"

        try:
            with wave.open(str(audio_path), 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data.tobytes())

            if GENAI_AVAILABLE and API_KEY:
                return self._transcribe_with_gemini(audio_path)
            else:
                # Fallback: try Google Speech Recognition via speech_recognition
                return self._transcribe_fallback(audio_path)

        except Exception as e:
            print(f"Transcription error: {e}")
            return None

    def _transcribe_with_gemini(self, audio_path) -> Optional[str]:
        """Use Gemini's audio understanding for transcription."""
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')

            # Upload audio file
            audio_file = genai.upload_file(str(audio_path))

            # Transcribe
            response = model.generate_content([
                "Transcribe this audio exactly as spoken. Output only the transcription, nothing else.",
                audio_file
            ])

            text = response.text.strip()
            print(f"📝 Transcribed: {text}")
            return text

        except Exception as e:
            print(f"Gemini transcription error: {e}")
            return self._transcribe_fallback(audio_path)

    def _transcribe_fallback(self, audio_path) -> Optional[str]:
        """Fallback transcription using speech_recognition library."""
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()

            with sr.AudioFile(str(audio_path)) as source:
                audio = recognizer.record(source)

            text = recognizer.recognize_google(audio)
            print(f"📝 Transcribed (fallback): {text}")
            return text

        except ImportError:
            print("speech_recognition not installed for fallback")
            return None
        except Exception as e:
            print(f"Fallback transcription error: {e}")
            return None

    def stop(self):
        """Stop listening."""
        self._is_listening = False


# Test function
if __name__ == "__main__":
    print("Testing VoiceInput...")
    vi = VoiceInput()
    text = vi.listen(timeout=5.0)
    if text:
        print(f"Got: {text}")
    else:
        print("No text captured")
