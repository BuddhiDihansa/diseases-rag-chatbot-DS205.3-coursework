"""
logger.py
Shared utility - utils/logger.py

Purpose: Consistent logging across the whole project. Instead of
everyone using random print() statements, this gives a standard
format with timestamps and log levels (INFO, WARNING, ERROR).

Useful for the demo video too - clean, consistent logs look more
professional when screen recording the system running.
"""

import logging
import os
import sys
from datetime import datetime


def get_logger(name: str, log_to_file: bool = True) -> logging.Logger:
    """
    Creates and returns a configured logger.

    name: usually the module/agent name (e.g. "RetrieverAgent")
    log_to_file: if True, also saves logs to a file in logs/ folder

    Usage:
        from utils.logger import get_logger
        logger = get_logger("RetrieverAgent")
        logger.info("Retrieved 5 chunks")
        logger.warning("No results found")
        logger.error("Failed to connect to vector store")
    """
    logger = logging.getLogger(name)

    # avoid adding duplicate handlers if get_logger() is called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # format: [2026-07-05 10:30:00] [RetrieverAgent] [INFO] message
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # console output
    # LLM-generated text sometimes contains "smart" Unicode punctuation
    # (non-breaking hyphens like U+2011, curly quotes, etc.) that Windows'
    # default terminal encoding (cp1252) cannot represent. Without this,
    # logging such a message crashes with UnicodeEncodeError mid-run. We
    # force the console stream to UTF-8 (with a safe fallback if the
    # terminal genuinely can't display a character) so logging a message
    # containing these characters never crashes the pipeline.
    console_handler = logging.StreamHandler(sys.stdout)
    try:
        console_handler.stream.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        # older Python / non-reconfigurable stream - fall back silently,
        # the try/except around logger.emit() will still stop a crash
        pass
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # optional file output (useful for debugging + showing evidence of testing)
    if log_to_file:
        os.makedirs("logs", exist_ok=True)
        log_filename = f"logs/{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_filename, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Example usage (for testing this file individually)
if __name__ == "__main__":
    logger = get_logger("TestModule")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    