"""Shared utility functions for TruthCheck."""

import re
import logging

logger = logging.getLogger(__name__)


def sanitize_text(text: str, max_length: int = 50000) -> str:
    """Basic text sanitization before passing to the model."""
    text = text.strip()
    text = re.sub(r'\r\n|\r', '\n', text)          # normalize line endings
    text = re.sub(r'\n{3,}', '\n\n', text)          # collapse excess blank lines
    text = re.sub(r'[ \t]{2,}', ' ', text)          # collapse whitespace
    return text[:max_length]


def is_valid_url(url: str) -> bool:
    pattern = re.compile(
        r'^(https?://)?' 
        r'((([a-zA-Z\d]([a-zA-Z\d\-]*[a-zA-Z\d])*)\.)+[a-zA-Z]{2,})'
        r'(:\d+)?(/[-a-zA-Z\d%_.~+]*)*'
        r'(\?[;&a-zA-Z\d%_.~+=-]*)?'
        r'(#[-a-zA-Z\d_]*)?$'
    )
    return bool(pattern.match(url))


def paginate_response(query, page: int, per_page: int):
    """Helper to build a standard paginated JSON response."""
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'items': paginated.items,
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': paginated.page,
        'has_next': paginated.has_next,
        'has_prev': paginated.has_prev,
    }
