import os
import sys
import time
import hashlib
from urllib.parse import urlparse
import requests
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_website_content(url):
    response = requests.get(url)
    return response.text

def compute_hash(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def send_email_notification(to_email, subject, body):
    from_email = os.environ.get('FROM_EMAIL')
    from_password = os.environ.get('FROM_PASSWORD')

    if not (from_email and from_password):
        print("Email credentials not found. Set environment variables FROM_EMAIL and FROM_PASSWORD.")
        return

    message = MIMEMultipart()
    message['From'] = from_email
    message['To'] = to_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    context = ssl.create_default_context()
    with SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, message.as_string())

def monitor_website(url, check_interval, email=None):
    print(f"Monitoring {url} for changes...")

    last_hash = compute_hash(get_website_content(url))
    domain = urlparse(url).netloc

    while True:
        time.sleep(check_interval)
        current_hash = compute_hash(get_website_content(url))

        if current_hash != last_hash:
            print(f"Content on {domain} has changed!")
            if email:
                send_email_notification(email, f"Website Update: {domain}", f"The content on {domain} has been updated.")
            last_hash = current_hash

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python website_monitor.py <url> <check_interval> [email]")
        sys.exit(1)

    url = sys.argv[1]
    check_interval = int(sys.argv[2])
    email = sys.argv[3] if len(sys.argv) == 4 else None
    monitor_website(url, check_interval, email)

