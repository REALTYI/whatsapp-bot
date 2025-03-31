import os
import logging
import pickle
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load properties
PROPERTIES = {
    'property1': {
        'name': 'Ocean View Apartment',
        'price': 12000000,
        'location': 'Mumbai',
        'bhk': 3,
        'description': 'Luxurious sea-facing apartment',
        'images': ['https://example.com/image1.jpg', 'https://example.com/image2.jpg']
    }
}

# Session data
sessions = {}

# Helper functions

def format_budget(budget_str):
    try:
        budget = int(budget_str.replace("cr", "0000000").replace("l", "00000").replace(" ", "").replace("₹", "").replace(",", ""))
        return budget
    except ValueError:
        return 0


def send_property_images(response, images):
    try:
        msg = response.message("📸 Property Images:")
        for image_url in images[:10]:
            msg.media(image_url)
        return True
    except Exception as e:
        logger.error(f"Error sending images: {str(e)}")
        return False


@app.route('/whatsapp', methods=['POST'])
def whatsapp_bot():import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Property database (could be extended or loaded from an external source)
PROPERTIES = {
    'property1': {
        'name': 'Ocean View Apartment',
        'price': 12000000,
        'location': 'Bandra, Mumbai',
        'bhk': 3,
        'description': 'Luxurious sea-facing apartment',
        'images': ['https://example.com/image1.jpg', 'https://example.com/image2.jpg']
    }
}

# Session data
sessions = {}

# Helper function to send images
def send_property_images(response, images):
    try:
        msg = response.message("📸 Property Images:")
        for image_url in images[:10]:
            msg.media(image_url)
        return True
    except Exception as e:
        logger.error(f"Error sending images: {str(e)}")
        return False

@app.route('/whatsapp', methods=['POST'])
def whatsapp_bot():
    incoming_msg = request.form.get('Body').strip().lower()
    from_number = request.form.get('From')
    response = MessagingResponse()

    if from_number not in sessions:
        sessions[from_number] = {'step': 'start'}

    current_step = sessions[from_number]['step']
    logger.info(f"Incoming message from {from_number}: {incoming_msg} | Current step: {current_step}")

    # Greeting
    if current_step == 'start':
        response.message("Hi there! 👋 Welcome to Real Estate Bot. How can I help you today? (e.g., 'Looking for a 3BHK')")
        sessions[from_number]['step'] = 'collecting_info'
        return str(response)

    # Collecting user preferences
    if current_step == 'collecting_info':
        if 'bhk' in incoming_msg:
            sessions[from_number]['bhk'] = incoming_msg
            response.message("Great choice! What's your budget range?")
            sessions[from_number]['step'] = 'collecting_budget'
            return str(response)
        response.message("Could you specify the property type? (e.g., '3BHK apartment')")
        return str(response)

    # Collecting budget
    if current_step == 'collecting_budget':
        try:
            budget = int(incoming_msg.replace("₹", "").replace(" ", ""))
            sessions[from_number]['budget'] = budget
            response.message("Got it! Any preferred location?")
            sessions[from_number]['step'] = 'collecting_location'
            return str(response)
        except ValueError:
            response.message("Please enter a valid budget amount.")
            return str(response)

    # Collecting location
    if current_step == 'collecting_location':
        sessions[from_number]['location'] = incoming_msg
        response.message(f"Perfect! Let me show you some options in {incoming_msg} within your budget.")
        # Listing matching properties
        for prop_id, details in PROPERTIES.items():
            response.message(f"🏡 {details['name']}: ₹{details['price']} at {details['location']} ({details['bhk']} BHK)")
        response.message("Reply with the property name for more details.")
        sessions[from_number]['step'] = 'details'
        return str(response)

    # Displaying property details
    for prop_id, details in PROPERTIES.items():
        if incoming_msg == details['name'].lower() and current_step == 'details':
            response.message(f"Property: {details['name']}
Price: ₹{details['price']}
Location: {details['location']}
Description: {details['description']}")
            send_property_images(response, details.get('images', []))
            response.message("Do you want to schedule a visit? (e.g., 'Yes, tomorrow at 4 PM')")
            sessions[from_number]['step'] = 'visit'
            return str(response)

    response.message("Sorry, I didn't get that. Please try again.")
    return str(response)

if __name__ == '__main__':
    app.run(debug=True)

    incoming_msg = request.form.get('Body').strip().lower()
    from_number = request.form.get('From')
    response = MessagingResponse()

    if from_number not in sessions:
        sessions[from_number] = {'step': 'start'}

    current_step = sessions[from_number]['step']
    logger.info(f"Incoming message from {from_number}: {incoming_msg} | Current step: {current_step}")

    # Handle start
    if current_step == 'start':
        response.message("Welcome to Real Estate Bot! Send 'list' to view properties.")
        sessions[from_number]['step'] = 'listing'
        return str(response)

    # Handle property listing
    if incoming_msg == 'list' and current_step == 'listing':
        for prop_id, details in PROPERTIES.items():
            response.message(f"🏡 {details['name']}: {details['price']} INR at {details['location']} ({details['bhk']} BHK)")
        response.message("Reply with the property name for more details.")
        sessions[from_number]['step'] = 'details'
        return str(response)

    # Handle property details
    for prop_id, details in PROPERTIES.items():
        if incoming_msg == details['name'].lower() and current_step == 'details':
            response.message(f"Property: {details['name']}\nPrice: {details['price']} INR\nLocation: {details['location']}\nDescription: {details['description']}")
            send_property_images(response, details.get('images', []))
            sessions[from_number]['step'] = 'start'
            return str(response)

    response.message("Invalid command. Please try again.")
    return str(response)

if __name__ == '__main__':
    app.run(debug=True)
