import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# SMTP Configuration (to be set in .env)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", SMTP_USER)

def send_custom_email(receiver_email: str, subject: str, html_body: str):
    if not SMTP_USER or not SMTP_PASS:
        print(f"WARNING: SMTP credentials not set. MOCK EMAIL SENT TO {receiver_email}: {subject}")
        return True

    try:
        msg = MIMEMultipart()
        msg['From'] = f"Lexora Platform <{SENDER_EMAIL}>"
        msg['To'] = receiver_email
        msg['Subject'] = subject

        msg.attach(MIMEText(html_body, 'html'))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        
        print(f"Email successfully sent to {receiver_email}")
        return True
    except Exception as e:
        print(f"Failed to send email to {receiver_email}: {e}")
        return False

def send_otp_email(receiver_email: str, otp_code: str):
    body = f"""
    <html>
    <body style="font-family: sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e1e1e1; border-radius: 10px;">
            <h2 style="color: #7b61ff; text-align: center;">Welcome to Lexora</h2>
            <p>Hello,</p>
            <p>To complete your registration, please use the following verification code:</p>
            <div style="text-align: center; margin: 30px 0;">
                <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #101114; background: #f6f7fb; padding: 10px 20px; border-radius: 8px;">
                    {otp_code}
                </span>
            </div>
            <p>This code will expire in 15 minutes.</p>
            <p>If you didn't request this code, you can safely ignore this email.</p>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="font-size: 12px; color: #777; text-align: center;">
                &copy; 2026 Lexora. All rights reserved.
            </p>
        </div>
    </body>
    </html>
    """
    return send_custom_email(receiver_email, f"{otp_code} is your Lexora verification code", body)


def send_password_reset_email(receiver_email: str, reset_link: str):
    body = f"""
    <html>
    <body style="font-family: sans-serif; line-height: 1.6; color: #333; background:#f6f7fb; margin:0; padding:20px;">
        <div style="max-width: 520px; margin: 0 auto; background:#fff; padding: 36px 40px; border: 1px solid #e5e7eb; border-radius: 16px;">
            <div style="text-align:center; margin-bottom:24px;">
                <span style="font-size:1.8rem; font-weight:700; color:#101114; letter-spacing:-0.03em;">Lex<span style="color:#7b61ff">ora</span></span>
            </div>
            <h2 style="font-size:1.2rem; font-weight:700; color:#101114; margin:0 0 8px;">Reset your password</h2>
            <p style="color:#6b6f7a; font-size:.9rem; margin:0 0 24px;">We received a request to reset the password for your Lexora account. Click the button below to choose a new password.</p>
            <div style="text-align: center; margin: 28px 0;">
                <a href="{reset_link}" style="display:inline-block; background:#7b61ff; color:#fff; text-decoration:none; font-weight:700; font-size:.95rem; padding:14px 36px; border-radius:999px;">
                    Reset Password
                </a>
            </div>
            <p style="color:#6b6f7a; font-size:.82rem; text-align:center;">This link expires in <strong>30 minutes</strong>.</p>
            <p style="color:#6b6f7a; font-size:.82rem; text-align:center;">If you didn't request a password reset, you can safely ignore this email.</p>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 24px 0;">
            <p style="font-size: 11px; color: #aaa; text-align: center;">&copy; 2026 Lexora. All rights reserved.</p>
        </div>
    </body>
    </html>
    """
    return send_custom_email(receiver_email, "Reset your Lexora password", body)
