app_name = "reyal_telegram"
app_title = "Reyal Telegram"
app_publisher = "Patrick Willy"
app_description = "Sends Frappe Notifications to Telegram via a bot"
app_email = "pin@reyal.email"
app_license = "mit"

# Install / migrate hooks:

after_install = "reyal_telegram.setup.install.after_install"
after_migrate = "reyal_telegram.setup.install.after_install"

# Request hooks:

before_request = "reyal_telegram.overrides.apply_patches"

# Document events:

doc_events = {
	"Notification Log": {
		"after_insert": "reyal_telegram.services.dispatcher.handle_notification_log",
	},
}
