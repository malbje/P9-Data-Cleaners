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
            "name": "list_customers",
            "description": "Returns customers. Optional: filter with a free-text search on name/surname/email.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "free text (name, surname or email)"},
                    "limit": {"type": "integer", "description": "max number of rows", "default": 20}
                }
            }
        }
    },
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
    }
]