# app_chat.py
# Kør LLM + function calling for list_customers_by_name (uden MCP/Cursor)

from sqlite3 import IntegrityError
from openai import OpenAI
import json
import private_settings  # indeholder OPENAI_API_KEY
from database.DB_access import get_connection

# ----------------------------
# 1) Din "rigtige" Python-funktion (genbrug af din DB-adgang)
# ----------------------------
def list_customers_by_name(customer_name: str):
    """Find kunder via navn (LIKE-søgning)"""
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            "SELECT id, name, address, email FROM customers WHERE name LIKE %s ORDER BY id",
            (f"%{customer_name}%",),
        )
        return cur.fetchall()
    finally:
        db.close()


def add_customer(name: str, address: str, email: str):
    """Opret en kunde. Fejler hvis email allerede findes."""
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            "INSERT INTO customers (name, address, email) VALUES (%s, %s, %s)",
            (name, address, email),
        )
        db.commit()
        return {"id": cur.lastrowid, "name": name, "address": address, "email": email}
    except IntegrityError as e:
        return {"error": "Email already exists", "details": str(e)}

# ----------------------------
# 2) Definér tool-schema (JSON Schema) til modellen
# ----------------------------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_customers_by_name",
            "description": "Find kunder via navn (LIKE-søgning). Returnerer en liste af kunder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Navnet (helt eller delvist) på kunden."
                    }
                },
                "required": ["customer_name"]
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
                    "address": {"type": "string"},
                    "email": {"type": "string"}
                },
                "required": ["name", "email"]
            }
        }
    }
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

        if name == "list_customers_by_name":
            result = list_customers_by_name(**args)
        elif name == "add_customer":
            result = add_customer(**args)
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
