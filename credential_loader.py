import json
import os
import logging

def load_credentials_from_json(file_path=None):
    """
    Load credentials from JSON file.
    
    Args:
        file_path (str): Path to JSON credential file. 
                        Defaults to "/tmp/sap_login/credential.json"
    
    Returns:
        dict: Dictionary containing credentials
    """
    if file_path is None:
        # Try Linux path first (for Replit), then Windows path
        file_path = "/tmp/sap_login/credential.json"
        if not os.path.exists(file_path):
            file_path = "C:/tmp/sap_login/credential.json"
    
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                credentials = json.load(f)
            logging.info(f"✅ Credentials loaded from {file_path}")
            return credentials
        else:
            logging.warning(f"⚠️ Credential file not found at {file_path}")
            return {}
    except json.JSONDecodeError as e:
        logging.error(f"❌ Error parsing JSON credential file: {e}")
        return {}
    except Exception as e:
        logging.error(f"❌ Error loading credential file: {e}")
        return {}

def get_credential(credentials, key, default=None):
    """
    Get a specific credential with fallback to environment variable.
    
    Args:
        credentials (dict): Loaded credentials dictionary
        key (str): Credential key to retrieve
        default: Default value if key not found
    
    Returns:
        str: Credential value
    """
    # Try to get from JSON credentials first
    if key in credentials:
        return credentials[key]
    
    # Fallback to environment variable
    env_value = os.environ.get(key, default)
    if env_value:
        logging.info(f"Using environment variable for {key}")
        return env_value
    
    logging.warning(f"⚠️ Credential '{key}' not found in JSON file or environment")
    return default