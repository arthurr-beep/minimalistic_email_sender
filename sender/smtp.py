from email.mime.application import MIMEApplication
import smtplib
import base64
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os
from typing import Optional, List, Tuple

def attach_files_decorator(func):
    def wrapper(self, msg, file_attachments=None, base64_attachments=None):
        file_attachments = file_attachments or []
        base64_attachments = base64_attachments or []

        for file_path in file_attachments:
            with open(file_path, "rb") as f:
                attachment = MIMEBase("application", "octet-stream")
                attachment.set_payload(f.read())
                encoders.encode_base64(attachment)
                attachment.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(file_path)}",
                )
                msg.attach(attachment)

        for filename, base64_data in base64_attachments:
            file_data = base64.b64decode(base64_data)
            attachment = MIMEApplication(
                file_data, _subtype="octet-stream", _encoder=encoders.encode_base64
            )
            attachment.add_header("Content-Disposition", "attachment", filename=filename)
            msg.attach(attachment)

        return func(self, msg)

    return wrapper



class EmailSender:
    def __init__(self, smtp_server, smtp_port, smtp_user, smtp_password, use_tls=True):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.use_tls = use_tls

    def __enter__(self):
        self.smtp = smtplib.SMTP(self.smtp_server, self.smtp_port)
        if self.use_tls:
            self.smtp.starttls()
        self.smtp.login(self.smtp_user, self.smtp_password)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            logging.error(f"An error occurred during the email sending process: {exc_value}")
        self.smtp.quit()

    def create_message(self, subject, body, body_type, from_email, to_emails, cc_emails=None, bcc_emails=None):
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = ", ".join(to_emails)
        msg["Subject"] = subject

        if cc_emails:
            msg["Cc"] = ", ".join(cc_emails)

        msg.attach(MIMEText(body, body_type))

        return msg

    @attach_files_decorator
    def send_email(
            self,
            msg: MIMEMultipart,
            file_attachments: Optional[List[str]] = None,
            base64_attachments: Optional[List[Tuple[str, str]]] = None,
        ):
        recipients = []
        if msg["To"]:
            recipients += msg["To"].split(",")
        if msg["Cc"]:
            recipients += msg["Cc"].split(",")

        self.smtp.sendmail(msg["From"], recipients, msg.as_string())

