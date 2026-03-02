from dotenv import load_dotenv
import os

load_dotenv()

print("TWILIO_FROM_NUMBER =", os.getenv("TWILIO_FROM_NUMBER"))
print("TWILIO_TO_NUMBER =", os.getenv("TWILIO_TO_NUMBER"))
print("PUBLIC_BASE_URL =", os.getenv("PUBLIC_BASE_URL"))