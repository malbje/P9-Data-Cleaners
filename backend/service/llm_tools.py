# backend/llm_tools.py
# OpenAI function-calling + integration to our DB_read.py

from typing import Any, Dict, List, Optional

# -----------------------------
# Tool-definitions (JSON schema)
# Only READ-related tools for now.
# -----------------------------
TOOLS: List[Dict[str, Any]] = [
    # list_customers_by_name
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
    # get_customer_by_id
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
    # get_customers_by_appointment_id
    {
        "type": "function",
        "function": {
            "name": "get_customers_by_appointment_id",
            "description": "Get a customer by the id of one of their appointments.",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {"type": "integer"}
                },
                "required": ["appointment_id"]
            }
        }
    },
    # get_customers_by_address_id
    {
        "type": "function",
        "function": {
            "name": "get_customers_by_address_id",
            "description": "Get a customer by the id of one of their addresses",
            "parameters": {
                "type": "object",
                "properties": {
                    "address_id": {"type": "integer"}
                },
                "required": ["address_id"]
            }
        }
    },
    # find_address_by_text
    {
        "type": "function",
        "function": {
            "name": "find_address_by_text",
            "description": "Search addresses across street, postal code and city using partial matching. Returns list of matching addresses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_text": {"type": "string", 'description': 'includes street name, postal code and/or city name'}
                },
                "required": ["search_text"]
            }
        }
    },
    # get_addresses_and_preferences_for_customer
    {
        'type': 'function',
        'function': {
            'name': 'get_addresses_and_preferences_for_customer',
            'description': 'Gets all addresses and their associated preferences for a specific customer.',
            'parameters': {
                'type': 'obejct',
                'properties': {
                    'customer_id': {'type': 'integer' }
                },
                'required': ['customer_id']
            }
        }
    },
    # add_prefrences_for_address_id
    {
        'type': 'function',
        'function': {
            'name': 'add_prefrences_for_address_id',
            'description': 'Adds additional info about an address to a table.',
            'parameters': {
                'type': 'obejct',
                'properties': {
                    'address_id': {'type': 'integer' },
                    'allergies': {'type': 'string'},
                    'pets': {'type': 'string'},
                    'kids': {'type': 'string'},
                    'square_footage': {'type': 'number', 'description': 'Has two decimal spaces'},
                    'notes': {'type': 'string'}
                },
                'required': ['address_id']
            }
        }
    },
    # add_customer
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
    # add_address
    {
        'type': 'function',
        'function': {
            'name': 'add_address',
            'description': 'Create a new address with an steet name, 4 digit postal code, and city name.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'street': { 'type': 'string' },
                    'postal': { 'type': 'string' },
                    'city': { 'type': 'string' }
                },
                'required': ['steet', 'postal', 'city']
            }
        }
    },
    # link_customer_to_address
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
    # add_appointment
    {
        'type': 'function',
        'function': {
            'name': 'add_appointment',
            'description': 'Create a new appointment, with an address id, a date (yyyy-mm-dd) and a time (format like 14:35:55) for the appointment, and optional notes.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'address_id': { 'type': 'integer' },
                    'date': { 'type': 'string' },
                    'time': { 'type': 'string' },
                    'notes': { 'type': 'string' }
                },
                'required': ['address_id', 'date', 'time']
            }
        }
    },
    # get_customer_by_email
    {
        "type": "function",
        "function": {
            'name': 'get_customer_by_email',
            'description': 'Find a customer and their info from the customer table by their email.',
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"}
                },
                "required": ["email"]
            }
        }
    },
    # get_address_by_id
    {
        'type': 'funciton',
        'function': {
            'name': 'get_address_by_id',
            'description': 'Get address info from given address id',
            "parameters": {
                "type": "object",
                "properties": {
                    "address_id": {"type": "integer"}
                },
                "required": ["address_id"]
            }
        }
    },
    # get_addresses_by_customer_id
    {
        "type": "function",
        "function": {
            "name": "get_addresses_by_customer_id",
            "description": "use a customers id to get all their addresses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "integer"}
                },
                "required": ["customer_id"]
            }
        }
    },
    # update_customer_address
    {
        "type": "function",
        "function": {
            "name": "update_customer_address",
            "description": "Update the city name, postal code, and street name and number for a given customers address",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "integer"},
                    'address_id': {'type': 'integer'},
                    'city': {'type': 'string', 'description': 'city name'},
                    'postal': {'type': 'string', 'description': 'a 4 digit postal code'},
                    'street': {'type': 'string', 'description': 'street name, and street number if needed'}
                },
                "required": ["customer_id", 'address_id', 'city', 'postal', 'street']
            }
        }
    },
    # get_appointments_by_address_id
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
    # get_appointment_by_id
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
    # get_precipitation
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
    # choose_case
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