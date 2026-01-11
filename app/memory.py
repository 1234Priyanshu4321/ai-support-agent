from typing import Dict, List

conversation_memory: Dict[str, List[dict]] = {}

MAX_MEMORY_MESSAGES = 6


def get_memory(session_id: str) -> List[dict]:
    return conversation_memory.get(session_id, [])


def add_to_memory(session_id: str, message: dict) -> None:
    if session_id not in conversation_memory:
        conversation_memory[session_id] = []

    conversation_memory[session_id].append(message)

    conversation_memory[session_id] = conversation_memory[session_id][-MAX_MEMORY_MESSAGES:]
