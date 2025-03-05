from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from src.config import Config

mail_config = ConnectionConfig(
    MAIL_USERNAME=Config.MAIL_USERNAME,
    MAIL_PASSWORD=Config.MAIL_PASSWORD,
    MAIL_FROM=Config.MAIL_FROM,
    MAIL_PORT=Config.MAIL_PORT,
    MAIL_SERVER=Config.MAIL_SERVER,
    MAIL_FROM_NAME=Config.MAIL_FROM_NAME,
    MAIL_STARTTLS=False,  # True if Email server support TTLS connection
    MAIL_SSL_TLS=False,
)

mail = FastMail(config=mail_config)


def create_message(recipients: list[str], subject: str, body: str) -> MessageSchema:
    message = MessageSchema(
        recipients=recipients, subject=subject, body=body, subtype=MessageType.html
    )
    return message
