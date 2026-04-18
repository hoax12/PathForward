# backend/ai/client.py
from __future__ import annotations


import os
from google import genai
from dotenv import load_dotenv

# Force load environment variables from the .env file
load_dotenv()

def get_client() -> genai.Client:
    # Explicitly fetch the key and pass it to the client instance
    api_key = os.getenv("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)

def get_model_name() -> str:
    # Use the model specified in .env, or fallback to flash
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
