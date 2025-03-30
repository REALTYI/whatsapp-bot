from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    incoming_msg = request.values.get("Body", "").lower()
    response = MessagingResponse()
    msg = response.message()

    # Bot Responses
    if "hello" in incoming_msg:
        msg.body("Hey there! 👋 Welcome to RealtyBot. How can I assist you today?")
    elif "property" in incoming_msg:
        msg.body("We have several properties available. Please specify your budget and location.")
    elif "visit" in incoming_msg:
        msg.body("Sure! Please share your preferred date and time for the visit.")
    elif "agent" in incoming_msg:
        msg.body("Connecting you to an agent... Please wait.")
    else:
        msg.body("Sorry, I didn't understand that. Try 'hello', 'property', or 'visit'.")

    return str(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
