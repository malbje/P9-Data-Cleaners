"""
================================================================================
DATA CLEANERS - NOTIFICATION SYSTEM
================================================================================

This module implements the email-based notification subsystem for the
Data Cleaners platform. It retrieves upcoming appointments from the Service
Layer, generates reminder messages, and handles delivery via SMTP or dry-run
terminal output.

USAGE
-----
To execute the notification system from the command line, run:

    python -m backend.service.notification --dry-run --preview

Examples:
    # Preview upcoming appointments without sending emails
    python -m backend.service.notification --dry-run --preview

    # Process all notifications (terminal only)
    python -m backend.service.notification --dry-run

    # Send real emails (requires valid SMTP config)
    python -m backend.service.notification --send


ARCHITECTURAL ROLE
------------------
This module is positioned in the outer "Application Services" layer. It
coordinates:
    * Retrieval of appointment data from backend.service.get_upcoming_appt
    * Composition and formatting of outbound notifications
    * Delivery through SMTP (production) or terminal preview (development)

KEY DESIGN PRINCIPLES
---------------------
1. No database access in this layer.
2. Dependencies are injected indirectly (database_logic → DAL).
3. SMTP configuration is sourced from private_settings.py or environment.
4. Dry-run mode is the default to support safe local development.
5. Errors are logged cleanly without interrupting batch processing.

================================================================================
"""

from __future__ import annotations

import sys
import os
import logging
import smtplib
import socket
import traceback
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from email.message import EmailMessage


# ==============================================================================
# PATH SETUP
# ==============================================================================
# Ensures the backend package is reliably importable regardless of execution path.
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


# ==============================================================================
# LOGGING CONFIGURATION
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [notification] %(message)s",
)
log = logging.getLogger("notification")


# ==============================================================================
# SMTP CONFIGURATION
# ==============================================================================
def _load_private_settings() -> Dict[str, Optional[str]]:
    """Load SMTP settings from private_settings.py or fallback environment.

    Priority:
        1. private_settings.py if available
        2. Environment variables if present
        3. Minimal defaults (where applicable)

    Returns:
        dict: A mapping of SMTP configuration values.
    """
    cfg: Dict[str, Optional[str]] = {}

    # Try private_settings.py first
    try:
        import private_settings  # type: ignore
        cfg["SMTP_HOST"] = getattr(private_settings, "SMTP_HOST", None)
        cfg["SMTP_PORT"] = int(getattr(private_settings, "SMTP_PORT", 587))
        cfg["SMTP_USER"] = getattr(private_settings, "SMTP_USER", None)
        cfg["SMTP_PASS"] = getattr(private_settings, "SMTP_PASS", None)
        cfg["SMTP_FROM"] = getattr(private_settings, "SMTP_FROM", cfg.get("SMTP_USER"))
        log.debug("Loaded SMTP settings from private_settings.py")
    except Exception:
        log.debug("private_settings.py missing or unreadable; falling back to ENV.")

    # Environment fallback
    cfg["SMTP_HOST"] = os.getenv("SMTP_HOST", cfg.get("SMTP_HOST"))
    cfg["SMTP_PORT"] = int(os.getenv("SMTP_PORT", cfg.get("SMTP_PORT", 587)))
    cfg["SMTP_USER"] = os.getenv("SMTP_USER", cfg.get("SMTP_USER"))
    cfg["SMTP_PASS"] = os.getenv("SMTP_PASS", cfg.get("SMTP_PASS"))
    cfg["SMTP_FROM"] = os.getenv("SMTP_FROM", cfg.get("SMTP_FROM"))

    # Warn if configuration is incomplete
    if not all([
        cfg.get("SMTP_HOST"),
        cfg.get("SMTP_PORT"),
        cfg.get("SMTP_USER"),
        cfg.get("SMTP_PASS"),
    ]):
        log.warning("SMTP configuration incomplete. Dry-run recommended.")

    return cfg


SMTP_CFG = _load_private_settings()


# ==============================================================================
# NOTIFICATION MESSAGE GENERATION
# ==============================================================================
def create_notification(name: str, date: str, time: str) -> str:
    """Generate a simple formatted appointment reminder message.

    Args:
        name (str): Customer's full name.
        date (str): Appointment date in 'YYYY-MM-DD'.
        time (str): Appointment time in 'HH:MM'.

    Returns:
        str: User-facing reminder text.
    """
    return (
        f"Hello {name}, this is a reminder that your cleaning is scheduled for "
        f"{date} at {time}."
    )


# ==============================================================================
# APPOINTMENT RETRIEVAL (SERVICE LAYER INTEGRATION)
# ==============================================================================
def fetch_appointments() -> List[Dict]:
    """Retrieve upcoming appointment data from the service layer.

    Returns:
        list[dict]: Each dict must contain:
            - name (str)
            - date (str)
            - time (str)
            - email (str)

    Notes:
        - This layer intentionally does not apply business rules. All date-based
          filtering is executed in get_upcoming_appt.
    """
    try:
        from backend.service.get_upcoming_appt import (
            get_appointments_to_notify,
        )  # type: ignore
    except Exception as e:
        log.error("Could not import get_appointments_to_notify: %s", e)
        return []

    try:
        appts = list(get_appointments_to_notify())
        # Basic schema validation
        for idx, appt in enumerate(appts):
            for key in ("name", "date", "time", "email"):
                if key not in appt:
                    log.warning(
                        "Appointment[%s] missing key '%s': %s", idx, key, appt
                    )
        return appts
    except Exception as e:
        log.error("Failed to fetch appointments: %s", e)
        log.debug("Traceback:\n%s", traceback.format_exc())
        return []


# ==============================================================================
# SMTP DELIVERY ENGINE
# ==============================================================================
def _open_smtp(host: str, port: int) -> smtplib.SMTP:
    """Open a secure SMTP connection using SSL or STARTTLS.

    Args:
        host (str): SMTP host URL or IP.
        port (int): SMTP port (465 = SSL, other common ports = STARTTLS).

    Returns:
        smtplib.SMTP: Connected SMTP object.
    """
    timeout = 30

    if port == 465:
        return smtplib.SMTP_SSL(host, port, timeout=timeout)

    server = smtplib.SMTP(host, port, timeout=timeout)
    server.ehlo()
    server.starttls()
    server.ehlo()
    return server


def send_notification(notification: str, email: str, *, dry_run: bool = True) -> bool:
    """Send or simulate sending an email notification.

    Args:
        notification (str): Email body content.
        email (str): Recipient email address.
        dry_run (bool): If True, no email is actually sent.

    Returns:
        bool: True if successfully delivered or simulated, False on failure.
    """
    if not email:
        log.error("Skipping send: missing recipient email. Message: %s", notification)
        return False

    # Mirror all messages to terminal
    if dry_run:
        print(f"[DRY_RUN] Would send to {email}: {notification}")
        return True

    msg = EmailMessage()
    msg["From"] = SMTP_CFG.get("SMTP_FROM") or SMTP_CFG.get("SMTP_USER")
    msg["To"] = email
    msg["Subject"] = "Cleaning Appointment Reminder"
    msg.set_content(notification)

    try:
        with _open_smtp(SMTP_CFG["SMTP_HOST"], SMTP_CFG["SMTP_PORT"]) as s:
            s.login(SMTP_CFG["SMTP_USER"], SMTP_CFG["SMTP_PASS"])
            s.send_message(msg)
        print(f"Sent to {email}")
        return True
    except (smtplib.SMTPException, socket.timeout, OSError) as e:
        print(f"FAILED to send to {email}: {e}")
        log.debug("Traceback:\n%s", traceback.format_exc())
        return False


# ==============================================================================
# NOTIFICATION PROCESSOR
# ==============================================================================
def process_notifications(
    *, dry_run: bool = True, limit: Optional[int] = None, preview: bool = False
) -> int:
    """Fetch, prepare, and dispatch appointment reminder notifications.

    Args:
        dry_run (bool): If True, output is only printed to terminal.
        limit (int | None): Maximum number of appointments to process.
        preview (bool): If True, raw appointment objects are printed first.

    Returns:
        int: Number of successfully processed notification attempts.
    """
    appointments = fetch_appointments()
    print(f"Found {len(appointments)} appointments to notify.")

    if preview:
        for appt in appointments[: limit or len(appointments)]:
            print("Appointment data:", appt)

    successes = 0
    processed = 0

    for appt in appointments:
        if limit is not None and processed >= limit:
            break
        processed += 1

        try:
            msg = create_notification(appt["name"], appt["date"], appt["time"])
            if send_notification(msg, appt["email"], dry_run=dry_run):
                successes += 1
        except KeyError as missing:
            print(f"FAILED (missing field {missing}): {appt}")
        except Exception as e:
            print(f"FAILED (unexpected error): {appt}\n{e}")
            log.debug("Traceback:\n%s", traceback.format_exc())

    print(f"Done. Success: {successes}/{processed}")
    return successes


# ==============================================================================
# CLI ENTRYPOINT
# ==============================================================================
def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments for CLI-based notification execution.

    Returns:
        argparse.Namespace: Parsed flags.
    """
    parser = argparse.ArgumentParser(
        description="Data Cleaners - Notification System (email + terminal)"
    )

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--send", action="store_true", help="Send real emails.")
    mode.add_argument("--dry-run", action="store_true", help="Simulate send (default).")

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of notifications processed.",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview raw appointment data before sending.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    dry_mode = not args.send
    process_notifications(
        dry_run=dry_mode,
        limit=args.limit,
        preview=args.preview,
    )
