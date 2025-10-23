# llm_tools.py - JSON Schema tool definitions for OpenAI function calling.
# Each tool maps to a database function in DB_read.py.

TOOLS = [
    # Customer Management Tools
    # These tools allow OpenAI to query and manipulate customer data
    
    {
        "type": "function",
        "function": {
            "name": "list_customers",
            "description": "Get all customers from the database. Returns a list of customers. Use this when user asks to see all customers, get customer overview, or list everyone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customers": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "string"},
                                "surname": {"type": "string"},
                                "address": {"type": "string"},
                                "email": {"type": "string"},
                                "notification_preference": {"type": "string"}
                            },
                            "required": ["id", "name", "surname", "address", "email", "notification_preference"]
                        }
                    }
                }
            }
        }
    },
    
    {
        "type": "function",
        "function": {
            "name": "list_customers_by_name",
            "description": "Find customers by their name and surname using partial matching (LIKE search). Use this when user searches for specific customers by name. Both name and surname support partial matches.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The first name (partial or full) of the customer."
                    },
                    "surname": {
                        "type": "string",
                        "description": "The surname (partial or full) of the customer."
                    }
                },
                "required": ["name", "surname"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_customer_by_email",
            "description": "Retrieve a customer by their unique email address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "The unique email address of the customer."
                    }
                },
                "required": ["email"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_customer_by_id",
            "description": "Retrieve a customer by their unique ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "The unique ID of the customer."
                    }
                },
                "required": ["customer_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "add_customer",
            "description": "Opretter en ny kunde i databasen.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "surname": {"type": "string"},
                    "email": {"type": "string"},
                    "notification_preference": {"type": "string"}
                },
                "required": ["name", "surname", "email", "notification_preference"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "add_address",
            "description": "Adds an address to a customer based on their ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer"
                    },
                    "address": {
                        "type": "string"
                    }
                },
                "required": ["customer_id", "address"]
            }
        }
    },

    # Appointment Management Tools
    # These tools handle scheduling and managing appointments
    
    {
        "type": "function",
        "function": {
            "name": "add_appointment",
            "description": "Creates a new appointment in the database. Use this when user wants to schedule, create, or book an appointment. Requires address_id (use find_address_by_text first if user provides text address), date in YYYY-MM-DD format, and time in HH:MM format.",
            "parameters": {
                "type": "object",
                "properties": {
                    "address_id": {
                        "type": "integer"
                    },
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format"
                    },
                    "time": {
                        "type": "string",
                        "description": "Time in HH:MM format"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Any notes for the appointment. Use empty string if no notes."
                    },
                    "notification_preference": {
                        "type": "string",
                        "description": "How to notify customer: 'email', 'sms', 'phone', or 'none'. Default is 'email'.",
                        "default": "email"
                    }
                },
                "required": ["address_id", "date", "time"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "update_customer_address",
            "description": "Updates a customer's address based on their ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer"
                    },
                    "address_id": {
                        "type": "integer"
                    },
                    "city_name": {
                        "type": "string"
                    },
                    "postal_code": {
                        "type": "string"
                    },
                    "street_and_number": {
                        "type": "string"
                    }
                },
                "required": ["customer_id", "address_id", "city_name", "postal_code", "street_and_number"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "delete_customer",
            "description": "Deletes a customer based on their ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer"
                    }
                },
                "required": ["customer_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_appointments_by_address_id",
            "description": "Retrieve all appointments for a specific address by its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "address_id": {
                        "type": "integer"
                    }
                },
                "required": ["address_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_appointments_by_id",
            "description": "Retrieve specific appointment by its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "The unique ID of the appointment."
                    }
                },
                "required": ["id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_customers_by_address_id",
            "description": "Retrieve all customers by their address ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "address_id": {
                        "type": "integer"
                    }
                },
                "required": ["address_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_appointments_by_id",
            "description": "Retrieve specific appointment by its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "The unique ID of the appointment."
                    }
                },
                "required": ["id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_customers_by_appointment_id",
            "description": "Retrieve all customers linked to an appointment by traversing the appointment's address via the lives_in table.",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {
                        "type": "integer"
                    }
                },
                "required": ["appointment_id"]
            }
        }
    },

    # Address Management Tools
    # These tools handle address searching and retrieval
    
    {
        "type": "function",
        "function": {
            "name": "find_address_by_text",
            "description": "Search for addresses using text. Searches across street name, postal code, and city name. CRITICAL: Use this FIRST when user provides an address as text (e.g., 'Danmarksgade 7 9000 Aalborg') to get the address_id needed for other operations like creating appointments. Returns list of matching addresses with their IDs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_text": {
                        "type": "string",
                        "description": "Text to search for in addresses (street, postal code, city)"
                    }
                },
                "required": ["search_text"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_address_by_id",
            "description": "Get specific address details by address ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "address_id": {
                        "type": "integer",
                        "description": "The ID of the address to retrieve"
                    }
                },
                "required": ["address_id"]
            }
        }
    },
]