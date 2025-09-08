import streamlit as st
from openai import OpenAI
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from twilio.rest import Client

# 🔑 OpenAI Setup
client = OpenAI(api_key="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")  # apna key daalo

# 🔑 Google Sheet Setup
SHEET_NAME = "LeadsDatabase"  # apna Google Sheet ka naam
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("client_secret.json", scope)
gs_client = gspread.authorize(creds)
sheet = gs_client.open(SHEET_NAME).sheet1

# 🔑 Twilio WhatsApp Setup
TWILIO_SID = "ACe17f62d7a4d1e777283a8b396584f18e"
TWILIO_AUTH_TOKEN = "a875a8692b185d5179d659260a5c8271"
FROM_WHATSAPP = "whatsapp:+14155238886"   # Twilio sandbox
TO_WHATSAPP = "whatsapp:+917044215131"   # Tumhara number
twilio_client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# Streamlit UI
st.set_page_config(page_title="AI Sales Chatbot", page_icon="🤖", layout="centered")

st.title("🤖 AI Sales Assistant")
st.write("Choose a quick question or type your own message below.")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Predefined Quick Replies ---
st.subheader("💡 Quick Questions")
predefined_msgs = [
    "Tell me about your company",
    "What services do you provide?",
    "How can I contact support?"
]

cols = st.columns(len(predefined_msgs))
for i, msg in enumerate(predefined_msgs):
    if cols[i].button(msg):
        st.session_state.chat_history.append(("You", msg))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": msg}]
        )
        bot_reply = response.choices[0].message.content
        st.session_state.chat_history.append(("Bot", bot_reply))

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
            # Save to Google Sheet
            sheet.append_row([name, email, phone, interest, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

            # Send WhatsApp notification
            twilio_client.messages.create(
                from_=FROM_WHATSAPP,
                body=f"📌 New lead received!\nName: {name}\nEmail: {email}\nPhone: {phone}\nInterest: {interest}",
                to=TO_WHATSAPP
            )

            # Chatbot Confirmation
            st.session_state.chat_history.append(("Bot", "✅ Thank you! Your details are saved. Our team will contact you soon."))
            st.success("✅ Lead submitted successfully!")
