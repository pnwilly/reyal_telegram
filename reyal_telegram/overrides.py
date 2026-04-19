"""Monkey-patches applied once per worker process."""

from __future__ import annotations


def apply_patches():
    import frappe.desk.doctype.notification_log.notification_log as nl_module

    if getattr(nl_module, "_reyal_telegram_patched", False):
        return

    nl_module._original_send_notification_email = nl_module.send_notification_email
    nl_module.send_notification_email = _send_notification_email
    nl_module._reyal_telegram_patched = True


def _send_notification_email(doc):
    import frappe

    try:
        profile = frappe.get_doc("Telegram Notification Profile", doc.for_user)
        if profile.suppress_email_notifications:
            return
    except frappe.DoesNotExistError:
        pass

    import frappe.desk.doctype.notification_log.notification_log as nl_module
    nl_module._original_send_notification_email(doc)


def send_fallback_email(doc):
    """Send the notification email that was suppressed after a Telegram failure."""
    import frappe.desk.doctype.notification_log.notification_log as nl_module

    original = getattr(nl_module, "_original_send_notification_email", nl_module.send_notification_email)
    try:
        original(doc)
    except Exception:
        import frappe
        frappe.log_error(title="Telegram Fallback Email Error", message=frappe.get_traceback())
