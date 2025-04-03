import gspread
from google.oauth2.service_account import Credentials
import logging
from typing import List, Dict, Any
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheets_client():
    """Initialize and return Google Sheets client"""
    try:
        # First try to get credentials from environment variable
        creds_json = os.getenv('GOOGLE_CREDENTIALS')
        if creds_json:
            try:
                # Parse the JSON string from environment variable
                creds_dict = json.loads(creds_json)
                creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
                client = gspread.authorize(creds)
                logger.info("Successfully initialized Google Sheets client using environment credentials")
                return client
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing credentials JSON: {str(e)}")
        
        # Fallback to credentials file
        credentials_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
        if os.path.exists(credentials_path):
            creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
            client = gspread.authorize(creds)
            logger.info("Successfully initialized Google Sheets client using credentials file")
            return client
            
        logger.error("No credentials found in environment variables or credentials file")
        return None
            
    except Exception as e:
        logger.error(f"Error initializing Google Sheets client: {str(e)}")
        return None

def get_property_data() -> List[Dict[str, Any]]:
    """Fetch property data from Google Sheets"""
    try:
        client = get_sheets_client()
        if not client:
            logger.error("Could not initialize Google Sheets client")
            return []
            
        # Get spreadsheet ID from environment variable or use default
        spreadsheet_id = os.getenv('GOOGLE_SHEET_ID', 'your-spreadsheet-id')
        spreadsheet_name = os.getenv('GOOGLE_SHEET_NAME', 'RealEstateData')
        
        try:
            # Try to open by ID first
            spreadsheet = client.open_by_key(spreadsheet_id)
        except:
            # Fallback to opening by name
            spreadsheet = client.open(spreadsheet_name)
            
        # Get the first sheet
        sheet = spreadsheet.sheet1
        
        # Get all records
        records = sheet.get_all_records()
        logger.info(f"Successfully fetched {len(records)} property records")
        return records
    except Exception as e:
        logger.error(f"Error fetching property data: {str(e)}")
        return []

def format_property_data(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Format property data into the required structure"""
    properties = {}
    try:
        for i, record in enumerate(records, 1):
            try:
                price = int(str(record.get('price', '0')).replace('₹', '').replace(',', ''))
                bhk = int(str(record.get('bhk', '0')).replace('BHK', ''))
            except ValueError:
                price = 0
                bhk = 0
                
            properties[f'property{i}'] = {
                'name': record.get('name', ''),
                'price': price,
                'location': record.get('location', ''),
                'bhk': bhk,
                'description': record.get('description', ''),
                'images': record.get('images', '').split(',') if record.get('images') else []
            }
        return properties
    except Exception as e:
        logger.error(f"Error formatting property data: {str(e)}")
        return {}

if __name__ == "__main__":
    # Test the connection
    try:
        records = get_property_data()
        print(f"Fetched {len(records)} records:")
        for record in records:
            print(record)
    except Exception as e:
        print(f"Error: {str(e)}") 