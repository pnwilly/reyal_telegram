"""Entry point for processing new Notification Log entries.

Called via doc_events hook after_insert on Notification Log.
The actual send is enqueued so that a slow or failing Telegram API call
never blocks the notification save transaction.
"""

from __future__ import annotations

import frappe
from frappe.utils import now_datetime


def handle_notification_log(doc, method=None):
	"""Enqueue a Telegram send for a newly inserted Notification Log."""
	frappe.enqueue(
		"reyal_telegram.services.dispatcher._process",
		notification_log=doc.name,
		queue="short",
		now=frappe.flags.in_test,
	)


def _process(notification_log: str):
	"""Load settings, validate routing, format, send, and record the delivery."""
	log = frappe.get_doc("Notification Log", notification_log)

	# Skip if already sent (guard against duplicate enqueues).
	if log.get("custom_telegram_sent"):
		return

	settings = frappe.get_single("Telegram Settings")

	if not settings.enabled:
		return

	token = settings.get_password("telegram_bot_token")
	if not token:
		return

	# Resolve user profile:
	profile = _get_profile(log.for_user)
	if not profile:
		# No profile at all; nothing to log, nothing to send.
		return

	if not profile.enabled:
		_save_delivery(log, profile, settings, status="Skipped", error="Profile disabled")
		return

	chat_id = profile.telegram_chat_id or settings.default_telegram_chat_id
	if not chat_id:
		_save_delivery(log, profile, settings, status="Skipped", error="No chat ID on profile and no default configured")
		return

	# Check notification type gate:
	from reyal_telegram.services.formatter import settings_flag_for_type

	flag = settings_flag_for_type(log.type or "")
	if not settings.get(flag):
		_save_delivery(log, profile, settings, status="Skipped", error=f"Type '{log.type}' disabled in settings")
		return

	# Build message:
	from reyal_telegram.services.formatter import build_message

	msg = build_message(log)

	# Send:
	from reyal_telegram.services.sender import send_message

	success, error = send_message(
		token=token,
		chat_id=chat_id,
		text=msg["text"],
		disable_web_page_preview=bool(settings.disable_web_page_preview),
	)

	if success:
		_save_delivery(log, profile, settings, status="Sent", msg=msg, chat_id=chat_id)
		_mark_log_sent(log)
	else:
		_save_delivery(
			log, profile, settings,
			status="Failed",
			msg=msg,
			chat_id=chat_id,
			error=error,
		)
		frappe.log_error(
			title="Telegram Notification Failed",
			message=f"Log: {log.name} | User: {log.for_user} | Error: {error}",
		)


def _get_profile(user: str | None):
	if not user:
		return None
	try:
		return frappe.get_doc("Telegram Notification Profile", user)
	except frappe.DoesNotExistError:
		return None


def _mark_log_sent(log):
	frappe.db.set_value(
		"Notification Log",
		log.name,
		{
			"custom_telegram_sent": 1,
			"custom_telegram_sent_on": now_datetime(),
		},
		update_modified=False,
	)


def _save_delivery(log, profile, settings, *, status: str, msg: dict | None = None, chat_id: str = "", error: str = ""):
	try:
		delivery = frappe.new_doc("Telegram Delivery Log")
		delivery.notification_log = log.name
		delivery.for_user = log.for_user
		delivery.telegram_chat_id = chat_id or profile.telegram_chat_id or settings.default_telegram_chat_id or ""
		delivery.status = status
		delivery.notification_type = log.type or ""
		if msg:
			delivery.title = (msg.get("title") or "")[:140]
			delivery.message = msg.get("message") or ""
			delivery.open_url = msg.get("open_url") or ""
		if error:
			delivery.error_message = error
		if status == "Sent":
			delivery.sent_on = now_datetime()
		delivery.insert(ignore_permissions=True)
	except Exception:
		frappe.log_error(title="Telegram Delivery Record Error", message=frappe.get_traceback())
