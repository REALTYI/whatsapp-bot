from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import logging
import pickle
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Google Calendar API setup
SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID')

# User session management
user_sessions = {}

class UserSession:
    def __init__(self, phone_number):
        self.phone_number = phone_number
        self.current_step = "initial"
        self.selected_property = None
        self.search_results = None
        self.location = None
        self.property_type = None

def get_user_session(phone_number):
    if phone_number not in user_sessions:
        user_sessions[phone_number] = UserSession(phone_number)
    return user_sessions[phone_number]

def get_google_calendar_service():
    """Get or create Google Calendar service"""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('calendar', 'v3', credentials=creds)

def schedule_visit(property_name, visitor_name, phone_number, preferred_date, preferred_time):
    """Schedule a property visit in Google Calendar"""
    try:
        service = get_google_calendar_service()
        
        visit_datetime = datetime.strptime(f"{preferred_date} {preferred_time}", "%Y-%m-%d %H:%M")
        
        event = {
            'summary': f'Property Visit: {property_name}',
            'description': f'Visitor: {visitor_name}\nPhone: {phone_number}',
            'start': {
                'dateTime': visit_datetime.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': (visit_datetime + timedelta(hours=1)).isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
        }
        
        event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        return True, event['id']
    except Exception as e:
        logger.error(f"Error scheduling visit: {str(e)}")
        return False, str(e)

# Sample property data with image URLs and virtual tours
PROPERTIES = {
    "mumbai": {
        "apartment": [
            {
                "name": "Luxury Sea View Apartment",
                "price": "₹2.5 Cr",
                "location": "Bandra",
                "features": "3BHK, Sea View, Gym",
                "images": [
                    "https://example.com/properties/mumbai/bandra-sea-view-1.jpg",
                    "https://example.com/properties/mumbai/bandra-sea-view-2.jpg"
                ],
                "virtual_tour": "https://example.com/virtual-tours/bandra-sea-view",
                "description": "Stunning 3BHK apartment with panoramic sea views, modern amenities, and 24/7 security."
            },
            {
                "name": "Modern Studio Apartment",
                "price": "₹85 L",
                "location": "Andheri",
                "features": "1BHK, Smart Home",
                "images": [
                    "https://example.com/properties/mumbai/andheri-studio-1.jpg",
                    "https://example.com/properties/mumbai/andheri-studio-2.jpg"
                ]
            },
        ],
        "house": [
            {
                "name": "Bungalow with Garden",
                "price": "₹5 Cr",
                "location": "Juhu",
                "features": "4BHK, Garden, Pool",
                "images": [
                    "https://example.com/properties/mumbai/juhu-bungalow-1.jpg",
                    "https://example.com/properties/mumbai/juhu-bungalow-2.jpg"
                ]
            },
            {
                "name": "Family Villa",
                "price": "₹3.2 Cr",
                "location": "Powai",
                "features": "3BHK, Terrace, Parking",
                "images": [
                    "https://example.com/properties/mumbai/powai-villa-1.jpg",
                    "https://example.com/properties/mumbai/powai-villa-2.jpg"
                ]
            },
        ]
    },
    "delhi": {
        "apartment": [
            {
                "name": "Penthouse with Terrace",
                "price": "₹3.8 Cr",
                "location": "South Delhi",
                "features": "4BHK, Terrace, Security",
                "images": [
                    "https://example.com/properties/delhi/south-delhi-penthouse-1.jpg",
                    "https://example.com/properties/delhi/south-delhi-penthouse-2.jpg"
                ]
            },
            {
                "name": "Smart Apartment",
                "price": "₹1.2 Cr",
                "location": "Noida",
                "features": "2BHK, Smart Home",
                "images": [
                    "https://example.com/properties/delhi/noida-smart-1.jpg",
                    "https://example.com/properties/delhi/noida-smart-2.jpg"
                ]
            },
        ],
        "house": [
            {
                "name": "Colonial Style House",
                "price": "₹4.5 Cr",
                "location": "Lutyens Delhi",
                "features": "5BHK, Garden, Servant Room",
                "images": [
                    "https://example.com/properties/delhi/lutyens-colonial-1.jpg",
                    "https://example.com/properties/delhi/lutyens-colonial-2.jpg"
                ]
            },
            {
                "name": "Modern Villa",
                "price": "₹2.8 Cr",
                "location": "Gurgaon",
                "features": "3BHK, Pool, Club House",
                "images": [
                    "https://example.com/properties/delhi/gurgaon-villa-1.jpg",
                    "https://example.com/properties/delhi/gurgaon-villa-2.jpg"
                ]
            },
        ]
    }
}

def send_property_images(response, property_images):
    """Send property images using Twilio's Media Message API"""
    try:
        for image_url in property_images[:10]:
            response.message().media(image_url)
        return True
    except Exception as e:
        logger.error(f"Error sending property images: {str(e)}")
        return False

def handle_property_search(location, property_type, budget=None):
    """Handle property search and return formatted response"""
    try:
        location = location.lower()
        property_type = property_type.lower()
        
        if location not in PROPERTIES:
            return "❌ Sorry, we don't have properties in that location yet. Try Mumbai or Delhi! 🏙️"
        
        if property_type not in PROPERTIES[location]:
            return "❌ Sorry, we don't have that property type. Try 'apartment' or 'house'! 🏠"
        
        properties = PROPERTIES[location][property_type]
        filtered_properties = [p for p in properties if p["price"] <= budget] if budget else properties
        
        if not filtered_properties:
            return "❌ No properties found matching your criteria. Try adjusting your budget! 💰"
        
        response = f"🏠 *Property Options in {location.title()}*\n\n"
        for i, prop in enumerate(filtered_properties, 1):
            response += f"{i}. *{prop['name']}*\n"
            response += f"   📍 Location: {prop['location']}\n"
            response += f"   💰 Price: {prop['price']}\n"
            response += f"   ✨ Features: {prop['features']}\n\n"
        
        response += "Reply with:\n"
        response += "- Number of property for details\n"
        response += "- 'back' to return to search"
        return response, filtered_properties
        
    except Exception as e:
        logger.error(f"Error in property search: {str(e)}")
        return "❌ Oops! Something went wrong. Please try again! 🔄", None

def handle_property_details(property):
    """Handle detailed property view"""
    response = f"🏠 *{property['name']}*\n\n"
    response += f"📍 Location: {property['location']}\n"
    response += f"💰 Price: {property['price']}\n"
    response += f"✨ Features: {property['features']}\n"
    response += f"📝 Description: {property['description']}\n\n"
    
    response += "What would you like to do?\n"
    response += "1. View images 📸\n"
    response += "2. Take virtual tour 🎥\n"
    response += "3. Schedule a visit 📅\n"
    response += "4. Back to search 🔍"
    
    return response

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    try:
        incoming_msg = request.values.get("Body", "").lower()
        from_number = request.values.get("From", "")
        
        logger.info(f"Received message from {from_number}: {incoming_msg}")
        
        response = MessagingResponse()
        session = get_user_session(from_number)
        
        # Handle initial greeting
        if session.current_step == "initial" and incoming_msg in ["hi", "hello", "hey"]:
            session.current_step = "search"
            response.message().body(
                "👋 Welcome to PropertyBot! 🏠\n\n"
                "Let's find your perfect property! First, tell me:\n"
                "1. Which city? (Mumbai/Delhi)\n"
                "2. What type? (apartment/house)\n"
                "3. Your budget (optional)\n\n"
                "Example: mumbai apartment 2.5cr"
            )
            return str(response)
        
        # Handle property search
        elif session.current_step == "search":
            parts = incoming_msg.split()
            if len(parts) >= 2:
                location = parts[0]
                property_type = parts[1]
                budget = parts[2] if len(parts) > 2 else None
                
                search_response, properties = handle_property_search(location, property_type, budget)
                if properties:
                    session.search_results = properties
                    session.location = location
                    session.property_type = property_type
                    session.current_step = "select_property"
                response.message().body(search_response)
            else:
                response.message().body(
                    "🔍 Please provide location and property type.\n"
                    "Example: mumbai apartment 2.5cr"
                )
        
        # Handle property selection
        elif session.current_step == "select_property":
            try:
                property_index = int(incoming_msg) - 1
                if 0 <= property_index < len(session.search_results):
                    session.selected_property = session.search_results[property_index]
                    session.current_step = "property_details"
                    response.message().body(handle_property_details(session.selected_property))
                else:
                    response.message().body("❌ Invalid property number. Please try again!")
            except ValueError:
                response.message().body("❌ Please provide a valid property number.")
        
        # Handle property details options
        elif session.current_step == "property_details":
            if incoming_msg == "1":
                if send_property_images(response, session.selected_property["images"]):
                    response.message().body(f"📸 Here are the images for {session.selected_property['name']}!")
                else:
                    response.message().body("❌ Sorry, couldn't send the images. Please try again later.")
            
            elif incoming_msg == "2":
                response.message().body(
                    f"🎥 Virtual Tour Link:\n"
                    f"{session.selected_property['virtual_tour']}\n\n"
                    "Click the link to take a virtual tour of the property!"
                )
            
            elif incoming_msg == "3":
                session.current_step = "schedule_visit"
                response.message().body(
                    "📅 Let's schedule your visit!\n\n"
                    "Please provide:\n"
                    "1. Your name\n"
                    "2. Phone number\n"
                    "3. Preferred date (YYYY-MM-DD)\n"
                    "4. Preferred time (HH:MM)\n\n"
                    "Example:\n"
                    "John Doe\n"
                    "+1234567890\n"
                    "2024-03-20\n"
                    "14:00"
                )
            
            elif incoming_msg == "4":
                session.current_step = "search"
                response.message().body(
                    "🔍 Let's search again!\n"
                    "Tell me:\n"
                    "1. Which city? (Mumbai/Delhi)\n"
                    "2. What type? (apartment/house)\n"
                    "3. Your budget (optional)\n\n"
                    "Example: mumbai apartment 2.5cr"
                )
        
        # Handle visit scheduling
        elif session.current_step == "schedule_visit":
            try:
                parts = incoming_msg.split("\n")
                if len(parts) >= 4:
                    visitor_name = parts[0]
                    phone_number = parts[1]
                    preferred_date = parts[2]
                    preferred_time = parts[3]
                    
                    success, result = schedule_visit(
                        session.selected_property["name"],
                        visitor_name,
                        phone_number,
                        preferred_date,
                        preferred_time
                    )
                    
                    if success:
                        response.message().body(
                            f"✅ Visit scheduled successfully!\n\n"
                            f"Property: {session.selected_property['name']}\n"
                            f"Date: {preferred_date}\n"
                            f"Time: {preferred_time}\n"
                            f"Duration: 1 hour\n\n"
                            f"You'll receive a calendar invitation shortly! 📅"
                        )
                    else:
                        response.message().body(f"❌ Sorry, couldn't schedule the visit. Error: {result}")
                    
                    session.current_step = "property_details"
                    response.message().body(handle_property_details(session.selected_property))
                else:
                    response.message().body(
                        "📅 Please provide all required information:\n"
                        "1. Your name\n"
                        "2. Phone number\n"
                        "3. Preferred date (YYYY-MM-DD)\n"
                        "4. Preferred time (HH:MM)"
                    )
            except Exception as e:
                logger.error(f"Error processing visit request: {str(e)}")
                response.message().body("❌ Sorry, couldn't process your visit request. Please try again!")
        
        # Handle back command
        elif incoming_msg == "back":
            if session.current_step == "property_details":
                session.current_step = "select_property"
                response.message().body(handle_property_search(session.location, session.property_type)[0])
            elif session.current_step == "select_property":
                session.current_step = "search"
                response.message().body(
                    "🔍 Let's search again!\n"
                    "Tell me:\n"
                    "1. Which city? (Mumbai/Delhi)\n"
                    "2. What type? (apartment/house)\n"
                    "3. Your budget (optional)\n\n"
                    "Example: mumbai apartment 2.5cr"
                )
        
        else:
            response.message().body(
                "👋 Welcome to PropertyBot! 🏠\n\n"
                "Say 'hi' to start searching for properties!"
            )
        
        logger.info("Successfully processed message and sent response")
        return str(response)
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp message: {str(e)}")
        response = MessagingResponse()
        response.message().body("❌ Sorry, there was an error processing your message. Please try again later.")
        return str(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting WhatsApp bot server on port {port}")
    app.run(host='0.0.0.0', port=port)
