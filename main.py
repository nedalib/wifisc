import os
import subprocess
import time
import smtplib
from email.mime.text import MIMEText
from plyer import notification
import logging
from pymongo import MongoClient

logging.basicConfig(filename='wifi_monitor.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

MONGO_URI = "mongodb://localhost:27017" 
DB_NAME = "wifi_monitor"
COLLECTION_NAME = "offline_events"

SMTP_SERVER = "example.example.com"  
SMTP_PORT = 587  
SENDER_EMAIL = "sender@example.com"
SENDER_PASSWORD = "password" 
RECIPIENT_EMAIL = "recipient@example.com" 


def check_wifi_status(target_ip):
    try:
        response = subprocess.run(["ping", "-c", "1", target_ip], capture_output=True, text=True)
        return response.returncode == 0
    except Exception as e:
        logging.error(f"Error occurred while checking Wi-Fi status: {e}")
        return False


def send_notification():
    title = "Wi-Fi Offline"
    message = "Your Spectrum Wi-Fi connection is offline."
    notification.notify(title=title, message=message, timeout=10)


def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        logging.info("Email notification sent")
    except Exception as e:
        logging.error(f"Error occurred while sending email notification: {e}")


def save_offline_event(target_ip):
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        event = {"timestamp": time.time(), "target_ip": target_ip}
        collection.insert_one(event)
        client.close()
    except Exception as e:
        logging.error(f"Error occurred while saving offline event: {e}")


def main(target_ip):
    while True:
        try:
            if not check_wifi_status(target_ip):
                send_notification()
                save_offline_event(target_ip)
                send_email("Wi-Fi Offline", "Your Spectrum Wi-Fi connection is offline.")
            time.sleep(60) 
        except KeyboardInterrupt:
            logging.info("Wi-Fi monitoring stopped")
            break
        except Exception as e:
            logging.error(f"Error occurred in main loop: {e}")


if __name__ == "__main__":
    target_ip = input("Enter the IP address of the router: ")
    logging.info("Wi-Fi monitoring started")
    main(target_ip)