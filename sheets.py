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

# Define absolute path for credentials
CREDENTIALS_PATH = r"C:\Users\darsh\OneDrive\Desktop\whatsapp-bot\credentials.json"

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
        
        # Fallback to credentials file using absolute path
        if os.path.exists(CREDENTIALS_PATH):
            logger.info(f"Using credentials file at: {CREDENTIALS_PATH}")
            creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
            client = gspread.authorize(creds)
            logger.info("Successfully initialized Google Sheets client using credentials file")
            return client
        else:
            logger.error(f"credentials.json file not found at: {CREDENTIALS_PATH}")
            
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

        # Get spreadsheet ID and name from environment variables
        sheet_id = os.getenv('GOOGLE_SHEET_ID')
        sheet_name = os.getenv('GOOGLE_SHEET_NAME', 'RealEstateData')

        logger.info(f"Attempting to access sheet: {sheet_name} (ID: {sheet_id})")

        # Try to open by ID first
        try:
            if sheet_id:
                spreadsheet = client.open_by_key(sheet_id)
                logger.info(f"Successfully opened spreadsheet by ID: {sheet_id}")
            else:
                spreadsheet = client.open(sheet_name)
                logger.info(f"Successfully opened spreadsheet by name: {sheet_name}")
        except Exception as e:
            logger.error(f"Error opening spreadsheet: {str(e)}")
            return []

        # Get the first worksheet
        worksheet = spreadsheet.get_worksheet(0)
        if not worksheet:
            logger.error("No worksheet found in the spreadsheet")
            return []

        # Get all records
        records = worksheet.get_all_records()
        
        # Log the data found
        logger.info(f"Found {len(records)} records in the spreadsheet")
        if records:
            logger.info("Sample of first record:")
            logger.info(json.dumps(records[0], indent=2))
        else:
            logger.warning("No records found in the spreadsheet")

        return records

    except Exception as e:
        logger.error(f"Error fetching property data: {str(e)}")
        return []

def format_property_data(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Format property data into a dictionary"""
    formatted_data = {}
    try:
        for idx, record in enumerate(records, 1):
            try:
                # Log each record being processed
                logger.info(f"Processing record {idx}: {record.get('name', 'Unnamed')}")
                
                # Convert price to integer, handling different formats
                price_str = str(record.get('price', '0'))
                try:
                    # Handle 'Cr' format
                    if 'cr' in price_str.lower():
                        price = float(price_str.lower().replace('cr', '').strip()) * 10000000
                    # Handle 'L' format
                    elif 'l' in price_str.lower():
                        price = float(price_str.lower().replace('l', '').strip()) * 100000
                    else:
                        price = float(price_str.replace(',', ''))
                    price = int(price)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid price format in record {idx}: {price_str}")
                    price = 0

                # Convert BHK to integer
                try:
                    bhk = int(float(str(record.get('bhk', '0')).replace(',', '')))
                except (ValueError, TypeError):
                    logger.warning(f"Invalid BHK format in record {idx}: {record.get('bhk')}")
                    bhk = 0

                # Create property entry
                property_id = f'property{idx}'
                formatted_data[property_id] = {
                    'name': record.get('name', 'Unnamed Property'),
                    'price': price,
                    'location': record.get('location', 'Location not specified'),
                    'bhk': bhk,
                    'description': record.get('description', 'No description available'),
                    'images': record.get('images', '').split(',') if record.get('images') else []
                }
                
                logger.info(f"Successfully formatted property: {property_id} - {formatted_data[property_id]['name']} with price: ₹{price:,}")
                
            except Exception as e:
                logger.error(f"Error formatting record {idx}: {str(e)}")
                continue

        logger.info(f"Successfully formatted {len(formatted_data)} properties")
        return formatted_data

    except Exception as e:
        logger.error(f"Error in format_property_data: {str(e)}")
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