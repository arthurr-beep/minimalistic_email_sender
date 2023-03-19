import smtplib
import base64
import mimetypes
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from functools import wraps

def attach_files_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        msg, file_attachments, base64_attachments = func(*args, **kwargs)
        for file_path in file_attachments:
            with open(file_path, "rb") as f:
                file_data = f.read()
                file_name = file_path.split("/")[-1]
                content_type, encoding = mimetypes.guess_type(file_path)
                if content_type is None or encoding is not None:
                    content_type = "application/octet-stream"
                main_type, sub_type = content_type.split("/", 1)
                attachment = MIMEBase(main_type, sub_type)
                attachment.set_payload(file_data)
                encoders.encode_base64(attachment)
                attachment.add_header("Content-Disposition", f"attachment; filename={file_name}")
                msg.attach(attachment)
        for file_name, base64_content in base64_attachments:
            file_data = base64.b64decode(base64_content)
            content_type, encoding = mimetypes.guess_type(file_name)
            if content_type is None or encoding is not None:
                content_type = "application/octet-stream"
            main_type, sub_type = content_type.split("/", 1)
            attachment = MIMEBase(main_type, sub_type)
            attachment.set_payload(file_data)
            encoders.encode_base64(attachment)
            attachment.add_header("Content-Disposition", f"attachment; filename={file_name}")
            msg.attach(attachment)
        return msg
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
    def attach_files(self, msg, file_attachments, base64_attachments):
        return msg, file_attachments, base64_attachments

    def send_email(self, msg, file_attachments=None, base64_attachments=None):
        msg = self.attach_files(msg, file_attachments or [], base64_attachments or [])
        to_emails = msg["To"].split(", ") + msg.get("Cc", "").split(", ") + msg.get("Bcc", "").split(", ")
        self.smtp.sendmail(msg["From"], to_emails, msg.as_string())

    def attachment_generator(self, file_paths):
        for file_path in file_paths:
            with open(file_path, "rb") as f:
                file_data = f.read()
                file_name = file_path.split("/")[-1]
                yield file_name, base64.b64encode(file_data).decode('utf-8')

