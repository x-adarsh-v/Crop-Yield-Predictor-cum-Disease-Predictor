import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Retrieve the Hugging Face token from the environment
HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN')

def get_hf_token():
    """
    Returns the Hugging Face token.
    Raises a ValueError if the token is not set.
    """
    if not HUGGINGFACE_TOKEN:
        raise ValueError("Hugging Face token not set in the .env file!")
    return HUGGINGFACE_TOKEN
