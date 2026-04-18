app_name = "reyal_telegram"
app_title = "Reyal Telegram"
app_publisher = "Patrick Willy"
app_description = "Telegram notification bridge for Frappe / ERPNext"
app_email = "pin@reyal.email"
app_license = "mit"

# Install / migrate hooks:

after_install = "reyal_telegram.setup.install.after_install"
after_migrate = "reyal_telegram.setup.install.after_install"

# Document events:

doc_events = {
	"Notification Log": {
		"after_insert": "reyal_telegram.services.dispatcher.handle_notification_log",
	}
}
