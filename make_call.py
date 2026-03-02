import os
from twilio.rest import Client

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
api_key = os.environ["TWILIO_API_KEY"]
api_secret = os.environ["TWILIO_API_SECRET"]

VOICE_URL = "https://2620-2401-4900-1cd7-4005-517a-bb2d-97f3-eec1.ngrok-free.app/voice"

client = Client(api_key, api_secret, account_sid)

call = client.calls.create(
    url=VOICE_URL,
    method="POST",
    to="+919821294499",
    from_="+15079365391",
)

print("Call SID:", call.sid)