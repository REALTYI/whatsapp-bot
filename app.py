from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def send_interactive_message(response, options):
    """
    Send an interactive message with multiple choice options
    :param response: MessagingResponse object
    :param options: List of options to display
    """
    msg = response.message()
    msg.body("Please select an option:")
    
    # Create numbered options
    for i, option in enumerate(options, 1):
        msg.body(f"{i}. {option}")
    
    return str(response)

@app.route("/", methods=["GET", "POST"])
def root():
    logger.info("Received request at root URL")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"Request values: {dict(request.values)}")
    
    # Handle POST requests (from Twilio)
    if request.method == "POST":
        return whatsapp()
    
    # Handle GET requests
    return "WhatsApp Bot is running! (Auto-deploy test)"

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    # Log all request data
    logger.info("Received WhatsApp request")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"Request values: {dict(request.values)}")
    
    # Get the message details
    incoming_msg = request.values.get("Body", "").lower()
    from_number = request.values.get("From", "")
    logger.info(f"Message from: {from_number}")
    logger.info(f"Incoming message: {incoming_msg}")

    response = MessagingResponse()

    # Bot Responses with interactive options
    if "hello" in incoming_msg:
        msg = response.message()
        msg.body("Hey there! 👋 Welcome to RealtyBot. How can I assist you today?")
        # Add interactive options
        msg.body("\nPlease select an option:")
        msg.body("1. View Properties")
        msg.body("2. Schedule a Visit")
        msg.body("3. Contact an Agent")
        msg.body("4. Get Price Range")
    elif "property" in incoming_msg or "1" in incoming_msg:
        msg = response.message()
        msg.body("We have several properties available. Please select your preferred type:")
        msg.body("\n1. Apartments")
        msg.body("2. Houses")
        msg.body("3. Villas")
        msg.body("4. Commercial")
    elif "visit" in incoming_msg or "2" in incoming_msg:
        msg = response.message()
        msg.body("Please select your preferred visit time:")
        msg.body("\n1. Morning (9 AM - 12 PM)")
        msg.body("2. Afternoon (1 PM - 4 PM)")
        msg.body("3. Evening (5 PM - 8 PM)")
    elif "agent" in incoming_msg or "3" in incoming_msg:
        msg = response.message()
        msg.body("Connecting you to an agent... Please wait.")
        # Here you could integrate with your agent assignment system
    elif "price" in incoming_msg or "4" in incoming_msg:
        msg = response.message()
        msg.body("Please select your budget range:")
        msg.body("\n1. Under ₹50 Lakhs")
        msg.body("2. ₹50 Lakhs - ₹1 Crore")
        msg.body("3. ₹1 Crore - ₹2 Crores")
        msg.body("4. Above ₹2 Crores")
    else:
        msg = response.message()
        msg.body("Sorry, I didn't understand that. Try 'hello' to see available options.")

    # Log the response
    logger.info(f"Sending response: {msg.body}")
    return str(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
