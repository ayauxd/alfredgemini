"""Alfred Gemini - Voice Assistant powered by Google AI"""

from .brain import AlfredBrain
from .voice_input import VoiceInput
from .voice_output import VoiceOutput
from .conversation import Conversation
from .personality import ALFRED_SYSTEM_PROMPT

__version__ = "0.1.0"
__all__ = [
    "AlfredBrain",
    "VoiceInput",
    "VoiceOutput",
    "Conversation",
    "ALFRED_SYSTEM_PROMPT"
]
