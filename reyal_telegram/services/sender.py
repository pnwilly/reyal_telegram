"""Low-level Telegram Bot API sender."""

from __future__ import annotations

import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


_TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


def send_message(
	token: str,
	chat_id: str,
	text: str,
	disable_web_page_preview: bool = False,
) -> tuple[bool, str | None]:
	"""POST a message to the Telegram Bot API.

	Returns ``(True, None)`` on success, or ``(False, error_string)`` on failure.
	Uses stdlib ``urllib`` only; no extra dependencies required.
	"""
	url = _TELEGRAM_API.format(token=token)
	payload = {
		"chat_id": chat_id,
		"text": text,
		"parse_mode": "HTML",
		"disable_web_page_preview": disable_web_page_preview,
	}

	body = json.dumps(payload).encode("utf-8")
	req = Request(url, data=body, headers={"Content-Type": "application/json"})

	try:
		with urlopen(req, timeout=10) as resp:
			result = json.loads(resp.read().decode("utf-8"))
			if result.get("ok"):
				return True, None
			return False, result.get("description", "Unknown Telegram API error")
	except HTTPError as exc:
		try:
			detail = json.loads(exc.read().decode("utf-8"))
			return False, detail.get("description", str(exc))
		except Exception:
			return False, str(exc)
	except URLError as exc:
		return False, str(exc.reason)
	except Exception as exc:
		return False, str(exc)
