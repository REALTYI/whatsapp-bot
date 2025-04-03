import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from sheets import get_property_data, format_property_data, store_user_interaction, update_user_interaction_status
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enhanced Logging setup
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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

def debug_session(from_number: str, action: str):
    """Debug helper to log session state"""
    if from_number in sessions:
        logger.debug(f"Session Debug - Number: {from_number}, Action: {action}")
        logger.debug(f"Current State: {sessions[from_number]}")
    else:
        logger.debug(f"No session found for {from_number}")

def parse_indian_currency(amount_str: str) -> int:
    """Parse Indian currency format (e.g., '1.5 Cr', '80 L', '2.5 Cr') to rupees"""
    try:
        # Remove spaces and convert to lowercase
        amount_str = str(amount_str).lower().strip()
        
        # Remove '₹' symbol if present
        amount_str = amount_str.replace('₹', '').strip()
        
        # Handle crore format (Cr)
        if 'cr' in amount_str:
            # Extract the number before 'cr'
            number = float(amount_str.replace('cr', '').strip())
            return int(number * 10000000)  # 1 crore = 10 million rupees
            
        # Handle lakhs format (L)
        elif 'l' in amount_str:
            # Extract the number before 'l'
            number = float(amount_str.replace('l', '').strip())
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
        if not images:
            logger.warning("No images provided to send")
            return False
            
        msg = response.message("📸 Property Images:")
        for image_url in images[:10]:
            logger.debug(f"Attempting to send image: {image_url}")
            msg.media(image_url)
        logger.info(f"Successfully sent {len(images[:10])} images")
        return True
    except Exception as e:
        logger.error(f"Error sending images: {str(e)}")
        return False

@app.route('/whatsapp', methods=['POST'])
def whatsapp_bot():
    try:
        incoming_msg = request.form.get('Body', '').strip().lower()
        from_number = request.form.get('From', '')
        response = MessagingResponse()

        logger.debug(f"Received message: '{incoming_msg}' from {from_number}")

        if from_number not in sessions:
            logger.debug(f"Creating new session for {from_number}")
            sessions[from_number] = {'step': 'start', 'phone_number': from_number}

        current_step = sessions[from_number]['step']
        logger.info(f"Processing message - Number: {from_number}, Message: '{incoming_msg}', Current step: {current_step}")

        debug_session(from_number, "before_processing")

        # Handle back and start commands
        if incoming_msg in ['back', 'start']:
            logger.debug(f"Handling navigation command: {incoming_msg}")
            if incoming_msg == 'start':
                sessions[from_number] = {'step': 'start', 'phone_number': from_number}
                logger.debug("Resetting session to start")
            elif current_step == 'collecting_budget':
                sessions[from_number]['step'] = 'collecting_info'
            elif current_step == 'collecting_location':
                sessions[from_number]['step'] = 'collecting_budget'
            elif current_step == 'details':
                sessions[from_number]['step'] = 'collecting_location'
            elif current_step == 'visit':
                sessions[from_number]['step'] = 'details'
            
            debug_session(from_number, "after_navigation")
            return whatsapp_bot()

        # Collecting user preferences
        if current_step == 'collecting_info':
            if 'bhk' in incoming_msg:
                sessions[from_number]['property_type'] = incoming_msg
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
            
            # Store initial interaction data
            store_user_interaction({
                'phone_number': from_number,
                'property_type': sessions[from_number].get('property_type', ''),
                'budget': sessions[from_number].get('budget', ''),
                'location': incoming_msg,
                'status': 'Searching'
            })
            
            response.message(f"Perfect! Let me show you some options in {incoming_msg} within your budget.")
            
            # Store property list in session for number-based selection
            property_list = list(PROPERTIES.items())
            sessions[from_number]['property_list'] = property_list
            
            # Listing matching properties with numbers
            for idx, (prop_id, details) in enumerate(property_list, 1):
                response.message(f"{idx}. 🏡 {details['name']}: ₹{details['price']:,} at {details['location']} ({details['bhk']} BHK)")
            
            response.message("Reply with the property number or name for more details.\n\nType 'back' to change location\nType 'start' to begin again")
            sessions[from_number]['step'] = 'details'
            return str(response)

        # Displaying property details
        if current_step == 'details':
            property_list = sessions[from_number].get('property_list', [])
            
            # Try to find property by number
            try:
                property_idx = int(incoming_msg) - 1
                if 0 <= property_idx < len(property_list):
                    prop_id, details = property_list[property_idx]
                else:
                    raise ValueError("Invalid property number")
            except ValueError:
                # Try to find property by name
                prop_id = None
                for pid, d in PROPERTIES.items():
                    if incoming_msg == d['name'].lower():
                        prop_id = pid
                        details = d
                        break
            
            if prop_id and details:
                # Update interaction with selected property
                sessions[from_number]['selected_property'] = details['name']
                update_user_interaction_status(from_number, 'Property Selected')
                
                response.message(f"Property: {details['name']}\nPrice: ₹{details['price']:,}\nLocation: {details['location']}\nDescription: {details['description']}")
                send_property_images(response, details.get('images', []))
                response.message("Do you want to schedule a visit? (e.g., 'Yes, tomorrow at 4 PM')\n\nType 'back' to see other properties\nType 'start' to begin again")
                sessions[from_number]['step'] = 'visit'
                return str(response)
            
            response.message("Sorry, I couldn't find that property. Please try again with the property number or name.\n\nType 'back' to see the property list\nType 'start' to begin again")
            return str(response)

        # Handling visit scheduling
        if current_step == 'visit':
            if 'yes' in incoming_msg:
                # Extract date and time from message
                visit_schedule = incoming_msg.replace('yes', '').strip()
                
                # Update interaction with visit schedule
                store_user_interaction({
                    'phone_number': from_number,
                    'property_type': sessions[from_number].get('property_type', ''),
                    'budget': sessions[from_number].get('budget', ''),
                    'location': sessions[from_number].get('location', ''),
                    'selected_property': sessions[from_number].get('selected_property', ''),
                    'visit_schedule': visit_schedule,
                    'status': 'Visit Scheduled'
                })
                
                response.message(f"Great! I've scheduled your visit for {visit_schedule}. Our representative will contact you shortly to confirm.\n\nType 'start' to look for more properties.")
                return str(response)

        debug_session(from_number, "after_processing")
        
        response.message("Sorry, I didn't get that. Please try again.\n\nType 'back' to go back\nType 'start' to begin again")
        return str(response)

    except Exception as e:
        logger.error(f"Unexpected error in whatsapp_bot: {str(e)}", exc_info=True)
        response = MessagingResponse()
        response.message("Sorry, something went wrong. Please type 'start' to begin again.")
        return str(response)

@app.route('/', methods=['GET'])
def root():
    return "WhatsApp Bot is running!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
