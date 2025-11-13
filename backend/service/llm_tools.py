# backend/llm_tools.py
# OpenAI function-calling + integration to our DB_read.py

from typing import Any, Dict, List, Optional
from openai import OpenAI
from database.DB_read import DB_read
from private_settings import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)            # reads OPENAI_API_KEY from private_settings
db = DB_read()               # Our data access layer

# -----------------------------
# Systemprompt: english assistant
# -----------------------------
SYSTEM_PROMPT = """
You are a helper in our booking web app. Always respond in English.
When the user requests data (customers, addresses, appointments), you must call the available tools.
Never guess data if you can look it up.
When returning lists, keep them short and manageable (use bullet points).
If nothing is found, say so kindly and suggest next steps.
"""

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

# -----------------------------
# Tool-executor: binder tools -> DB_read
# Tool-execution is a separate function for clarity. Binder tool-names to DB_read calls.
# -----------------------------
def _execute_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]: # Executes a tool by name with given arguments.
    try:
        if name == "list_customers":
            rows = db.search_customers(arguments.get("query", ""), arguments.get("limit", 20))
            return {"customers": rows}

        if name == "list_customers_by_name":
            # brug samme søgning, men saml fornavn+efternavn som query
            name_q = (arguments.get("name") or "").strip()
            surname_q = (arguments.get("surname") or "").strip()
            query = (name_q + " " + surname_q).strip()
            rows = db.search_customers(query=query, limit=20)
            return {"customers": rows}

        if name == "get_customer_by_email":
            row = db.get_customer_by_email(arguments["email"])
            return {"customer": row}

        if name == "get_customer_by_id":
            row = db.get_customer_by_id(arguments["customer_id"])
            return {"customer": row}

        if name == "get_customer_addresses":
            rows = db.get_addresses_for_customer_name_or_email(arguments["name_or_email"])
            return {"addresses": rows}

        if name == "get_appointments_by_address_id":
            rows = db.get_appointments_by_address_id(arguments["address_id"])
            return {"appointments": rows}

        if name == "get_appointment_by_id":
            row = db.get_appointment_by_id(arguments["appointment_id"])
            return {"appointment": row}

        return {"error": f"Ukendt tool: {name}"}
    except Exception as e:
        return {"error": f"Tool '{name}' fejlede: {e}"}

# -----------------------------
# Organizing: chat-loop
# -----------------------------
def chat_with_tools(user_message: str, chat_history: Optional[List[Dict[str, str]]] = None, model: str = "gpt-5") -> str:
    """
    Called from Flask-route. Sends the user's message to the model,
    handles tool-calls, and returns a final, formulated response in Danish.
    """
    messages: List[Dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    if chat_history:
        messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=0.2,
    )
    msg = resp.choices[0].message

    # loop mens modellen vil kalde tools
    while getattr(msg, "tool_calls", None):
        tool_outputs: List[Dict[str, Any]] = []
        for tc in msg.tool_calls:
            import json
            tool_name = tc.function.name
            args = json.loads(tc.function.arguments or "{}")
            result = _execute_tool(tool_name, args)

            tool_outputs.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "name": tool_name,
                "content": json.dumps(result, ensure_ascii=False)
            })

        # giv modellen tool-resultaterne så den kan formulere et svar til brugeren
        messages.append({"role": "assistant", "tool_calls": msg.tool_calls})
        messages.extend(tool_outputs)

        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
        )
        msg = resp.choices[0].message

    return msg.content or "I found nothing to respond to."
