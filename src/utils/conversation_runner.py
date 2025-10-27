"""Utility for executing multi-turn conversations."""
from typing import List, Dict, Any
from playwright.sync_api import Page
from ..extraction import send_prompt, read_last_bot_message
from .button_handler import click_option_button


class ConversationTurn:
    """Represents a single turn in a conversation."""
    
    def __init__(self, turn_data: Dict[str, Any]):
        self.turn_number = turn_data.get("turn", 0)
        self.action = turn_data["action"]  # "message" or "click_button"
        self.input = turn_data.get("input", "")
        self.button_selector = turn_data.get("button_selector", "")
        self.button_text = turn_data.get("button_text", "")  # For logging/display
        self.expected_answer = turn_data.get("expected_answer", "")
        self.expected_keywords = turn_data.get("expected_keywords", [])
        self.expected_intent = turn_data.get("expected_intent", "")
        self.threshold = turn_data.get("threshold", 0.70)
        
    def execute(self, page: Page) -> str:
        """
        Execute this conversation turn.
        
        Args:
            page: Playwright page object
            
        Returns:
            Bot's response text
        """
        if self.action == "message":
            # Count messages before sending
            messages_before = page.locator(".mimir-chat-message").count()
            
            send_prompt(page, self.input)
            
            # Wait for NEW message to appear (bot's response)
            page.wait_for_function(
                f"document.querySelectorAll('.mimir-chat-message').length > {messages_before}",
                timeout=15000
            )
            page.wait_for_timeout(2000)  # Wait for message to fully render
            
            return read_last_bot_message(page)
            
        elif self.action == "click_button":
            # click_option_button already waits for new message
            click_option_button(page, self.button_selector)
            page.wait_for_timeout(2000)
            return read_last_bot_message(page)
            
        else:
            raise ValueError(f"Unknown action: {self.action}")


class ConversationRunner:
    """Executes multi-turn conversations and tracks responses."""
    
    def __init__(self, page: Page):
        self.page = page
        self.conversation_history: List[Dict[str, str]] = []
        
    def execute_turn(self, turn: ConversationTurn) -> str:
        """
        Execute a single conversation turn.
        
        Args:
            turn: ConversationTurn object
            
        Returns:
            Bot's response
        """
        response = turn.execute(self.page)
        
        # Track history
        self.conversation_history.append({
            "turn": turn.turn_number,
            "action": turn.action,
            "input": turn.input if turn.action == "message" else f"[Button: {turn.button_selector}]",
            "response": response
        })
        
        return response
        
    def execute_flow(self, turns: List[Dict[str, Any]]) -> List[str]:
        """
        Execute a complete conversation flow.
        
        Args:
            turns: List of turn data dictionaries
            
        Returns:
            List of bot responses for each turn
        """
        responses = []
        for turn_data in turns:
            turn = ConversationTurn(turn_data)
            response = self.execute_turn(turn)
            responses.append(response)
        return responses
        
    def get_history(self) -> List[Dict[str, str]]:
        """Get the conversation history."""
        return self.conversation_history
        
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []

