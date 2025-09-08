import streamlit as st
from openai import OpenAI
import gspread 
from oauth2client.service_account import ServiceAccountCredentials 
import datetime
from twilio.rest import Client 
import json

# ----------------------------
# 🔑 OpenAI Setup
# ----------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ----------------------------
# 🔑 Google Sheet Setup (via Streamlit Secrets)
# ----------------------------
SHEET_NAME = "LeadsDatabase"  # apna Google Sheet ka naam
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load service account credentials from secrets
service_account_info = json.loads(st.secrets["gcp_service_account_json"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
gs_client = gspread.authorize(creds)
sheet = gs_client.open(SHEET_NAME).sheet1

# ----------------------------
# 🔑 Twilio WhatsApp Setup (via Streamlit Secrets)
# ----------------------------
TWILIO_SID = st.secrets["TWILIO_SID"]
TWILIO_AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
FROM_WHATSAPP = "whatsapp:+14155238886"   # Twilio sandbox
TO_WHATSAPP = st.secrets["TO_WHATSAPP"]   # Tumhara number
twilio_client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="AI Sales Chatbot", page_icon="🤖", layout="centered")

st.title("🤖 Chatbot")
st.write("Yadava's- Born to Fashion")
st.write("Choose a quick question or type your own message below.")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Predefined Quick Replies ---
st.subheader("💡 Quick Questions")
predefined_msgs = {
    "Tell me about your company": "We are Yadava's, a modern lifestyle & fashion brand blending Sanatan culture with Gen-Z aesthetics.",
    "What services do you provide?": "We provide premium streetwear, ethnic fusion wear, AI-powered chatbot solutions, and more.",
    "How can I contact support?": "You can reach our support team at support@yadavas.com or call us at +91-XXXXXXXXXX."
}

cols = st.columns(len(predefined_msgs))
for i, (msg, reply) in enumerate(predefined_msgs.items()):
    if cols[i].button(msg):
        st.session_state.chat_history.append(("You", msg))
        st.session_state.chat_history.append(("Bot", reply))


# --- Free Text Input ---
user_input = st.text_input("💬 Type your message:", key="user_input")
if st.button("Send", key="send_button"):
    if user_input:
        st.session_state.chat_history.append(("You", user_input))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_input}]
        )
        bot_reply = response.choices[0].message.content
        st.session_state.chat_history.append(("Bot", bot_reply))

# --- Display Chat ---
st.subheader("📨 Conversation")
for role, text in st.session_state.chat_history:
    st.write(f"**{role}:** {text}")

# --- Lead Form Section ---
with st.expander("📋 Lead Form (Click to open)"):
    with st.form("lead_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        interest = st.text_area("Your Interest")
        submitted = st.form_submit_button("Submit")

        if submitted:
            errors = []
            
            # ✅ Name validation
            if not name.strip():
                errors.append("⚠️ Name cannot be empty.")

            # ✅ Email validation
            import re
            email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
            if not re.match(email_pattern, email):
                errors.append("⚠️ Please enter a valid email address.")

            # ✅ Phone validation (India specific: 10 digit, starts with 6-9)
            phone_pattern = r"^[6-9]\d{9}$"
            if not re.match(phone_pattern, phone):
                errors.append("⚠️ Please enter a valid 10-digit phone number.")

            # ✅ Final check
            if errors:
                for e in errors:
                    st.error(e)
            else:
                # Save to Google Sheet
                # Lead form submit section
                
             now = datetime.now(ZoneInfo("Asia/Kolkata"))

    # Save to Google Sheet
    sheet.append_row(
        [name, email, phone, interest, timestamp],
        value_input_option='USER_ENTERED'
    )

    # Send WhatsApp notification
    twilio_client.messages.create(
        from_=FROM_WHATSAPP,
        body=f"📌 New lead received!\nName: {name}\nEmail: {email}\nPhone: {phone}\nInterest: {interest}",
        to=TO_WHATSAPP
    )

    # Chatbot Confirmation
    st.session_state.chat_history.append(
        ("Bot", "✅ Thank you! Your details are saved. Our team will contact you soon.")
    )
    st.success("✅ Lead submitted successfully!")
