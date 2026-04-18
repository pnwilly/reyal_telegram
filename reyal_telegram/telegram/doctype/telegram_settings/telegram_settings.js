frappe.ui.form.on("Telegram Settings", {
	refresh(frm) {
		frm.add_custom_button(__("Notification Profiles"), () => {
			frappe.set_route("List", "Telegram Notification Profile");
		}, __("View"));

		frm.add_custom_button(__("Send Test Message"), () => {
			frappe.prompt(
				{
					fieldname: "chat_id",
					fieldtype: "Data",
					label: __("Chat ID"),
					reqd: 1,
					description: __("Enter the Telegram chat ID to send the test message to."),
				},
				({ chat_id }) => {
					frappe.show_alert({ message: __("Sending…"), indicator: "blue" });
					frappe.call({
						method: "reyal_telegram.telegram.doctype.telegram_settings.telegram_settings.send_test_message",
						args: { chat_id },
						callback(r) {
							if (!r.exc) {
								frappe.show_alert({
									message: __("Test message sent successfully."),
									indicator: "green",
								});
							}
						},
					});
				},
				__("Send Test Message"),
				__("Send")
			);
		});
	},
});
