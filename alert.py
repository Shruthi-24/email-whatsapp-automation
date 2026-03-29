import imaplib
import email
import pyautogui
import pywhatkit
import time
from transformers import pipeline

# Initialize summarizer
summarizer = pipeline("summarization", model="t5-base")

# Function to summarize content
def summarize(content):
    summary = summarizer(content, max_length=20, min_length=10, do_sample=False)
    return summary[0]['summary_text']

# Function to fetch unread emails
def fetch_all_unread_emails(username, password):
    mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
    mail.login(username, password)
    mail.select('inbox')

    result, data = mail.search(None, 'UNSEEN')
    email_details_list = []

    if data[0]:
        for num in data[0].split():
            result, message_data = mail.fetch(num, '(RFC822)')

            try:
                raw_email = message_data[0][1].decode("utf-8")
            except UnicodeDecodeError:
                raw_email = message_data[0][1].decode("latin1")

            email_message = email.message_from_string(raw_email)

            sender = email.utils.parseaddr(email_message['From'])[1]
            subject = email_message['Subject']

            date_received = email.utils.parsedate(email_message['Date'])
            formatted_date_time = time.strftime("%Y-%m-%d %H:%M:%S", date_received)

            # Extract message content
            message_content = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        message_content = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        break
            else:
                message_content = email_message.get_payload(decode=True).decode("utf-8", errors="ignore")

            # Summarize
            summary = summarize(message_content)

            email_details = f"""Sender: {sender}
Subject: {subject}
Date Received: {formatted_date_time}

Summary:
{summary}

Link: https://mail.google.com/mail/u/0/#inbox
"""
            email_details_list.append(email_details)

            # Mark as unread again
            mail.store(num, '-FLAGS', '(\\Seen)')

    mail.close()
    mail.logout()

    return email_details_list


# MAIN EXECUTION
if __name__ == "__main__":
    username = "your_email@gmail.com"
    password = "your_password"

    email_details_list = fetch_all_unread_emails(username, password)

    if email_details_list:
        phone_number = "+91XXXXXXXXXX"

        consolidated_message = '\n\n'.join(email_details_list)

        try:
            # Send WhatsApp message
            pywhatkit.sendwhatmsg_instantly(phone_number, consolidated_message)

            time.sleep(5)  # wait for WhatsApp Web

            # Press Enter to send
            pyautogui.press('enter')

            print("Message sent successfully.")

        except Exception as e:
            print(f"Error: {e}")
    else:
        print("No unread emails to send.")