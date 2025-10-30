# app/services/email_service.py
import os
import json
import requests
from typing import Optional, Dict

EMAILJS_ENDPOINT = "https://api.emailjs.com/api/v1.0/email/send"

def _or_na(v: Optional[str], fallback: str = "N/A") -> str:
    if v is None:
        return fallback
    v = str(v).strip()
    return v if v else fallback

def _build_plaintext(payload: Dict) -> str:
    return (
        f"Category: {_or_na(payload.get('category')).upper()}\n"
        f"Title: {_or_na(payload.get('title'))}\n"
        f"Description:\n{_or_na(payload.get('description'))}\n\n"
        f"Steps:\n{_or_na(payload.get('steps'))}\n\n"
        f"Expected:\n{_or_na(payload.get('expected_behavior'))}\n\n"
        f"Actual:\n{_or_na(payload.get('actual_behavior'))}\n\n"
        f"Browser Info:\n{_or_na(payload.get('browser_info'))}\n\n"
        f"Additional Info:\n{_or_na(payload.get('additional_info'), 'None')}\n\n"
        f"From Email: {_or_na(payload.get('from_email'), 'Not provided')}\n"
    )

def _build_html(payload: Dict, app_name: str) -> str:
    def esc(s: Optional[str]) -> str:
        if s is None:
            return "N/A"
        return (str(s)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;"))
    rows = [
        ("Category", _or_na(payload.get("category")).upper()),
        ("Title", _or_na(payload.get("title"))),
        ("Description", _or_na(payload.get("description"))),
        ("Steps", _or_na(payload.get("steps"))),
        ("Expected", _or_na(payload.get("expected_behavior"))),
        ("Actual", _or_na(payload.get("actual_behavior"))),
        ("Browser Info", _or_na(payload.get("browser_info"))),
        ("Additional Info", _or_na(payload.get("additional_info"), "None")),
        ("From Email", _or_na(payload.get("from_email"), "Not provided")),
    ]
    rows_html = "".join(
        f"""
        <tr>
          <td style="padding:8px 12px;border:1px solid #e5e7eb;background:#f9fafb;font-weight:600;color:#111827">{esc(k)}</td>
          <td style="padding:8px 12px;border:1px solid #e5e7eb;color:#111827;white-space:pre-wrap">{esc(v)}</td>
        </tr>
        """
        for k, v in rows
    )
    return f"""
    <div style="font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;font-size:14px;color:#111827">
      <div style="margin-bottom:10px;color:#374151">
        A new <strong>{esc(app_name)}</strong> feedback message has been received.
      </div>
      <div style="display:flex;align-items:center;margin:14px 0">
        <div style="font-size:28px;margin-right:10px">👤</div>
        <div>
          <div style="font-size:16px;font-weight:700;color:#111827">{esc(_or_na(payload.get('name')))}</div>
          <div style="font-size:12px;color:#6b7280">{esc(_or_na(payload.get('time')))}</div>
        </div>
      </div>
      <table role="presentation" cellpadding="0" cellspacing="0" style="border-collapse:collapse;width:100%;max-width:720px">
        {rows_html}
      </table>
      <div style="margin-top:14px;font-size:12px;color:#6b7280">
        This message was sent via {esc(app_name)} feedback.
      </div>
    </div>
    """

class EmailService:
    """
    Sends feedback using EmailJS REST API.

    Modes:
      1) If EMAILJS_PRIVATE_KEY is set -> use Authorization: Bearer <PRIVATE_KEY>.
      2) Else -> include user_id = EMAILJS_PUBLIC_KEY in the JSON body (no Authorization header).

    Required ENV:
      EMAILJS_SERVICE_ID
      EMAILJS_TEMPLATE_ID
      EITHER EMAILJS_PRIVATE_KEY OR EMAILJS_PUBLIC_KEY (for user_id mode)
      APP_NAME (optional; default 'gitRAG')
    """

    @staticmethod
    def send_feedback(payload: Dict) -> bool:
        service_id   = os.getenv("EMAILJS_SERVICE_ID")
        template_id  = os.getenv("EMAILJS_TEMPLATE_ID")
        private_key  = os.getenv("EMAILJS_PRIVATE_KEY")  
        public_key   = os.getenv("EMAILJS_PUBLIC_KEY")   
        app_name     = os.getenv("APP_NAME", "gitRAG")

        missing_base = [k for k, v in {
            "EMAILJS_SERVICE_ID": service_id,
            "EMAILJS_TEMPLATE_ID": template_id
        }.items() if not v]
        if missing_base:
            raise RuntimeError(f"Missing EmailJS env: {', '.join(missing_base)}")

        # Choose auth mode
        use_private = bool(private_key)
        if not use_private and not public_key:
            raise RuntimeError("Missing EmailJS env: EMAILJS_PUBLIC_KEY (required when no private key)")

        # Build template params (MUST match your EmailJS template variable names)
        template_params = {
            "name": _or_na(payload.get("name")),
            "from_email": _or_na(payload.get("from_email"), "Not provided"),
            "category": _or_na(payload.get("category")).upper(),
            "title": _or_na(payload.get("title")),
            "description": _or_na(payload.get("description")),
            "steps": _or_na(payload.get("steps")),
            "expected_behavior": _or_na(payload.get("expected_behavior")),
            "actual_behavior": _or_na(payload.get("actual_behavior")),
            "browser_info": _or_na(payload.get("browser_info")),
            "additional_info": _or_na(payload.get("additional_info"), "None"),
            "time": _or_na(payload.get("time")),
            "subject": f"[{app_name} Feedback] {_or_na(payload.get('category')).upper()} • {_or_na(payload.get('title'))}",
            "html_body": _build_html(payload, app_name),
            "text_body": _build_plaintext(payload),
        }

        body = {
            "service_id": service_id,
            "template_id": template_id,
            "template_params": template_params,
        }

        headers = {"Content-Type": "application/json"}

        if use_private:
            # Server-to-server (preferred, no user_id needed)
            headers["Authorization"] = f"Bearer {private_key}"
        else:
            # Public key mode requires user_id in body, no Authorization header
            body["user_id"] = public_key

        resp = requests.post(EMAILJS_ENDPOINT, headers=headers, data=json.dumps(body), timeout=20)

        if resp.status_code >= 300:
            # Helpful debug info in logs
            raise RuntimeError(f"EmailJS send failed ({resp.status_code}): {resp.text}")

        return True