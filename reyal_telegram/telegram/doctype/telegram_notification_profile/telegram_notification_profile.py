import frappe
from frappe.model.document import Document


class TelegramNotificationProfile(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		display_name: DF.Data | None
		enabled: DF.Check
		telegram_chat_id: DF.Data | None
		user: DF.Link

	# end: auto-generated types
