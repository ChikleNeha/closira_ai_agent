"""
workflow.py — 4-stage conversation orchestrator.

State machine:
  FAQ → QUALIFICATION → (ESCALATION if triggered) → SUMMARY

The workflow manages:
  - Conversation history (passed to Claude on every turn)
  - Stage transitions
  - Unanswered question counting
  - Escalation log
  - Qualification data collection
"""

import uuid
import anthropic
from rich.console import Console

from stages.faq import answer_faq
from stages.qualification import get_qualification_questions, build_qualification_summary
from stages.escalation import (
    check_explicit_escalation,
    check_medical_question,
    handle_escalation,
)
from stages.summary import generate_summary
from logger import (
    log_event,
    log_stage_transition,
    log_session_start,
    log_session_end,
)

console = Console()

UNANSWERED_THRESHOLD = 2  # Auto-escalate after this many unanswered questions


class ConversationWorkflow:
    def __init__(self, client: anthropic.Anthropic):
        self.client = client
        self.session_id = str(uuid.uuid4())[:8]
        self.conversation_history = []   # [{role, content}] — full history sent to Claude
        self.stage = "FAQ"               # FAQ | QUALIFICATION | ESCALATED | SUMMARY
        self.unanswered_count = 0
        self.escalation_log = []
        self.qualification_answers = {}
        self.qualification_step = 0
        self.qualification_summary = {}
        self.sop_gaps = []

    # ── Public: process one user message ─────────────────────────────────────

    def process(self, user_message: str) -> str:
        """Main entry point. Takes user input, returns AI response string."""

        # Always check for explicit escalation triggers first
        should_escalate, escalate_reason = check_explicit_escalation(user_message)
        if should_escalate and self.stage not in ("ESCALATED", "SUMMARY"):
            return self._escalate(escalate_reason, user_message)

        # Medical question check
        if check_medical_question(user_message) and self.stage not in ("ESCALATED", "SUMMARY"):
            return self._escalate("medical", user_message)

        # Route to correct stage handler
        if self.stage == "FAQ":
            return self._handle_faq(user_message)
        elif self.stage == "QUALIFICATION":
            return self._handle_qualification(user_message)
        elif self.stage == "ESCALATED":
            return "Our team has been notified and will be in touch shortly. Is there anything else I can note for them?"
        elif self.stage == "SUMMARY":
            return self._handle_summary()

    # ── Stage handlers ────────────────────────────────────────────────────────

    def _handle_faq(self, user_message: str) -> str:
        result = answer_faq(user_message, self.conversation_history, self.client)

        answer_text = result.get("answer", "")
        can_answer = result.get("can_answer", True)
        escalate = result.get("escalate", False)
        escalate_reason = result.get("escalate_reason", "out_of_scope")
        sop_gap = result.get("sop_gap")

        # Track SOP gaps
        if sop_gap:
            self.sop_gaps.append(sop_gap)

        # Append to conversation history
        self._add_to_history("user", user_message)
        self._add_to_history("assistant", answer_text)

        log_event("FAQ_RESPONSE", f"can_answer={can_answer}", {
            "confidence": result.get("confidence"),
            "escalate": escalate,
        })

        if escalate:
            return self._escalate(escalate_reason or "out_of_scope", user_message)

        if not can_answer:
            self.unanswered_count += 1
            if self.unanswered_count >= UNANSWERED_THRESHOLD:
                return self._escalate("unanswered_limit", user_message)

        return answer_text

    def _handle_qualification(self, user_message: str) -> str:
        questions = get_qualification_questions()

        # Store answer to previous question
        if self.qualification_step > 0:
            prev_question = questions[self.qualification_step - 1]
            self.qualification_answers[prev_question] = user_message
            self._add_to_history("user", user_message)

        # All questions answered
        if self.qualification_step >= len(questions):
            return self._finish_qualification()

        # Ask next question
        next_question = questions[self.qualification_step]
        self.qualification_step += 1
        self._add_to_history("assistant", next_question)
        log_event("QUALIFICATION_QUESTION", f"Step {self.qualification_step}/{len(questions)}")
        return next_question

    def _finish_qualification(self) -> str:
        self.qualification_summary = build_qualification_summary(
            self.qualification_answers, self.client
        )
        log_event("QUALIFICATION_COMPLETE", "Lead summary generated", self.qualification_summary)

        lead_quality = self.qualification_summary.get("lead_quality", "unknown")
        next_action = self.qualification_summary.get("recommended_action", "")

        transition_message = (
            f"Thank you so much for sharing that! Based on what you've told me, "
            f"I'd love to help you get booked in. {next_action} "
            f"Would you like to go ahead and schedule a consultation or appointment now?"
        )

        self._add_to_history("assistant", transition_message)
        log_stage_transition("QUALIFICATION", "SUMMARY")
        self.stage = "SUMMARY"
        return transition_message

    def _handle_summary(self) -> str:
        summary = generate_summary(
            conversation_history=self.conversation_history,
            qualification_data=self.qualification_summary,
            escalation_log=self.escalation_log,
            client=self.client,
        )
        log_event("SUMMARY_GENERATED", "Session summary created", summary)
        log_session_end(self.session_id)
        return summary

    # ── Escalation ────────────────────────────────────────────────────────────

    def _escalate(self, reason: str, trigger_message: str) -> str:
        self.escalation_log.append({
            "reason": reason,
            "trigger": trigger_message,
            "stage_at_escalation": self.stage,
        })
        self.stage = "ESCALATED"
        log_stage_transition(self.stage, "ESCALATED")

        message = handle_escalation(
            reason=reason,
            trigger=trigger_message,
            conversation_history=self.conversation_history,
        )
        self._add_to_history("assistant", message)
        return message

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _add_to_history(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})

    def start_qualification(self):
        log_stage_transition("FAQ", "QUALIFICATION")
        self.stage = "QUALIFICATION"

    def get_session_id(self) -> str:
        return self.session_id

    def get_summary(self) -> dict:
        return generate_summary(
            conversation_history=self.conversation_history,
            qualification_data=self.qualification_summary,
            escalation_log=self.escalation_log,
            client=self.client,
        )
