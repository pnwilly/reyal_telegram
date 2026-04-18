import frappe
from frappe.model.document import Document


class TelegramDeliveryLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		error_message: DF.LongText | None
		for_user: DF.Link | None
		message: DF.LongText | None
		notification_log: DF.Link | None
		notification_type: DF.Data | None
		open_url: DF.Data | None
		sent_on: DF.Datetime | None
		status: DF.Literal["Pending", "Sent", "Failed", "Skipped"]
		telegram_chat_id: DF.Data | None
		title: DF.SmallText | None

	# end: auto-generated types

	@staticmethod
	def clear_old_logs(days=30):
		from frappe.query_builder import Interval
		from frappe.query_builder.functions import Now

		table = frappe.qb.DocType("Telegram Delivery Log")
		frappe.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))
