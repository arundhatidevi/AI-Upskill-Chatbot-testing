import pytest
import yaml
import logging
from pathlib import Path
from playwright.sync_api import Page
from src.config import settings
from src.extraction import open_chat_if_needed
from src.utils.conversation_runner import ConversationRunner, ConversationTurn
from src.validators.intent import validate_intent
from src.validators.semantic import validate_semantic_similarity

logger = logging.getLogger(__name__)

DATA_FILE = Path(__file__).parent / "data" / "conversation_flows.yaml"


def load_conversation_flows():
    with open(DATA_FILE, "r") as f:
        data = yaml.safe_load(f)
    return data.get("conversation_flows", [])


@pytest.mark.parametrize("test_case", load_conversation_flows(), ids=lambda tc: tc["id"])
def test_conversation_flow(page: Page, test_case: dict):
    """
    Test multi-turn conversation flows.
    Execute multiple turns and validate each response.
    """
    test_id = test_case["id"]
    description = test_case["description"]
    turns = test_case["turns"]

    logger.info(f"[{test_id}] Starting conversation flow test")
    logger.info(f"[{test_id}] Description: {description}")
    logger.info(f"[{test_id}] Turns: {len(turns)}")

    # Navigate and open chat
    page.goto(settings.base_url)
    page.wait_for_load_state("networkidle")
    open_chat_if_needed(page)
    
    # Skip reset to avoid modal issues (same as test_prompt_injection)
    logger.info(f"[{test_id}] Using existing conversation state (skipping reset to avoid modal blocking)")
    
    # Wait for welcome message and buttons
    page.wait_for_selector(".mimir-chip-button", timeout=5000)
    page.wait_for_timeout(1000)

    # Execute conversation
    runner = ConversationRunner(page)
    
    for turn_data in turns:
        turn = ConversationTurn(turn_data)
        turn_num = turn.turn_number
        
        logger.info(f"[{test_id}] Turn {turn_num}: {turn.action} - {turn.input or turn.button_selector}")
        
        # Execute turn
        response = runner.execute_turn(turn)
        logger.info(f"[{test_id}] Turn {turn_num} response: {response[:100]}...")
        
        # Validate semantic similarity if specified (preferred method)
        if turn.expected_answer:
            semantic_result = validate_semantic_similarity(
                turn.expected_answer, 
                response, 
                turn.threshold
            )
            logger.info(
                f"[{test_id}] Turn {turn_num} semantic similarity: {semantic_result.similarity:.4f} "
                f"(threshold: {turn.threshold})"
            )
            
            assert semantic_result.passed, (
                f"Turn {turn_num} failed - Semantic similarity too low.\n"
                f"Expected: {turn.expected_answer}\n"
                f"Actual: {response}\n"
                f"Similarity: {semantic_result.similarity:.4f} < {turn.threshold}"
            )
        
        # Validate intent if specified
        if turn.expected_intent:
            passed, intent_result = validate_intent(response, turn.expected_intent, turn.threshold)
            logger.info(
                f"[{test_id}] Turn {turn_num} intent: {intent_result.decision}, "
                f"Confidence: {intent_result.confidence:.2f}"
            )
            
            assert passed, (
                f"Turn {turn_num} failed - Intent mismatch.\n"
                f"Expected intent: {turn.expected_intent}\n"
                f"Response: {response}\n"
                f"Decision: {intent_result.decision}, Confidence: {intent_result.confidence:.2f}"
            )
    
    # Log conversation history
    history = runner.get_history()
    logger.info(f"[{test_id}] Conversation completed successfully with {len(history)} turns")
    logger.info(f"[{test_id}] PASSED - All turns validated")

