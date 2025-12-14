"""Alfred's AI brain powered by Google Gemini"""

from typing import Optional, List, Dict
import google.generativeai as genai

from .config import API_KEY, GEMINI_PRO_MODEL, GEMINI_FLASH_MODEL, DEFAULT_MODEL
from .personality import ALFRED_SYSTEM_PROMPT, ALFRED_FAST_PROMPT, ALFRED_CONTEXT_PROMPT


class AlfredBrain:
    """Handles AI reasoning and response generation using Gemini."""

    def __init__(self, fast_mode: bool = True):
        """
        Initialize Alfred's brain.

        Args:
            fast_mode: Use Flash model for faster responses (default True)
        """
        if not API_KEY:
            raise ValueError("No API key found. Set GOOGLE_API_KEY in .env")

        genai.configure(api_key=API_KEY)

        self.fast_mode = fast_mode
        self.model_name = GEMINI_FLASH_MODEL if fast_mode else GEMINI_PRO_MODEL

        # Initialize model with Alfred's personality
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=ALFRED_SYSTEM_PROMPT if not fast_mode else ALFRED_FAST_PROMPT
        )

        # For multi-turn conversations
        self.chat = None
        self._history: List[Dict] = []

    def think(self,
              user_input: str,
              use_history: bool = True,
              fast: Optional[bool] = None) -> str:
        """
        Process user input and generate Alfred's response.

        Args:
            user_input: What the user said
            use_history: Include conversation history for context
            fast: Override fast_mode for this call

        Returns:
            Alfred's response text
        """
        try:
            # Determine which model to use
            if fast is not None:
                model_name = GEMINI_FLASH_MODEL if fast else GEMINI_PRO_MODEL
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=ALFRED_FAST_PROMPT if fast else ALFRED_SYSTEM_PROMPT
                )
            else:
                model = self.model

            if use_history and self._history:
                # Use chat for multi-turn
                if self.chat is None:
                    self.chat = model.start_chat(history=self._format_history())

                response = self.chat.send_message(user_input)
            else:
                # Single turn
                response = model.generate_content(user_input)

            # Extract text
            result = response.text.strip()

            # Update history
            self._history.append({"role": "user", "content": user_input})
            self._history.append({"role": "assistant", "content": result})

            # Trim history if too long
            if len(self._history) > 40:  # Keep last 20 exchanges
                self._history = self._history[-40:]

            return result

        except Exception as e:
            print(f"Brain error: {e}")
            return "I hit a snag processing that. Try again?"

    def think_with_context(self,
                           user_input: str,
                           context: str) -> str:
        """
        Think with additional context (e.g., user profile).

        Args:
            user_input: What the user said
            context: Additional context to include

        Returns:
            Alfred's response
        """
        augmented_input = f"""Context about the user:
{context}

User's message:
{user_input}"""

        return self.think(augmented_input, use_history=False)

    def _format_history(self) -> List[Dict]:
        """Format history for Gemini chat."""
        formatted = []
        for msg in self._history:
            role = "user" if msg["role"] == "user" else "model"
            formatted.append({
                "role": role,
                "parts": [msg["content"]]
            })
        return formatted

    def clear_history(self):
        """Clear conversation history."""
        self._history = []
        self.chat = None
        print("🧹 Conversation history cleared")

    def set_fast_mode(self, fast: bool):
        """Switch between fast and full mode."""
        self.fast_mode = fast
        self.model_name = GEMINI_FLASH_MODEL if fast else GEMINI_PRO_MODEL
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=ALFRED_FAST_PROMPT if fast else ALFRED_SYSTEM_PROMPT
        )
        self.chat = None  # Reset chat for new model
        print(f"🧠 Switched to {'fast' if fast else 'full'} mode ({self.model_name})")


# Test function
if __name__ == "__main__":
    print("Testing AlfredBrain...")
    brain = AlfredBrain(fast_mode=True)

    test_inputs = [
        "What should I focus on today?",
        "Should I learn Python or JavaScript?",
        "How do I price my consulting services?"
    ]

    for inp in test_inputs:
        print(f"\n👤 User: {inp}")
        response = brain.think(inp)
        print(f"🎩 Alfred: {response}")
