import json
import os
import smtplib
from email.message import EmailMessage


def notifcation(message: bytes) -> None | str:
    try:
        msg = json.loads(message)
        mp3_fid = msg["mp3_fid"]
        sender_address = os.environ.get("GMAIL_ADDRESS")
        assert sender_address
        sender_password = os.environ.get("GMAIL_PASSWORD")
        assert sender_password
        receiver_address = msg["username"]

        email_msg = EmailMessage()
        email_msg.set_content(f"mp3 file_id: {mp3_fid} is now ready to be downloaded")
        email_msg["Subject"] = "MP3 Download"
        email_msg["From"] = sender_address
        email_msg["To"] = receiver_address

        session = smtplib.SMTP("smtmp.gmail.com")
        session.starttls()
        session.login(sender_address, sender_password)
        session.send_message(email_msg, sender_address, receiver_address)
        session.quit()

    except Exception as e:
        print(e)
        return str(e)

    return None
