from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def root():
    if request.method == "POST":
        return whatsapp()
    return "WhatsApp Bot is running!"

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    # Get the message details
    incoming_msg = request.values.get("Body", "").lower()
    from_number = request.values.get("From", "")
    
    response = MessagingResponse()
    msg = response.message()
    
    # Basic response for testing
    msg.body("Hello! This is a fresh start. Please provide your instructions for the new bot.")
    
    return str(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
