"""Conversation management and main interaction loop"""

import time
import threading
from enum import Enum
from typing import Optional, Callable
from dataclasses import dataclass

from .voice_input import VoiceInput
from .voice_output import VoiceOutput
from .brain import AlfredBrain


class ConversationState(Enum):
    """States for the conversation state machine."""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"


@dataclass
class ConversationConfig:
    """Configuration for conversation behavior."""
    continuous_mode: bool = False  # Keep listening after response
    listen_timeout: float = 10.0   # Max listen time
    fast_mode: bool = True         # Use fast model
    greeting: str = "Alfred here. What do you need?"


class Conversation:
    """
    Manages the conversation loop between user and Alfred.

    Handles state transitions:
    IDLE -> LISTENING -> PROCESSING -> SPEAKING -> IDLE (or back to LISTENING)
    """

    def __init__(self, config: Optional[ConversationConfig] = None):
        self.config = config or ConversationConfig()

        # Components
        self.voice_input = VoiceInput()
        self.voice_output = VoiceOutput()
        self.brain = AlfredBrain(fast_mode=self.config.fast_mode)

        # State
        self._state = ConversationState.IDLE
        self._running = False
        self._thread: Optional[threading.Thread] = None

        # Callbacks
        self.on_state_change: Optional[Callable[[ConversationState], None]] = None
        self.on_transcript: Optional[Callable[[str], None]] = None
        self.on_response: Optional[Callable[[str], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None

    @property
    def state(self) -> ConversationState:
        return self._state

    def _set_state(self, new_state: ConversationState):
        """Update state and notify listeners."""
        old_state = self._state
        self._state = new_state
        print(f"State: {old_state.value} -> {new_state.value}")

        if self.on_state_change:
            self.on_state_change(new_state)

    def start(self):
        """Start the conversation loop in a background thread."""
        if self._running:
            print("Conversation already running")
            return

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        print("🎩 Alfred conversation started")

    def stop(self):
        """Stop the conversation loop."""
        self._running = False
        self.voice_input.stop()
        self.voice_output.stop()
        self._set_state(ConversationState.IDLE)
        print("🛑 Conversation stopped")

    def _run_loop(self):
        """Main conversation loop."""
        # Initial greeting
        if self.config.greeting:
            self._speak(self.config.greeting)

        while self._running:
            try:
                # Listen for input
                self._set_state(ConversationState.LISTENING)
                user_text = self.voice_input.listen(timeout=self.config.listen_timeout)

                if not user_text:
                    if not self.config.continuous_mode:
                        self._set_state(ConversationState.IDLE)
                        break
                    continue

                # Notify transcript
                if self.on_transcript:
                    self.on_transcript(user_text)

                # Check for exit commands
                if self._is_exit_command(user_text):
                    self._speak("Later.")
                    break

                # Process with brain
                self._set_state(ConversationState.PROCESSING)
                response = self.brain.think(user_text)

                # Notify response
                if self.on_response:
                    self.on_response(response)

                # Speak response
                self._speak(response)

                # Continue or stop
                if not self.config.continuous_mode:
                    self._set_state(ConversationState.IDLE)
                    break

            except Exception as e:
                print(f"Conversation error: {e}")
                self._set_state(ConversationState.ERROR)

                if self.on_error:
                    self.on_error(str(e))

                # Try to recover
                time.sleep(1)
                self._set_state(ConversationState.IDLE)

                if not self.config.continuous_mode:
                    break

        self._running = False
        self._set_state(ConversationState.IDLE)

    def _speak(self, text: str):
        """Speak text and update state."""
        self._set_state(ConversationState.SPEAKING)
        self.voice_output.speak(text, wait=True)

    def _is_exit_command(self, text: str) -> bool:
        """Check if user wants to exit."""
        exit_phrases = [
            "goodbye", "bye", "exit", "quit", "stop",
            "that's all", "thanks alfred", "thank you alfred",
            "i'm done", "we're done"
        ]
        text_lower = text.lower().strip()
        return any(phrase in text_lower for phrase in exit_phrases)

    def single_interaction(self) -> Optional[str]:
        """
        Run a single listen -> process -> speak cycle.
        Returns the response text.
        """
        try:
            # Listen
            self._set_state(ConversationState.LISTENING)
            user_text = self.voice_input.listen(timeout=self.config.listen_timeout)

            if not user_text:
                self._set_state(ConversationState.IDLE)
                return None

            if self.on_transcript:
                self.on_transcript(user_text)

            # Process
            self._set_state(ConversationState.PROCESSING)
            response = self.brain.think(user_text)

            if self.on_response:
                self.on_response(response)

            # Speak
            self._speak(response)

            self._set_state(ConversationState.IDLE)
            return response

        except Exception as e:
            print(f"Interaction error: {e}")
            self._set_state(ConversationState.ERROR)
            return None

    def text_interaction(self, user_text: str) -> str:
        """
        Process text input directly (no voice).
        Useful for testing or text-only mode.
        """
        self._set_state(ConversationState.PROCESSING)
        response = self.brain.think(user_text)
        self._set_state(ConversationState.IDLE)
        return response


# Test function
if __name__ == "__main__":
    print("Testing Conversation...")

    config = ConversationConfig(
        continuous_mode=False,
        fast_mode=True,
        greeting="Alfred here. What can I help you with?"
    )

    convo = Conversation(config)

    # Test text interaction
    print("\n--- Text Mode Test ---")
    response = convo.text_interaction("What's the most important thing for a startup?")
    print(f"Response: {response}")

    # Test voice interaction
    print("\n--- Voice Mode Test ---")
    print("Speak when you hear Alfred...")
    response = convo.single_interaction()
    if response:
        print(f"Got response: {response[:100]}...")
