"""
utils.py — shared utilities for Production Parser
"""


def safe_print(message: str):
    """
    Safe print wrapper so logs format consistently.
    """
    print(f"[LOG] {message}")

