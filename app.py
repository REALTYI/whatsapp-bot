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
    msg = response.message()

    # Bot Responses with interactive options
    if "hello" in incoming_msg:
        msg.body("Hey there! 👋 Welcome to RealtyBot. How can I assist you today?")
        msg.body("\nPlease select an option:")
        msg.body("1. View Properties")
        msg.body("2. Schedule a Visit")
        msg.body("3. Contact an Agent")
        msg.body("4. Get Price Range")
        msg.body("\nType 'help' for assistance or 'back' to return to previous menu.")
    elif "property" in incoming_msg or "1" in incoming_msg:
        msg.body("We have several properties available. Please select your preferred type:")
        msg.body("\n1. Apartments")
        msg.body("2. Houses")
        msg.body("3. Villas")
        msg.body("4. Commercial")
        msg.body("\nType 'help' for assistance or 'back' to return to main menu.")
    # Handle property type selections
    elif incoming_msg in ["apartments", "1"]:
        msg.body("Great choice! Here are our available apartments:")
        msg.body("\n1. 2BHK Premium Apartment")
        msg.body("2. 3BHK Luxury Apartment")
        msg.body("3. 1BHK Starter Apartment")
        msg.body("\nEach apartment includes:")
        msg.body("• Modern amenities")
        msg.body("• Security system")
        msg.body("• Parking space")
        msg.body("\nPlease select an option (1-3) or type:")
        msg.body("• 'details' for more information")
        msg.body("• 'back' to return to property types")
        msg.body("• 'help' for assistance")
    elif incoming_msg in ["houses", "2"]:
        msg.body("Here are our available houses:")
        msg.body("\n1. Independent House")
        msg.body("2. Row House")
        msg.body("3. Duplex House")
        msg.body("\nEach house includes:")
        msg.body("• Garden area")
        msg.body("• Security system")
        msg.body("• Garage")
        msg.body("\nPlease select an option (1-3) or type:")
        msg.body("• 'details' for more information")
        msg.body("• 'back' to return to property types")
        msg.body("• 'help' for assistance")
    elif incoming_msg in ["villas", "3"]:
        msg.body("Here are our premium villas:")
        msg.body("\n1. Luxury Villa with Pool")
        msg.body("2. Smart Villa")
        msg.body("3. Beachfront Villa")
        msg.body("\nEach villa includes:")
        msg.body("• Private pool")
        msg.body("• Smart home system")
        msg.body("• Security staff")
        msg.body("\nPlease select an option (1-3) or type:")
        msg.body("• 'details' for more information")
        msg.body("• 'back' to return to property types")
        msg.body("• 'help' for assistance")
    elif incoming_msg in ["commercial", "4"]:
        msg.body("Here are our commercial properties:")
        msg.body("\n1. Office Space")
        msg.body("2. Retail Shop")
        msg.body("3. Warehouse")
        msg.body("\nEach property includes:")
        msg.body("• High-speed internet")
        msg.body("• Security system")
        msg.body("• Parking facility")
        msg.body("\nPlease select an option (1-3) or type:")
        msg.body("• 'details' for more information")
        msg.body("• 'back' to return to property types")
        msg.body("• 'help' for assistance")
    elif "details" in incoming_msg:
        msg.body("Here's what you need to know:")
        msg.body("\n• All properties are ready to move in")
        msg.body("• Flexible payment options available")
        msg.body("• Property insurance included")
        msg.body("• 24/7 maintenance support")
        msg.body("\nWould you like to:")
        msg.body("1. Schedule a visit")
        msg.body("2. Talk to an agent")
        msg.body("3. See more properties")
        msg.body("\nType 'back' to return to previous menu.")
    elif "help" in incoming_msg:
        msg.body("I'm here to help! Here are some commands you can use:")
        msg.body("\n• 'hello' - Start over")
        msg.body("• 'back' - Return to previous menu")
        msg.body("• 'details' - Get more information")
        msg.body("• 'help' - Show this help message")
        msg.body("\nYou can also select options by typing their numbers (1-4)")
    elif "back" in incoming_msg:
        msg.body("Returning to main menu. How can I assist you today?")
        msg.body("\n1. View Properties")
        msg.body("2. Schedule a Visit")
        msg.body("3. Contact an Agent")
        msg.body("4. Get Price Range")
        msg.body("\nType 'help' for assistance.")
    elif "visit" in incoming_msg or "2" in incoming_msg:
        msg.body("Please select your preferred visit time:")
        msg.body("\n1. Morning (9 AM - 12 PM)")
        msg.body("2. Afternoon (1 PM - 4 PM)")
        msg.body("3. Evening (5 PM - 8 PM)")
        msg.body("\nType 'back' to return to main menu.")
    elif "agent" in incoming_msg or "3" in incoming_msg:
        msg.body("Connecting you to an agent... Please wait.")
        msg.body("\nOur agent will contact you shortly.")
        msg.body("In the meantime, you can:")
        msg.body("1. Browse more properties")
        msg.body("2. Schedule a visit")
        msg.body("3. Return to main menu")
    elif "price" in incoming_msg or "4" in incoming_msg:
        msg.body("Please select your budget range:")
        msg.body("\n1. Under ₹50 Lakhs")
        msg.body("2. ₹50 Lakhs - ₹1 Crore")
        msg.body("3. ₹1 Crore - ₹2 Crores")
        msg.body("4. Above ₹2 Crores")
        msg.body("\nType 'back' to return to main menu.")
    else:
        msg.body("Sorry, I didn't understand that. Try 'hello' to see available options or 'help' for assistance.")

    # Log the response
    logger.info(f"Sending response: {msg.body}")
    return str(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
