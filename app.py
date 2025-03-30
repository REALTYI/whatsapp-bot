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

    # Main menu
    if "hello" in incoming_msg or "hi" in incoming_msg:
        msg.body("Hey there! 👋 Welcome to RealtyBot. I'm here to help you find your dream property! 🏡")
        msg.body("\nJust let me know what you're looking for, and I'll do the rest!")
        msg.body("\nOptions:")
        msg.body("1. Buy a Property 🏡")
        msg.body("2. Rent a Property 🏢")
        msg.body("3. Schedule a Visit 📅")
        msg.body("4. Talk to an Agent 💬")
        msg.body("\nType your choice (1-4) or 'help' for assistance.")
    
    # Buy Property Flow
    elif "buy" in incoming_msg or "1" in incoming_msg:
        msg.body("Great! Let's find the perfect place for you. First, tell me your preferred location:")
        msg.body("\n1. Mumbai 🏙️")
        msg.body("2. Delhi 🏛️")
        msg.body("3. Bangalore 🌆")
        msg.body("4. Chennai 🏘️")
        msg.body("\nType your choice (1-4) or 'back' to return to main menu.")
    
    # Rent Property Flow
    elif "rent" in incoming_msg or "2" in incoming_msg:
        msg.body("Perfect! Let's find your ideal rental property. What's your preferred location?")
        msg.body("\n1. Mumbai 🏙️")
        msg.body("2. Delhi 🏛️")
        msg.body("3. Bangalore 🌆")
        msg.body("4. Chennai 🏘️")
        msg.body("\nType your choice (1-4) or 'back' to return to main menu.")
    
    # Location Selection (Mumbai)
    elif "mumbai" in incoming_msg or "1" in incoming_msg:
        msg.body("Got it! What's your budget range? 💰")
        msg.body("\n1. Under ₹50 Lakhs")
        msg.body("2. ₹50 Lakhs - ₹1 Crore")
        msg.body("3. ₹1 Crore - ₹2 Crores")
        msg.body("4. Above ₹2 Crores")
        msg.body("\nType your choice (1-4) or 'back' to return to previous menu.")
    
    # Budget Selection
    elif "50" in incoming_msg or "1" in incoming_msg:
        msg.body("Nice! What kind of property are you looking for? 🏠")
        msg.body("\n1. 1 BHK 🛏️")
        msg.body("2. 2 BHK 🛏️")
        msg.body("3. 3 BHK 🛏️")
        msg.body("\nType your choice (1-3) or 'back' to return to previous menu.")
    
    # Property Type Selection
    elif "1 bhk" in incoming_msg or "1" in incoming_msg:
        msg.body("Here are some top picks for you! 🎯")
        msg.body("\n1. 1 BHK - ₹45 lakh - Andheri East")
        msg.body("2. 1 BHK - ₹48 lakh - Malad")
        msg.body("3. 1 BHK - ₹42 lakh - Borivali")
        msg.body("\nEach property includes:")
        msg.body("• Modern amenities 🏗️")
        msg.body("• Security system 🔒")
        msg.body("• Parking space 🚗")
        msg.body("\nWant more details about any of these? Just reply with the number!")
        msg.body("\nType 'back' to return to previous menu or 'help' for assistance.")
    
    # Property Selection
    elif incoming_msg in ["1", "2", "3"]:
        msg.body("Great choice! Would you like to schedule a visit to this property? 📅")
        msg.body("\nPick a time slot:")
        msg.body("1. Morning (9 AM - 12 PM) 🌅")
        msg.body("2. Afternoon (1 PM - 4 PM) ☀️")
        msg.body("3. Evening (5 PM - 8 PM) 🌙")
        msg.body("\nType your choice (1-3) or 'back' to return to previous menu.")
    
    # Visit Scheduling
    elif "afternoon" in incoming_msg or "2" in incoming_msg:
        msg.body("Got it! Your visit is scheduled for tomorrow at 2 PM. ⏰")
        msg.body("\nYou'll receive a reminder beforehand!")
        msg.body("\nThanks for booking a visit! Could I have your name and contact number for confirmation?")
        msg.body("\nPlease reply with your name and number.")
    
    # Help Menu
    elif "help" in incoming_msg:
        msg.body("I'm here to help! Here are some commands you can use:")
        msg.body("\n• 'hello' - Start over 🔄")
        msg.body("• 'back' - Return to previous menu ⬅️")
        msg.body("• 'help' - Show this help message ❓")
        msg.body("\nYou can also select options by typing their numbers (1-4)")
    
    # Back to Main Menu
    elif "back" in incoming_msg:
        msg.body("Returning to main menu. How can I assist you today? 🔄")
        msg.body("\n1. Buy a Property 🏡")
        msg.body("2. Rent a Property 🏢")
        msg.body("3. Schedule a Visit 📅")
        msg.body("4. Talk to an Agent 💬")
        msg.body("\nType your choice (1-4) or 'help' for assistance.")
    
    # Default Response
    else:
        msg.body("Sorry, I didn't understand that. Try 'hello' to see available options or 'help' for assistance. 🤔")

    # Log the response
    logger.info(f"Sending response: {msg.body}")
    return str(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
