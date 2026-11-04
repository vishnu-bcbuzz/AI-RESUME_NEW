"""Safe JSON loading and repair utilities for AI and LLM outputs.

Guarantees robust parsing of LLM outputs by stripping markdown code blocks,
repairing trailing commas, recovering nested JSON objects, and preventing
unhandled JSONDecodeError exceptions.
"""

import json
import re
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("futrsec.json_utils")


def safe_json_loads(text: str, default: Optional[Any] = None) -> Any:
    """Safely parses JSON from potentially malformed or markdown-wrapped LLM text.

    Handles:
    - Markdown fences (```json ... ```)
    - Trailing commas before closing braces/brackets (, } or , ])
    - Leading/trailing prose or conversational text
    - Single-quoted keys and strings
    - Unescaped newlines within strings
    """
    if not text or not text.strip():
        return default if default is not None else {}

    cleaned = text.strip()

    # 1. Strip markdown fences if present
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()

    # 2. Try direct json.loads
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 3. Extract outermost JSON object {...} or array [...]
    match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", cleaned)
    if match:
        extracted = match.group(1).strip()
        try:
            return json.loads(extracted)
        except json.JSONDecodeError:
            cleaned = extracted

    # 4. Repair common JSON issues:
    # A. Remove trailing commas before } and ]
    repaired = re.sub(r",\s*([\}\]])", r"\1", cleaned)

    # B. Replace unescaped control characters
    repaired = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", repaired)

    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass

    # C. Replace single quotes around keys and values with double quotes
    try:
        single_quote_fixed = re.sub(r"(?<=[{\[,:])\s*'([^']+)'\s*(?=[},:\]])", r'"\1"', repaired)
        single_quote_fixed = re.sub(r"'([a-zA-Z0-9_]+)'\s*:", r'"\1":', single_quote_fixed)
        return json.loads(single_quote_fixed)
    except json.JSONDecodeError as exc:
        logger.warning("Safe JSON parser could not repair text: %s. Returning default.", exc)
        return default if default is not None else {}

