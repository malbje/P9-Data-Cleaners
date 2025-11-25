# backend/llm_tools.py
# OpenAI function-calling + integration to our DB_read.py

from typing import Any, Dict, List, Optional
from openai import OpenAI
from database.DB_read import DB_read
from private_settings import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)            # reads OPENAI_API_KEY from private_settings
db = DB_read()               # Our data access layer

# -----------------------------
# Tool-definitions (JSON schema)
# Only READ-related tools for now.
# -----------------------------
TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "list_customers_by_name",
            "description": "Find customers with partial/full first name and last name (LIKE search).",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "first name (partial or full)"},
                    "surname": {"type": "string", "description": "last name (partial or full)"}
                },
                "required": ["name", "surname"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_by_email",
            "description": "Find a customer by email (unique).",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"}
                },
                "required": ["email"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_by_id",
            "description": "Get a customer by customer ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "integer"}
                },
                "required": ["customer_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_customer",
            "description": "Create a new customer with name, surname, and email.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": { "type": "string" },
                    "surname": { "type": "string" },
                    "email": { "type": "string", "format": "email" }
                },
                "required": ["name", "surname", "email"]
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'add_address',
            'description': 'Create a new address with an steet name, 4 digit postal code, and city name.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'street': { 'type': 'string' },
                    'postal': { 'type': 'integer' },
                    'city': { 'type': 'string' }
                },
                'required': ['steet', 'postal', 'city']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'link_customer_to_address',
            'description': 'Adds to junction table the id for a customer and id for an address, giving the customer that address',
            'parameters': {
                'type': 'object',
                'properties': {
                    'customer_id': { 'type': 'integer' },
                    'address_id': { 'type': 'integer' }
                },
                'required': ['customer_id', 'address_id']
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_addresses",
            "description": "Find all addresses for a customer by name (possibly full name) or email.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name_or_email": {"type": "string", "description": "e.g. 'Anne Madsen' or 'anne@firma.dk'"}
                },
                "required": ["name_or_email"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_appointments_by_address_id",
            "description": "Get all appointments for an address (including service names).",
            "parameters": {
                "type": "object",
                "properties": {
                    "address_id": {"type": "integer"}
                },
                "required": ["address_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_appointment_by_id",
            "description": "Get a specific appointment by its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {"type": "integer"}
                },
                "required": ["appointment_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_precipitation",
            "description": "Returns a list of precipitation values (in mm) for the next 16 days including today. Call this when looking for info expected rain",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": 'function',
        'function': {
            'name': 'choose_case',
            'description': 'ask chat_gpt to choose which case the user belongs to, based on the chat history. Then inserts that case into chat history.',
            'parameters': {
                'type': 'object',
                'properties': {}
            }
        }
    }
]