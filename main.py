import imaplib
import email
import re
import requests
import time
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('APP_PASSWORD') # google APP password
IMAP_SERVER = "imap.gmail.com"

def check_for_new_emails():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")

    status, messages = mail.search(None, '(UNSEEN FROM "dnsadmin@afraid.org")')

    if not messages[0]:
        print("No unread emails from dnsadmin@afraid.org.")
        mail.logout()
        return

    email_ids = messages[0].split()
    latest_email_id = email_ids[-1]

    status, msg_data = mail.fetch(latest_email_id, "(RFC822)")
    msg = email.message_from_bytes(msg_data[0][1])
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode()
                break
    else:
        body = msg.get_payload(decode=True).decode()

    match = re.search(r"https?://\S+", body)
    if match:
        first_link = match.group()
        print("Requesting:", first_link)
        response = requests.get(first_link)
        print("Response Status:", response.status_code)
        
        mail.store(latest_email_id, '+FLAGS', '\\Seen')
        print("Email marked as read!")
    else:
        print("no link found in the email.")

    mail.logout()

def main():
    while True:
        check_for_new_emails()
        print("Waiting 60 seconds before checking again...")
        time.sleep(60)  # Cooldown time (60 sec)

if __name__ == "__main__":
    main()
