#!/usr/bin/env python3
"""
Alfred Gemini - Voice Assistant powered by Google AI

Usage:
    python main.py              # Interactive voice mode
    python main.py --text       # Text-only mode
    python main.py --continuous # Keep listening after each response
    python main.py --test       # Quick test
"""

import argparse
import sys

from alfred import Conversation, AlfredBrain
from alfred.conversation import ConversationConfig


def print_banner():
    """Print Alfred banner."""
    banner = """
    ╔═══════════════════════════════════════════╗
    ║                                           ║
    ║     █████╗ ██╗     ███████╗██████╗        ║
    ║    ██╔══██╗██║     ██╔════╝██╔══██╗       ║
    ║    ███████║██║     █████╗  ██████╔╝       ║
    ║    ██╔══██║██║     ██╔══╝  ██╔══██╗       ║
    ║    ██║  ██║███████╗██║     ██║  ██║       ║
    ║    ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝       ║
    ║                                           ║
    ║    Powered by Google Gemini               ║
    ║    No bullshit. Just results.             ║
    ║                                           ║
    ╚═══════════════════════════════════════════╝
    """
    print(banner)


def run_voice_mode(continuous: bool = False):
    """Run Alfred in voice interaction mode."""
    print_banner()

    config = ConversationConfig(
        continuous_mode=continuous,
        fast_mode=True,
        greeting="Alfred here. What do you need?"
    )

    convo = Conversation(config)

    # Set up callbacks for visibility
    convo.on_transcript = lambda t: print(f"\n👤 You: {t}")
    convo.on_response = lambda r: print(f"\n🎩 Alfred: {r}\n")
    convo.on_error = lambda e: print(f"\n❌ Error: {e}")

    if continuous:
        print("🔄 Continuous mode - say 'goodbye' to exit")
        convo.start()

        # Keep main thread alive
        try:
            while convo._running:
                pass
        except KeyboardInterrupt:
            print("\n👋 Interrupted")
            convo.stop()
    else:
        print("🎤 Single interaction mode")
        convo.single_interaction()


def run_text_mode():
    """Run Alfred in text-only mode (no voice)."""
    print_banner()
    print("📝 Text mode - type 'quit' to exit\n")

    brain = AlfredBrain(fast_mode=True)

    while True:
        try:
            user_input = input("👤 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("🎩 Alfred: Later.")
                break

            response = brain.think(user_input)
            print(f"\n🎩 Alfred: {response}\n")

        except KeyboardInterrupt:
            print("\n👋 Bye")
            break
        except EOFError:
            break


def run_test():
    """Quick test of Alfred's brain."""
    print("🧪 Testing Alfred...")

    brain = AlfredBrain(fast_mode=True)

    test_questions = [
        "What's the most important thing for success?",
        "Should I follow my passion or follow the money?",
    ]

    for q in test_questions:
        print(f"\n👤 Test: {q}")
        response = brain.think(q, use_history=False)
        print(f"🎩 Alfred: {response}")

    print("\n✅ Test complete")


def main():
    parser = argparse.ArgumentParser(
        description="Alfred - Voice Assistant powered by Google Gemini"
    )
    parser.add_argument(
        '--text', '-t',
        action='store_true',
        help='Text-only mode (no voice)'
    )
    parser.add_argument(
        '--continuous', '-c',
        action='store_true',
        help='Continuous listening mode'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run quick test'
    )

    args = parser.parse_args()

    try:
        if args.test:
            run_test()
        elif args.text:
            run_text_mode()
        else:
            run_voice_mode(continuous=args.continuous)

    except KeyboardInterrupt:
        print("\n👋 Goodbye")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
