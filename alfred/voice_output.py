"""Voice output using Google AI text-to-speech"""

import os
import subprocess
import tempfile
from typing import Optional
from pathlib import Path

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

from .config import API_KEY, AUDIO_CACHE, SPEAKING_RATE


class VoiceOutput:
    """Handles text-to-speech synthesis and audio playback."""

    def __init__(self):
        self._is_speaking = False
        self._current_process: Optional[subprocess.Popen] = None

        if GENAI_AVAILABLE and API_KEY:
            genai.configure(api_key=API_KEY)

    def speak(self, text: str, wait: bool = True) -> bool:
        """
        Convert text to speech and play it.

        Args:
            text: Text to speak
            wait: Wait for audio to finish before returning

        Returns:
            True if successful
        """
        if self._is_speaking:
            print("Already speaking, queuing...")
            self.stop()

        self._is_speaking = True

        try:
            # Try Google TTS first, then fallback
            audio_path = self._synthesize(text)

            if audio_path and audio_path.exists():
                return self._play_audio(audio_path, wait=wait)
            else:
                # Fallback to system TTS
                return self._speak_system(text)

        except Exception as e:
            print(f"Speak error: {e}")
            return self._speak_system(text)
        finally:
            if wait:
                self._is_speaking = False

    def _synthesize(self, text: str) -> Optional[Path]:
        """Synthesize speech using Google AI."""
        try:
            # For now, use system TTS as Google's TTS API
            # requires Cloud TTS, not available in generativeai SDK
            # This is a placeholder for when Gemini Live TTS is available

            # TODO: Integrate with Gemini Live's native TTS when available
            # For now, return None to trigger fallback
            return None

        except Exception as e:
            print(f"Synthesis error: {e}")
            return None

    def _play_audio(self, audio_path: Path, wait: bool = True) -> bool:
        """Play audio file."""
        try:
            # macOS: use afplay
            if os.name == 'posix' and os.uname().sysname == 'Darwin':
                cmd = ['afplay', str(audio_path)]
            # Linux: use aplay or paplay
            elif os.name == 'posix':
                cmd = ['paplay', str(audio_path)]
            # Windows: use start
            else:
                cmd = ['start', '', str(audio_path)]

            if wait:
                result = subprocess.run(cmd, check=True, capture_output=True)
                return result.returncode == 0
            else:
                self._current_process = subprocess.Popen(cmd)
                return True

        except Exception as e:
            print(f"Playback error: {e}")
            return False
        finally:
            # Clean up temp file
            if audio_path.exists() and 'temp' in str(audio_path):
                try:
                    audio_path.unlink()
                except:
                    pass

    def _speak_system(self, text: str) -> bool:
        """Fallback: use system text-to-speech."""
        try:
            # macOS: use say command
            if os.name == 'posix' and os.uname().sysname == 'Darwin':
                # Use a good voice if available
                voices = ['Daniel', 'Alex', 'Tom']  # British-ish voices
                voice = None

                for v in voices:
                    result = subprocess.run(
                        ['say', '-v', '?'],
                        capture_output=True,
                        text=True
                    )
                    if v in result.stdout:
                        voice = v
                        break

                cmd = ['say']
                if voice:
                    cmd.extend(['-v', voice])
                cmd.extend(['-r', str(int(SPEAKING_RATE * 200))])  # Rate
                cmd.append(text)

                print(f"🔊 Speaking: {text[:50]}...")
                result = subprocess.run(cmd, check=True)
                return result.returncode == 0

            # Linux: use espeak
            elif os.name == 'posix':
                cmd = ['espeak', text]
                result = subprocess.run(cmd, check=True)
                return result.returncode == 0

            # Windows: use pyttsx3
            else:
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
                return True

        except Exception as e:
            print(f"System TTS error: {e}")
            return False

    def stop(self):
        """Stop current speech."""
        self._is_speaking = False

        if self._current_process:
            try:
                self._current_process.terminate()
                self._current_process = None
            except:
                pass

        # macOS: kill any afplay
        if os.name == 'posix' and os.uname().sysname == 'Darwin':
            subprocess.run(['pkill', '-9', 'afplay'], capture_output=True)
            subprocess.run(['pkill', '-9', 'say'], capture_output=True)

    @property
    def is_speaking(self) -> bool:
        """Check if currently speaking."""
        return self._is_speaking


# Test function
if __name__ == "__main__":
    print("Testing VoiceOutput...")
    vo = VoiceOutput()

    test_texts = [
        "Hello, I'm Alfred. Your no-bullshit assistant.",
        "Here's the rule: execution beats ideas. Every time.",
    ]

    for text in test_texts:
        print(f"\nSaying: {text}")
        vo.speak(text)
