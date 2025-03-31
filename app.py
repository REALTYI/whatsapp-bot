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
def whatsapp_bot():
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
