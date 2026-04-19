"""Build Telegram HTML messages from Notification Log documents."""

from __future__ import annotations

import re

from reyal_telegram.services.utils import (
	build_doc_url,
	clean_text,
	escape_html,
	get_user_display_name,
)

# Strips the leading @mention chip (e.g. "@ Patrick W. ") from mention bodies.
# Matches @ + optional whitespace + consecutive Titlecase words (the name) only.
_LEADING_MENTION_RE = re.compile(r"^@\s*(?:[A-Z]\w*\.?\s*)+")

_TYPE_FLAG_MAP = {
	"Mention": "send_mentions",
	"Assignment": "send_assignments",
	"Alert": "send_alerts",
	"Share": "send_shares",
}

_ACTION_MAP = {
	"Mention": "mentioned you",
	"Assignment": "assigned you",
	"Alert": "sent an alert",
	"Share": "shared",
}


def settings_flag_for_type(notification_type: str) -> str:
	"""Return the Telegram Settings field name that gates this notification type."""
	return _TYPE_FLAG_MAP.get(notification_type, "send_generic_updates")


def _resolve_actor(from_user: str | None) -> str:
	if not from_user:
		return "Someone"
	return get_user_display_name(from_user) or from_user


def _resolve_target_title(doc_type: str | None, doc_name: str | None) -> str:
	if not doc_type or not doc_name:
		return doc_name or ""

	import frappe

	if doc_type == "User":
		full_name = frappe.db.get_value("User", doc_name, "full_name")
		return full_name or doc_name

	try:
		title_field = frappe.get_meta(doc_type).get_title_field()
		if title_field and title_field != "name":
			title = frappe.db.get_value(doc_type, doc_name, title_field)
			return title or doc_name
	except Exception:
		pass

	return doc_name


def build_message(log) -> dict:
	"""Build a Telegram HTML message from a Notification Log document.

	Returns a dict with keys:
	  - ``text``: full Telegram HTML string
	  - ``title``: plain heading (for delivery record)
	  - ``message``: plain body (for delivery record)
	  - ``open_url``: resolved URL
	"""
	notification_type = log.type or ""
	actor = _resolve_actor(log.from_user)
	doc_type = log.document_type or ""
	doc_name = log.document_name or ""
	target_title = _resolve_target_title(doc_type, doc_name) if doc_type else ""
	url = build_doc_url(doc_type, doc_name, log.link)

	raw_body = clean_text(log.email_content or log.subject or "")
	body = _clean_body(raw_body, notification_type)

	heading = _build_heading(notification_type, actor, target_title, doc_type, doc_name, url)
	text = _assemble(heading, body)

	return {
		"text": text,
		"title": heading,
		"message": body,
		"open_url": url,
	}



def _build_heading(
	notification_type: str,
	actor: str,
	target_title: str,
	doc_type: str,
	doc_name: str,
	url: str,
) -> str:
	actor_e = escape_html(actor)
	target_e = escape_html(target_title or doc_name)
	doc_type_e = escape_html(doc_type)
	action = escape_html(_ACTION_MAP.get(notification_type, "updated"))

	if url and target_e:
		ref = f'<a href="{url}">{target_e}</a>'
	elif target_e:
		ref = target_e
	else:
		ref = doc_type_e or "a document"

	if ref:
		return f"<b>{actor_e} {action}: {ref}</b>"
	return f"<b>{actor_e} {action}</b>"


def _clean_body(body: str, notification_type: str) -> str:
	if not body:
		return ""

	if notification_type == "Mention":
		# Frappe prepends "@Full Name\n"; strip it if present.
		body = _LEADING_MENTION_RE.sub("", body).strip()

	elif notification_type == "Share":
		# Share body is always redundant ("shared a document ... with you").
		return ""

	return body


def _assemble(heading: str, body: str) -> str:
	if body:
		return f"{heading}\n{body}"
	return heading
