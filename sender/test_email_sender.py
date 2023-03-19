import unittest
from unittest.mock import MagicMock, patch
from smtp import EmailSender

class TestEmailSender(unittest.TestCase):

    @patch("smtplib.SMTP")
    def test_send_email_without_attachments(self, mock_smtp):
        smtp_instance = mock_smtp.return_value

        with EmailSender("smtp.example.com", 587, "user@example.com", "password") as email_sender:
            msg = email_sender.create_message(
                "Test subject", "Test body", "plain",
                "user@example.com", ["recipient@example.com"]
            )
            email_sender.send_email(msg)

        smtp_instance.sendmail.assert_called_once_with(
            "user@example.com",
            ["recipient@example.com"],
            msg.as_string()
        )

    @patch("smtplib.SMTP")
    def test_send_email_with_attachments(self, mock_smtp):
        smtp_instance = mock_smtp.return_value
        base64_attachments = [
            ("file.txt", "c29tZSB0ZXh0IGZpbGU="),
            ("image.jpg", "c29tZSBpbWFnZSBmaWxl")
        ]

        with EmailSender("smtp.example.com", 587, "user@example.com", "password") as email_sender:
            msg = email_sender.create_message(
                "Test subject", "Test body", "plain",
                "user@example.com", ["recipient@example.com"]
            )
            email_sender.send_email(msg, base64_attachments=base64_attachments)

        smtp_instance.sendmail.assert_called_once()
        sent_msg = smtp_instance.sendmail.call_args[0][2]
        self.assertIn("c29tZSB0ZXh0IGZpbGU=", sent_msg)
        self.assertIn("c29tZSBpbWFnZSBmaWxl", sent_msg)

if __name__ == "__main__":
    unittest.main()
