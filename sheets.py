import gspread
from google.oauth2.service_account import Credentials
import logging
from typing import List, Dict, Any
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Define the absolute path for credentials.json
CREDENTIALS_PATH = r"C:\Users\darsh\OneDrive\Desktop\whatsapp-bot\credentials.json"

def get_sheets_client():
    """Initialize and return Google Sheets client"""
    try:
        # Check if credentials file exists at the absolute path
        if not os.path.exists(CREDENTIALS_PATH):
            logger.error(f"credentials.json file not found at: {CREDENTIALS_PATH}")
            return None
            
        # Load credentials from service account file using absolute path
        creds = Credentials.from_service_account_file(
            CREDENTIALS_PATH,
            scopes=SCOPES
        )
        # Authorize the client
        client = gspread.authorize(creds)
        logger.info("Successfully initialized Google Sheets client")
        return client
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