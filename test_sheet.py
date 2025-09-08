import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Step 1: Auth Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

# Step 2: Open Google Sheet (apna Sheet URL daalo yaha)
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1SK7LEfRY9mtbex-MghJ6EN6PwJI8bT4OknCWAEWVHTo/edit?gid=0#gid=0").sheet1

# Step 3: Test Entry
sheet.append_row([
    "Rahul Yadav",
    "rahul@example.com",
    "9876543210",
    "AI Sales Agent Demo",
    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
])

print("✅ Data inserted into Google Sheet successfully!")
