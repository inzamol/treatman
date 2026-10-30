"""
TM Voice-First Interactive Interface
"""

import sys
from tm.config import get_config
from tm.core.agent import TMAgent
from tm.voice.ear import Ear
from tm.voice.speaker import Speaker

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    console = Console()
except ImportError:
    console = None


def run_voice_mode():
    """Runs continuous hands-free voice interface with real-time speech and auditory responses."""
    config = get_config()
    agent = TMAgent(config)
    ear = Ear(config)
    speaker = Speaker(config)

    user_title = config.agent.user_title or "Sir"

    if console:
        console.print(Panel(
            Text(f"🎙️ TM VOICE INTERFACE ACTIVE\nVoice: {config.voice.voice_id}\n\nSpeak into your microphone, or press Ctrl+C to exit.", justify="center", style="bold cyan"),
            title=f"[bold green]TM - Hands-Free Voice Mode[/bold green]",
            border_style="cyan"
        ))
    else:
        print(f"\n=== TM VOICE INTERFACE ACTIVE ===")
        print(f"Voice: {config.voice.voice_id}")
        print("Speak into your microphone or press Ctrl+C to exit.\n")

    # Initial greeting
    greeting = f"{config.agent.name} online and listening, {user_title}. How may I assist you?"
    if console:
        console.print(f"[bold cyan]{config.agent.name}:[/bold cyan] {greeting}")
    else:
        print(f"{config.agent.name}: {greeting}")
    speaker.speak(greeting, interruptable=True)

    while True:
        try:
            def status_cb(msg: str):
                if console:
                    console.print(f"[dim italic yellow]🎙️  {msg}[/dim italic yellow]")
                else:
                    print(f">> {msg}")

            # Listen for speech
            text = ear.listen_phrase(status_callback=status_cb)

            if not text:
                continue

            if console:
                console.print(f"\n[bold green]{user_title} (Voice):[/bold green] {text}")
            else:
                print(f"\n{user_title} (Voice): {text}")

            # Exit command detection
            if text.lower() in ["exit", "quit", "goodbye", "shut down", "goodbye jarvis"]:
                bye_msg = f"Shutting down. Good day, {user_title}."
                if console:
                    console.print(f"[cyan]{config.agent.name}:[/cyan] {bye_msg}")
                else:
                    print(f"{config.agent.name}: {bye_msg}")
                speaker.speak(bye_msg, interruptable=False)
                break

            # ReAct Agent execution
            def agent_status(st: str, msg: str):
                if console:
                    if st == "thinking":
                        console.print(f"[dim italic cyan]⚡ {msg}[/dim italic cyan]")
                    elif st == "executing":
                        console.print(f"[bold yellow]⚙️  {msg}[/bold yellow]")
                else:
                    print(f">> {msg}")

            result = agent.execute_turn(user_message=text, status_callback=agent_status)
            response = result.get("response", "")

            if console:
                console.print(f"[bold cyan]{config.agent.name}:[/bold cyan] {response}\n")
            else:
                print(f"\n{config.agent.name}: {response}\n")

            # Speak response
            speaker.speak(response, interruptable=True)

        except KeyboardInterrupt:
            print("\nExiting Voice Mode.")
            speaker.stop()
            break
        except Exception as e:
            if console:
                console.print(f"[bold red]Voice error:[/bold red] {e}")
            else:
                print(f"Error: {e}")

