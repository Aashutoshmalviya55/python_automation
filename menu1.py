import streamlit as st
import os
from dotenv import load_dotenv
import smtplib
import requests
from twilio.rest import Client
import pywhatkit
import datetime
import time
import paramiko
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Twilio setup
account_sid = os.getenv("ACCOUNT_SID")
auth_token = os.getenv("AUTH_TOKEN")
twilio_phone_number = os.getenv("TWILIO_PHONE")
twilio_client = Client(account_sid, auth_token)

# Email setup
email_password = os.getenv("EMAIL_PASSWORD")

# Telegram
telegram_token = os.getenv("TELEGRAM_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

# Instagram (if using instagrapi)
# from instagrapi import Client as InstaClient
# insta_user = os.getenv("INSTA_USER")
# insta_pass = os.getenv("INSTA_PASS")

# Streamlit layout
st.set_page_config(page_title="Automation Toolkit", layout="wide")
st.sidebar.title("📚 Tools Menu")
tool = st.sidebar.radio("Select a Tool", ["Send SMS", "WhatsApp", "Email", "Telegram", "Linux Remote SSH", "Twilio Call"])

st.title("🛠️ Multi-Tool Python Automation App")

# ----------- 1. Twilio SMS -----------
if tool == "Send SMS":
    st.header("📱 Send SMS via Twilio")
    phone = st.text_input("Recipient Phone Number (e.g. +91...)")
    message = st.text_area("Message")
    if st.button("Send SMS"):
        try:
            msg = twilio_client.messages.create(body=message, from_=twilio_phone_number, to=phone)
            st.success(f"✅ SMS sent! SID: {msg.sid}")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ----------- 2. WhatsApp -------------
elif tool == "WhatsApp":
    st.header("💬 Send WhatsApp Message or Image")
    phone = st.text_input("WhatsApp Number (+countrycode)")
    message = st.text_area("Message")
    image = st.file_uploader("Upload Image", type=["jpg", "png"])

    if st.button("Send Text Message"):
        now = datetime.datetime.now()
        pywhatkit.sendwhatmsg(phone, message, now.hour, now.minute + 1)
        st.success("✅ Message scheduled! Leave browser open.")

    if st.button("Send Image"):
        if image:
            with open("temp_img.jpg", "wb") as f:
                f.write(image.getbuffer())
            pywhatkit.sendwhats_image(phone, "temp_img.jpg", caption=message)
            st.success("✅ Image sent!")

# ----------- 3. Email -----------------
elif tool == "Email":
    st.header("📧 Send Email via Gmail")
    sender = st.text_input("Sender Gmail")
    recipient = st.text_input("Recipient Email")
    subject = st.text_input("Subject")
    msg_body = st.text_area("Message")
    if st.button("Send Email"):
        try:
            content = f"Subject: {subject}\n\n{msg_body}"
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender, email_password)
            server.sendmail(sender, recipient, content)
            server.quit()
            st.success("✅ Email sent successfully!")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ----------- 4. Telegram --------------
elif tool == "Telegram":
    st.header("📩 Send Telegram Message")
    telegram_message = st.text_input("Enter your message")
    if st.button("Send to Telegram"):
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage?chat_id={telegram_chat_id}&text={telegram_message}"
        res = requests.get(url)
        if res.status_code == 200:
            st.success("✅ Message sent!")
        else:
            st.error("❌ Failed. Check token/chat ID.")

# ----------- 5. Linux SSH -------------
elif tool == "Linux Remote SSH":
    st.header("💻 Execute Linux Commands Remotely")
    col1, col2, col3 = st.columns(3)
    with col1:
        ssh_user = st.text_input("Username")
    with col2:
        ssh_ip = st.text_input("IP Address")
    with col3:
        ssh_pass = st.text_input("Password", type="password")

    cmd = st.selectbox("Command", [
        "date", "cal", "ls", "ifconfig",
        "adduser", "mkdir", "gedit", "cd / && ls"
    ])
    extra = st.text_input("Extra input (username/folder/file name if needed)")

    if st.button("Run Command"):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ssh_ip, username=ssh_user, password=ssh_pass)

            base_cmds = {
                "date": "date",
                "cal": "cal",
                "ls": "ls",
                "ifconfig": "ifconfig",
                "adduser": f"sudo adduser {extra}",
                "mkdir": f"mkdir {extra}",
                "gedit": f"gedit {extra}",
                "cd / && ls": "cd / && ls"
            }
            stdin, stdout, stderr = ssh.exec_command(base_cmds[cmd])
            output = stdout.read().decode()
            err = stderr.read().decode()
            if output:
                st.success("✅ Output:")
                st.code(output)
            if err:
                st.error("❌ Error:")
                st.code(err)
            ssh.close()
        except Exception as e:
            st.error(f"❌ SSH Error: {e}")

# ----------- 6. Twilio Call -----------
elif tool == "Twilio Call":
    st.header("📞 Make a Phone Call")
    call_number = st.text_input("Phone Number to Call (e.g. +91...)")
    call_message = st.text_area("Message to Speak", "Hello! This is a Python-powered call.")
    if st.button("Make Call"):
        try:
            call = twilio_client.calls.create(
                to=call_number,
                from_=twilio_phone_number,
                twiml=f"<Response><Say>{call_message}</Say></Response>"
            )
            st.success("✅ Call started!")
            st.info(f"Call SID: {call.sid}")
        except Exception as e:
            st.error(f"❌ Error: {e}")
