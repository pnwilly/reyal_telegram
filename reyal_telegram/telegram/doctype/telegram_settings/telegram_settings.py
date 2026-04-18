import frappe
from frappe import _
from frappe.model.document import Document


class TelegramSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		default_telegram_chat_id: DF.Data | None
		disable_web_page_preview: DF.Check
		enabled: DF.Check
		send_alerts: DF.Check
		send_assignments: DF.Check
		send_generic_updates: DF.Check
		send_mentions: DF.Check
		send_shares: DF.Check
		telegram_bot_token: DF.Password | None

	# end: auto-generated types


@frappe.whitelist()
def send_test_message(chat_id: str) -> dict:
	"""Send a test message to the given chat ID using the configured bot token."""
	settings = frappe.get_single("Telegram Settings")

	if not settings.enabled:
		frappe.throw(_("Telegram Settings is not enabled."))

	token = settings.get_password("telegram_bot_token")
	if not token:
		frappe.throw(_("No bot token configured in Telegram Settings."))

	if not chat_id:
		frappe.throw(_("Please provide a chat ID."))

	from reyal_telegram.services.sender import send_message

	text = (
		"<b>Reyal Telegram: test message</b>\n\n"
		"If you can read this, your bot is configured correctly. ✓"
	)

	success, error = send_message(
		token=token,
		chat_id=chat_id,
		text=text,
		disable_web_page_preview=bool(settings.disable_web_page_preview),
	)

	if success:
		return {"status": "ok"}

	frappe.throw(_("Test message failed: {0}").format(error))
