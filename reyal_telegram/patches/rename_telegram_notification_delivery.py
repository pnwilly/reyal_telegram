import frappe


def execute():
	if frappe.db.table_exists("tabTelegram Notification Delivery") and not frappe.db.table_exists("tabTelegram Delivery Log"):
		frappe.rename_doc("DocType", "Telegram Notification Delivery", "Telegram Delivery Log", force=True)
		frappe.db.commit()
