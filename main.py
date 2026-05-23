"""
main.py — CLI entry point for the Closira AI Agent.

Usage:
    python main.py

Commands during conversation:
    /qualify    — move to lead qualification stage
    /summary    — generate session summary and exit
    /exit       — end session
    /help       — show commands
"""

import os
import json
import anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from workflow import ConversationWorkflow
from logger import log_session_start

load_dotenv()
console = Console()

COMMANDS = {
    "/qualify": "Start lead qualification questions",
    "/summary": "Generate session summary and exit",
    "/exit":    "End the session",
    "/help":    "Show this help message",
}

WELCOME_MESSAGE = (
    "Hello! Welcome to Bloom Aesthetics Clinic 🌸\n\n"
    "I'm Bloom, your virtual assistant. I can help you with information about our services, "
    "pricing, and bookings. How can I help you today?"
)


def print_welcome():
    console.print(Panel.fit(
        "[bold magenta]Bloom Aesthetics Clinic — AI Support Agent[/bold magenta]\n"
        "[dim]Type /help for commands | /qualify to start lead qualification | /summary to end[/dim]",
        border_style="magenta",
    ))
    console.print(f"\n[bold green]Bloom:[/bold green] {WELCOME_MESSAGE}\n")


def print_help():
    console.print("\n[bold]Available commands:[/bold]")
    for cmd, desc in COMMANDS.items():
        console.print(f"  [cyan]{cmd}[/cyan]  — {desc}")
    console.print()


def print_summary(summary: dict):
    console.print("\n")
    console.print(Panel(
        Markdown(f"""## Session Summary

**Customer Intent:** {summary.get('customer_intent', 'N/A')}

**Key Details Collected:**
{chr(10).join(f'- {d}' for d in summary.get('key_details_collected', ['None']))}

**SOP Gaps Identified:**
{chr(10).join(f'- {g}' for g in summary.get('sop_gaps_identified', ['None']))}

**Escalated:** {'Yes — ' + summary.get('escalation_reason', '') if summary.get('escalated') else 'No'}

**Lead Quality:** {summary.get('lead_quality', 'N/A').upper()}

**Recommended Next Action:** {summary.get('recommended_next_action', 'N/A')}
"""),
        title="[bold blue]End of Session Summary[/bold blue]",
        border_style="blue",
    ))


def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        console.print("[bold red]Error:[/bold red] ANTHROPIC_API_KEY not found in environment.")
        console.print("Create a .env file with: ANTHROPIC_API_KEY=your-key-here")
        return

    client = anthropic.Anthropic(api_key=api_key)
    workflow = ConversationWorkflow(client)

    log_session_start(workflow.get_session_id())
    print_welcome()

    # Add welcome message to history
    workflow._add_to_history("assistant", WELCOME_MESSAGE)

    while True:
        try:
            user_input = console.input("[bold yellow]You:[/bold yellow] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Session interrupted.[/dim]")
            break

        if not user_input:
            continue

        # Handle commands
        if user_input.lower() == "/help":
            print_help()
            continue

        elif user_input.lower() == "/qualify":
            workflow.start_qualification()
            response = workflow.process("")
            console.print(f"\n[bold green]Bloom:[/bold green] {response}\n")
            continue

        elif user_input.lower() == "/summary":
            console.print("\n[dim]Generating session summary...[/dim]")
            summary = workflow.get_summary()
            print_summary(summary)
            # Also save to file
            with open("session_summary.json", "w") as f:
                json.dump(summary, f, indent=2)
            console.print("[dim]Summary saved to session_summary.json[/dim]")
            break

        elif user_input.lower() == "/exit":
            console.print("[dim]Session ended. Goodbye![/dim]")
            break

        # Normal message processing
        response = workflow.process(user_input)

        if isinstance(response, dict):
            # Summary was returned (end of SUMMARY stage)
            print_summary(response)
            break

        console.print(f"\n[bold green]Bloom:[/bold green] {response}\n")

        # Auto-prompt for summary after escalation
        if workflow.stage == "ESCALATED":
            console.print("[dim]Session escalated. Type /summary to generate a session report, or /exit to end.[/dim]\n")


if __name__ == "__main__":
    main()
