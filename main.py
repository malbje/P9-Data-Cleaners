# app_chat.py
# Kør LLM + function calling for list_customers_by_name (uden MCP/Cursor)

from openai import OpenAI
import json
import private_settings  # indeholder OPENAI_API_KEY
from backend.llm_tools import TOOLS
from database.DB_read import list_customers, list_customers_by_name, get_customer_by_email, add_address, update_customer_address, delete_customer, add_customer


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
