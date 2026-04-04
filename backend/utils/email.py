"""
Email utilities — uses Flask-Mail with SendGrid SMTP.

Required env vars:
  MAIL_SERVER          smtp.sendgrid.net
  MAIL_PORT            587
  MAIL_USERNAME        apikey
  MAIL_PASSWORD        <sendgrid api key>
  MAIL_DEFAULT_SENDER  noreply@yourdomain.com
"""
import os
from flask_mail import Mail, Message

mail = Mail()


def init_app(app):
    app.config['MAIL_SERVER']          = os.environ.get('MAIL_SERVER', 'smtp.sendgrid.net')
    app.config['MAIL_PORT']            = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS']         = True
    app.config['MAIL_USERNAME']        = os.environ.get('MAIL_USERNAME', 'apikey')
    app.config['MAIL_PASSWORD']        = os.environ.get('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER']  = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@stayeasy.com')
    mail.init_app(app)


def send_booking_confirmation(booking, room, hotel):
    nights = (booking.check_out_date - booking.check_in_date).days
    subject = f"Booking Confirmed — {hotel.name} ({booking.check_in_date})"
    body = f"""
Hi {booking.guest_first_name},

Your booking is confirmed! Here are your details:

  Hotel:      {hotel.name}
  Room:       {room.name}
  Check-in:   {booking.check_in_date} at {hotel.check_in_time}
  Check-out:  {booking.check_out_date} at {hotel.check_out_time}
  Guests:     {booking.num_guests}
  Nights:     {nights}
  Total paid: ${booking.total_price_usd:.2f}

Booking reference: {booking.id[:8].upper()}

We look forward to welcoming you!

— The StayEasy Team
"""
    _send(booking.guest_email, subject, body)


def send_checkin_reminder(booking, room, hotel):
    subject = f"Reminder: Check-in tomorrow at {hotel.name}"
    body = f"""
Hi {booking.guest_first_name},

Just a reminder — your check-in is tomorrow!

  Hotel:     {hotel.name}
  Address:   {hotel.address_line1}, {hotel.city}
  Check-in:  {booking.check_in_date} at {hotel.check_in_time}
  Room:      {room.name}
  Reference: {booking.id[:8].upper()}

Safe travels!

— The StayEasy Team
"""
    _send(booking.guest_email, subject, body)


def send_cancellation_confirmation(booking, hotel):
    subject = f"Booking Cancelled — {hotel.name}"
    body = f"""
Hi {booking.guest_first_name},

Your booking has been cancelled.

  Hotel:     {hotel.name}
  Dates:     {booking.check_in_date} → {booking.check_out_date}
  Reference: {booking.id[:8].upper()}

If you were charged, a refund will appear within 5–10 business days.

— The StayEasy Team
"""
    _send(booking.guest_email, subject, body)


def _send(to: str, subject: str, body: str):
    """Send a plain-text email. Silently no-ops if MAIL_PASSWORD is not set."""
    if not os.environ.get('MAIL_PASSWORD'):
        return
    try:
        msg = Message(subject=subject, recipients=[to], body=body.strip())
        mail.send(msg)
    except Exception as e:
        print(f"[email] Failed to send to {to}: {e}")
