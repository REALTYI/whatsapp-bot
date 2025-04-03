import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from sheets import get_property_data, format_property_data
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize property data from Google Sheets
try:
    records = get_property_data()
    if records:
        PROPERTIES = format_property_data(records)
        logger.info(f"Successfully loaded {len(PROPERTIES)} properties from Google Sheets")
    else:
        logger.warning("No records found in Google Sheets, using default data")
        PROPERTIES = {
            'property1': {
                'name': 'Ocean View Apartment',
                'price': 12000000,
                'location': 'Bandra, Mumbai',
                'bhk': 3,
                'description': 'Luxurious sea-facing apartment',
                'images': [
                    'https://imgur.com/vFCCHtC',
                    'https://imgur.com/ihW0dlY',
                    'https://imgur.com/YGxOIlh'
                ]
            }
        }
except Exception as e:
    logger.error(f"Error loading properties from Google Sheets: {str(e)}")
    PROPERTIES = {
        'property1': {
            'name': 'Ocean View Apartment',
            'price': 12000000,
            'location': 'Bandra, Mumbai',
            'bhk': 3,
            'description': 'Luxurious sea-facing apartment',
            'images': [
                'https://imgur.com/vFCCHtC',
                'https://imgur.com/ihW0dlY',
                'https://imgur.com/YGxOIlh'
            ]
        }
    }

# Session data
sessions = {}

def parse_indian_currency(amount_str: str) -> int:
    """Parse Indian currency format (e.g., '1cr', '50lakhs', '1.5cr') to rupees"""
    try:
        # Remove spaces and convert to lowercase
        amount_str = amount_str.lower().strip()
        
        # Remove '₹' symbol if present
        amount_str = amount_str.replace('₹', '').strip()
        
        # Handle crore format
        if 'cr' in amount_str:
            # Extract the number before 'cr'
            number = float(amount_str.replace('cr', '').strip())
            return int(number * 10000000)  # 1 crore = 10 million rupees
            
        # Handle lakhs format
        elif 'lakh' in amount_str or 'lac' in amount_str:
            # Extract the number before 'lakh' or 'lac'
            number = float(amount_str.replace('lakh', '').replace('lac', '').strip())
            return int(number * 100000)  # 1 lakh = 100,000 rupees
            
        # Handle direct number format
        else:
            # Remove commas and convert to integer
            return int(float(amount_str.replace(',', '')))
            
    except (ValueError, AttributeError) as e:
        logger.error(f"Error parsing amount: {str(e)}")
        return 0

def send_property_images(response, images):
    """Send property images using Twilio's Media Message API"""
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
    incoming_msg = request.form.get('Body', '').strip().lower()
    from_number = request.form.get('From', '')
    response = MessagingResponse()

    if from_number not in sessions:
        sessions[from_number] = {'step': 'start'}

    current_step = sessions[from_number]['step']
    logger.info(f"Incoming message from {from_number}: {incoming_msg} | Current step: {current_step}")

    # Handle back and start commands
    if incoming_msg in ['back', 'start']:
        if incoming_msg == 'start':
            sessions[from_number] = {'step': 'start'}
        elif current_step == 'collecting_budget':
            sessions[from_number]['step'] = 'collecting_info'
        elif current_step == 'collecting_location':
            sessions[from_number]['step'] = 'collecting_budget'
        elif current_step == 'details':
            sessions[from_number]['step'] = 'collecting_location'
        elif current_step == 'visit':
            sessions[from_number]['step'] = 'details'
        
        # Return to the appropriate step
        return whatsapp_bot()

    # Greeting
    if current_step == 'start':
        response.message("Hi there! 👋 Welcome to Real Estate Bot. How can I help you today? (e.g., 'Looking for a 3BHK')\n\nType 'start' anytime to begin again.")
        sessions[from_number]['step'] = 'collecting_info'
        return str(response)

    # Collecting user preferences
    if current_step == 'collecting_info':
        if 'bhk' in incoming_msg:
            sessions[from_number]['bhk'] = incoming_msg
            response.message("Great choice! What's your budget range? (e.g., '1cr', '50lakhs', '1.5cr')\n\nType 'back' to change property type\nType 'start' to begin again")
            sessions[from_number]['step'] = 'collecting_budget'
            return str(response)
        response.message("Could you specify the property type? (e.g., '3BHK apartment')\n\nType 'start' to begin again")
        return str(response)

    # Collecting budget
    if current_step == 'collecting_budget':
        budget = parse_indian_currency(incoming_msg)
        if budget > 0:
            sessions[from_number]['budget'] = budget
            response.message("Got it! Any preferred location?\n\nType 'back' to change budget\nType 'start' to begin again")
            sessions[from_number]['step'] = 'collecting_location'
            return str(response)
        response.message("Please enter a valid budget amount (e.g., '1cr', '50lakhs', '1.5cr')\n\nType 'back' to change property type\nType 'start' to begin again")
        return str(response)

    # Collecting location
    if current_step == 'collecting_location':
        sessions[from_number]['location'] = incoming_msg
        response.message(f"Perfect! Let me show you some options in {incoming_msg} within your budget.")
        # Listing matching properties
        for prop_id, details in PROPERTIES.items():
            response.message(f"🏡 {details['name']}: ₹{details['price']} at {details['location']} ({details['bhk']} BHK)")
        response.message("Reply with the property name for more details.\n\nType 'back' to change location\nType 'start' to begin again")
        sessions[from_number]['step'] = 'details'
        return str(response)

    # Displaying property details
    for prop_id, details in PROPERTIES.items():
        if incoming_msg == details['name'].lower() and current_step == 'details':
            response.message(f"Property: {details['name']}\nPrice: ₹{details['price']}\nLocation: {details['location']}\nDescription: {details['description']}")
            send_property_images(response, details.get('images', []))
            response.message("Do you want to schedule a visit? (e.g., 'Yes, tomorrow at 4 PM')\n\nType 'back' to see other properties\nType 'start' to begin again")
            sessions[from_number]['step'] = 'visit'
            return str(response)

    response.message("Sorry, I didn't get that. Please try again.\n\nType 'back' to go back\nType 'start' to begin again")
    return str(response)

@app.route('/', methods=['GET'])
def root():
    return "WhatsApp Bot is running!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
