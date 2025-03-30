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
        msg.body("Hey there! 👋 Welcome to RealtyBot. I'm here to help you find your dream property! 🏡")
        msg.body("\nJust let me know what you're looking for, and I'll do the rest!")
        msg.body("\nOptions:")
        msg.body("1. Buy a Property 🏡")
        msg.body("2. Rent a Property 🏢")
        msg.body("3. Schedule a Visit 📅")
        msg.body("4. Talk to an Agent 💬")
        msg.body("\nType 'help' for assistance or 'back' to return to previous menu.")
    elif "buy" in incoming_msg or "1" in incoming_msg:
        msg.body("Great! Let's find the perfect place for you. First, tell me your preferred location:")
        msg.body("\n1. Mumbai 🏙️")
        msg.body("2. Delhi 🏛️")
        msg.body("3. Bangalore 🌆")
        msg.body("4. Chennai 🏘️")
        msg.body("\nType your choice or 'back' to return to main menu.")
    elif "rent" in incoming_msg or "2" in incoming_msg:
        msg.body("Perfect! Let's find your ideal rental property. What's your preferred location?")
        msg.body("\n1. Mumbai 🏙️")
        msg.body("2. Delhi 🏛️")
        msg.body("3. Bangalore 🌆")
        msg.body("4. Chennai 🏘️")
        msg.body("\nType your choice or 'back' to return to main menu.")
    elif "mumbai" in incoming_msg or "1" in incoming_msg:
        msg.body("Got it! What's your budget range? 💰")
        msg.body("\n1. Under ₹50 Lakhs")
        msg.body("2. ₹50 Lakhs - ₹1 Crore")
        msg.body("3. ₹1 Crore - ₹2 Crores")
        msg.body("4. Above ₹2 Crores")
        msg.body("\nType your choice or 'back' to return to previous menu.")
    elif "50" in incoming_msg or "1" in incoming_msg:
        msg.body("Nice! What kind of property are you looking for? 🏠")
        msg.body("\n1. 1 BHK 🛏️")
        msg.body("2. 2 BHK 🛏️")
        msg.body("3. 3 BHK 🛏️")
        msg.body("\nType your choice or 'back' to return to previous menu.")
    elif "1 bhk" in incoming_msg or "1" in incoming_msg:
        msg.body("Here are some top picks for you! 🎯")
        msg.body("\n1. 1 BHK - ₹45 lakh - Andheri East [View Photos 📷]")
        msg.body("2. 1 BHK - ₹48 lakh - Malad [View Photos 📷]")
        msg.body("3. 1 BHK - ₹42 lakh - Borivali [View Photos 📷]")
        msg.body("\nEach property includes:")
        msg.body("• Modern amenities 🏗️")
        msg.body("• Security system 🔒")
        msg.body("• Parking space 🚗")
        msg.body("\nWant more details about any of these? Just reply with the number!")
        msg.body("\nType 'back' to return to previous menu or 'help' for assistance.")
    elif "2 bhk" in incoming_msg or "2" in incoming_msg:
        msg.body("Here are some amazing 2 BHK options for you! 🎯")
        msg.body("\n1. 2 BHK - ₹65 lakh - Andheri East [View Photos 📷]")
        msg.body("2. 2 BHK - ₹68 lakh - Borivali [View Photos 📷]")
        msg.body("3. 2 BHK - ₹62 lakh - Malad [View Photos 📷]")
        msg.body("\nEach property includes:")
        msg.body("• Modern amenities 🏗️")
        msg.body("• Security system 🔒")
        msg.body("• Parking space 🚗")
        msg.body("\nWant more details about any of these? Just reply with the number!")
        msg.body("\nType 'back' to return to previous menu or 'help' for assistance.")
    elif "3 bhk" in incoming_msg or "3" in incoming_msg:
        msg.body("Here are some premium 3 BHK options for you! 🎯")
        msg.body("\n1. 3 BHK - ₹85 lakh - Andheri East [View Photos 📷]")
        msg.body("2. 3 BHK - ₹88 lakh - Borivali [View Photos 📷]")
        msg.body("3. 3 BHK - ₹82 lakh - Malad [View Photos 📷]")
        msg.body("\nEach property includes:")
        msg.body("• Modern amenities 🏗️")
        msg.body("• Security system 🔒")
        msg.body("• Parking space 🚗")
        msg.body("\nWant more details about any of these? Just reply with the number!")
        msg.body("\nType 'back' to return to previous menu or 'help' for assistance.")
    # Handle property selection responses
    elif incoming_msg in ["1", "2", "3"]:
        msg.body("Here's a sneak peek of the property! 😍")
        msg.body("\n[Property Images]")
        msg.body("\nWould you like a virtual tour video as well? (Yes/No)")
        msg.body("\nType 'yes' to view the virtual tour or 'no' to proceed with visit scheduling.")
    elif "yes" in incoming_msg:
        msg.body("Here's the virtual tour of the property! 🎥")
        msg.body("\n[Virtual Tour Video]")
        msg.body("\nImpressed? Let's schedule a visit! 📅")
        msg.body("\nPick a time slot:")
        msg.body("1. Morning (9 AM - 12 PM) 🌅")
        msg.body("2. Afternoon (1 PM - 4 PM) ☀️")
        msg.body("3. Evening (5 PM - 8 PM) 🌙")
        msg.body("\nType your choice or 'back' to return to previous menu.")
    elif "no" in incoming_msg:
        msg.body("Let's schedule a visit to see the property in person! 📅")
        msg.body("\nPick a time slot:")
        msg.body("1. Morning (9 AM - 12 PM) 🌅")
        msg.body("2. Afternoon (1 PM - 4 PM) ☀️")
        msg.body("3. Evening (5 PM - 8 PM) 🌙")
        msg.body("\nType your choice or 'back' to return to previous menu.")
    elif "afternoon" in incoming_msg or "2" in incoming_msg:
        msg.body("Got it! Your visit is scheduled for tomorrow at 2 PM. ⏰")
        msg.body("\nYou'll receive a reminder beforehand!")
        msg.body("\nThanks for booking a visit! Could I have your name and contact number for confirmation?")
        msg.body("\nPlease reply with your name and number.")
    elif "morning" in incoming_msg or "1" in incoming_msg:
        msg.body("Got it! Your visit is scheduled for tomorrow at 10 AM. ⏰")
        msg.body("\nYou'll receive a reminder beforehand!")
        msg.body("\nThanks for booking a visit! Could I have your name and contact number for confirmation?")
        msg.body("\nPlease reply with your name and number.")
    elif "evening" in incoming_msg or "3" in incoming_msg:
        msg.body("Got it! Your visit is scheduled for tomorrow at 5 PM. ⏰")
        msg.body("\nYou'll receive a reminder beforehand!")
        msg.body("\nThanks for booking a visit! Could I have your name and contact number for confirmation?")
        msg.body("\nPlease reply with your name and number.")
    elif "agent" in incoming_msg or "4" in incoming_msg:
        msg.body("Connecting you to an agent... Please wait. 💬")
        msg.body("\nOur agent will contact you shortly.")
        msg.body("\nIn the meantime, you can:")
        msg.body("1. Browse more properties 🏠")
        msg.body("2. Schedule a visit 📅")
        msg.body("3. Return to main menu 🔄")
        msg.body("\nType your choice or 'back' to return to main menu.")
    elif "help" in incoming_msg:
        msg.body("I'm here to help! Here are some commands you can use:")
        msg.body("\n• 'hello' - Start over 🔄")
        msg.body("• 'back' - Return to previous menu ⬅️")
        msg.body("• 'details' - Get more information ℹ️")
        msg.body("• 'help' - Show this help message ❓")
        msg.body("\nYou can also select options by typing their numbers (1-4)")
    elif "back" in incoming_msg:
        msg.body("Returning to main menu. How can I assist you today? 🔄")
        msg.body("\n1. Buy a Property 🏡")
        msg.body("2. Rent a Property 🏢")
        msg.body("3. Schedule a Visit 📅")
        msg.body("4. Talk to an Agent 💬")
        msg.body("\nType 'help' for assistance.")
    else:
        msg.body("Sorry, I didn't understand that. Try 'hello' to see available options or 'help' for assistance. 🤔")

    # Log the response
    logger.info(f"Sending response: {msg.body}")
    return str(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
