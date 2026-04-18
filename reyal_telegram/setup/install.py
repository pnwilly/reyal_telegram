import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


_CUSTOM_FIELDS = {
	"Notification Log": [
		{
			"fieldname": "custom_telegram_sent",
			"fieldtype": "Check",
			"label": "Telegram Sent",
			"insert_after": "read",
			"read_only": 1,
			"no_copy": 1,
		},
		{
			"fieldname": "custom_telegram_sent_on",
			"fieldtype": "Datetime",
			"label": "Telegram Sent On",
			"insert_after": "custom_telegram_sent",
			"read_only": 1,
			"no_copy": 1,
		},
	]
}


def after_install():
	create_custom_fields(_CUSTOM_FIELDS, ignore_validate=True, update=True)
	_register_log_settings()
	frappe.db.commit()


def _register_log_settings():
	log_settings = frappe.get_single("Log Settings")
	rows = log_settings.get("logs_to_clear", [])

	# Remove stale entry from old doctype name if present.
	for row in rows:
		if row.ref_doctype == "Telegram Notification Delivery":
			log_settings.remove(row)
			break

	already_registered = any(row.ref_doctype == "Telegram Delivery Log" for row in log_settings.get("logs_to_clear", []))
	if not already_registered:
		log_settings.append("logs_to_clear", {
			"ref_doctype": "Telegram Delivery Log",
			"days": 30,
		})

	log_settings.save(ignore_permissions=True)
