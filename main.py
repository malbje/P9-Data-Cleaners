# app_chat.py
# Kør LLM + function calling for list_customers_by_name (uden MCP/Cursor)

from mysql.connector import IntegrityError
from openai import OpenAI
import json
import private_settings  # indeholder OPENAI_API_KEY
from database.DB_access import get_connection

# ----------------------------
# 1) Din "rigtige" Python-funktion (genbrug af din DB-adgang)
# ----------------------------
def list_customers():
    """
    Hent alle kunder fra databasen.
    """
    db = get_connection()
    try: 
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT id, name, surname, address, email, notification_preference FROM customers ORDER BY id")
        return cur.fetchall()
    finally:
        db.close()


def list_customers_by_name(name: str, surname: str):
    """
    Find kunder via navn og efternavn (LIKE-søgning).
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            "SELECT id, name, surname, email, notification_preference FROM customers WHERE name LIKE %s AND surname LIKE %s ORDER BY id", 
            (f"%{name}%", f"%{surname}%")
        )
        return cur.fetchall()
    finally:
        db.close()

def get_customer_by_email(email: str):
    """
    Hent en kunde via email.
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            "SELECT id, name, surname, address, email, notification_preference FROM customers WHERE email = %s",
            (email,),
        )
        return cur.fetchone()  # Antager email er unik, så vi forventer kun én række
    finally:
        db.close()


def add_customer(name: str, surname: str, email: str, notification_preference: str):
    """
    Opret en kunde. Fejler hvis email allerede findes.
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            "INSERT INTO customers (name, surname, email, notification_preference) VALUES (%s, %s, %s, %s)",
            (name, surname, email, notification_preference),
        )
        db.commit()
        return {"id": cur.lastrowid, "name": name, "surname": surname, "email": email, "notification_preference": notification_preference}
    except IntegrityError as e:
        return {"error": "Email already exists", "details": str(e)}

def add_address(customer_id: int, address: str):
    """
    Tilføjer en adresse til en kunde baseret på deres ID.
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            "INSERT INTO Address (customer_id, address) VALUES (%s, %s)",
            (customer_id, address),
        )
        db.commit()
        return {"updated_rows": cur.rowcount}
    finally:
        db.close()

def update_customer_address(customer_id: int, address: str):
    """
    Opdaterer en kundes adresse baseret på deres ID.
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            "UPDATE customers SET address = %s WHERE id = %s",
            (address, customer_id),
        )
        db.commit()
        return {"updated_rows": cur.rowcount}
    finally:
        db.close()

def delete_customer(customer_id: int):
    """
    Slet en kunde baseret på deres ID.
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            "DELETE FROM customers WHERE id = %s",
            (customer_id,),
        )
        db.commit()
        return {"deleted_rows": cur.rowcount}
    finally:
        db.close()



# ----------------------------
# 2) Definér tool-schema (JSON Schema) til modellen
# ----------------------------
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
            "description": "Updates a customer's address based on their ID and previous address.",
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
]

# ----------------------------
# 3) Minimal samtale + tool-calling loop
# ----------------------------
def ask_llm(user_prompt: str):
    client = OpenAI(api_key=private_settings.OPENAI_API_KEY)

    messages = [
        {"role": "system", "content": "Du er en assistent for et kundekartotek. Brug tools når der skal hentes data."},
        {"role": "user", "content": user_prompt},
    ]

    # Første kald: giv modellen muligheden for at foreslå tool-kald
    resp = client.chat.completions.create(
        model="gpt-5",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )

    assistant_msg = resp.choices[0].message
    messages.append({"role": "assistant", "content": assistant_msg.content or "", "tool_calls": assistant_msg.tool_calls})

    # Hvis modellen vil kalde et tool, udfør det og send resultatet tilbage som role="tool"
    tool_calls = assistant_msg.tool_calls or []
    for call in tool_calls:
        name = call.function.name
        args = json.loads(call.function.arguments or "{}")

        if name == "list_customers":
            result = list_customers(**args)
        elif name == "list_customers_by_name":
            result = list_customers_by_name(**args)
        elif name == "add_customer":
            result = add_customer(**args)
        elif name == "get_customer_by_email":
            result = get_customer_by_email(**args)
        elif name == "add_address":
            result = add_address(**args)
        elif name == "update_customer_address":
            result = update_customer_address(**args)
        elif name == "delete_customer":
            result = delete_customer(**args)
        else:
            result = {"error": f"Ukendt funktion: {name}"}

        # svar tilbage til modellen med tool-resultatet (vigtigt: tool_call_id)
        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "name": name,
            "content": json.dumps(result, ensure_ascii=False),
        })

    # Andet kald: få det endelige, naturlige svar til brugeren
    final = client.chat.completions.create(
        model="gpt-5",
        messages=messages
    )
    return final.choices[0].message.content


# ----------------------------
# 4) Kør eksempel
# ----------------------------
if __name__ == "__main__":
    # Eksempel: spørg efter kunder hvor navnet indeholder "Jensen"
    prompt = "tilføj en kunde med navn 'Lars Larsen', adresse 'Nørregade 1, 8000 Aarhus' og email 'lars@example.com'"
    answer = ask_llm(prompt)
    print(answer)
