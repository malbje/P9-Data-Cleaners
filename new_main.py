# app_chat.py
# Kør LLM + function calling for list_customers_by_name (uden MCP/Cursor)

from openai import OpenAI
import json
import private_settings  # indeholder OPENAI_API_KEY
from database.DB_access import get_connection

# ----------------------------
# 1) Din "rigtige" Python-funktion (genbrug af din DB-adgang)
# ----------------------------
def list_customers_by_name(customer_name: str):
    """Find kunder via navn (LIKE-søgning). Returnerer liste af dicts."""
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
    prompt = "Vis kunder med navn der indeholder 'Jensen', og list id + navn + email pænt."
    answer = ask_llm(prompt)
    print(answer)
