# backend/mail.py
from flask_mail import Mail, Message

# Initialize mail extension
mail = Mail()

def init_mail(app):
    """Initialize mail with app"""
    mail.init_app(app)

def send_email(subject, recipient, html_body):
    """Send email synchronously (for immediate emails)"""
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient],
            html=html_body
        )
        mail.send(msg)
        return True, "Email sent successfully"
    except Exception as e:
        print(f"Email error: {str(e)}")
        return False, str(e)