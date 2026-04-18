import re
import unicodedata

import frappe
from frappe.utils import get_url_to_form


_HTML_TAG_RE = re.compile(r"<[^>]+>")
_EXCESS_WHITESPACE_RE = re.compile(r"[ \t]+")
_MULTI_NEWLINE_RE = re.compile(r"\n{3,}")

_HTML_ESCAPE_TABLE = str.maketrans(
	{"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}
)


def escape_html(text: str) -> str:
	"""Escape text for safe use inside Telegram HTML parse_mode messages."""
	return text.translate(_HTML_ESCAPE_TABLE)


def clean_text(text: str) -> str:
	"""Strip HTML tags, normalise non-breaking spaces and collapse whitespace."""
	if not text:
		return ""

	# Strip HTML tags
	text = _HTML_TAG_RE.sub(" ", text)

	# Replace HTML entities for non-breaking space
	text = text.replace("&nbsp;", " ")

	# Normalise unicode: replace non-breaking space (U+00A0), narrow no-break
	# space (U+202F), zero-width no-break space / BOM (U+FEFF), etc.
	text = "".join(
		" " if unicodedata.category(ch) in ("Zs", "Cf") else ch
		for ch in text
	)

	# Collapse horizontal whitespace within lines
	text = _EXCESS_WHITESPACE_RE.sub(" ", text)

	# Strip leading/trailing whitespace per line
	text = "\n".join(line.strip() for line in text.splitlines())

	# Collapse runs of blank lines
	text = _MULTI_NEWLINE_RE.sub("\n\n", text)

	return text.strip()


def build_doc_url(doc_type: str | None, doc_name: str | None, link: str | None = None) -> str:
	"""Return the best available URL for a Notification Log's reference document.

	Preference order:
	  1. ``link`` field if populated (may contain an arbitrary direct URL)
	  2. ``get_url_to_form`` built from doc_type + doc_name
	"""
	if link:
		return link.strip()
	if doc_type and doc_name:
		return get_url_to_form(doc_type, doc_name)
	return ""


def get_user_display_name(user: str | None) -> str:
	"""Return the formatted display name for a user.

	Uses reyal_core's display name utility when installed, otherwise falls
	back to the user's full_name.
	"""
	if not user:
		return ""
	if "reyal_core" in frappe.get_installed_apps():
		from reyal_core.utils import get_display_name
		return get_display_name(user) or user
	full_name = frappe.db.get_value("User", user, "full_name")
	return full_name or user
