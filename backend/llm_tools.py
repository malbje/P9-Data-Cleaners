
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_customers",
            "description": "Get all customers from the database. Returns a list of customers.",
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
            "description": "Find customers by their name and surname (partial match).",
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
    }
]