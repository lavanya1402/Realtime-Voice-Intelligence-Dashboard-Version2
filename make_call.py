import os
from twilio.rest import Client

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
api_key = os.environ["TWILIO_API_KEY"]
api_secret = os.environ["TWILIO_API_SECRET"]

VOICE_URL = f"https://{os.environ['NGROK_DOMAIN']}/voice"

client = Client(api_key, api_secret, account_sid)

call = client.calls.create(
    url=VOICE_URL,
    method="POST",
    to=os.environ["TO_NUMBER"],
    from_=os.environ["FROM_NUMBER"],
)

print("Call SID:", call.sid)