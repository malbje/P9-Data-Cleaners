# ------------------------------
# main.py – OpenAI integration for DataCleaners customer management
# ------------------------------

from openai import OpenAI
import json
import private_settings  # indeholder OPENAI_API_KEY
from backend.llm_tools import TOOLS
from database.DB_read import (
    add_appointment, get_appointment_by_id, get_appointments_by_address_id, 
    get_customer_by_id, get_customers_by_address_id, list_customers, 
    list_customers_by_name, get_customer_by_email, add_address, 
    update_customer_address, delete_customer, add_customer, 
    get_customers_by_appointment_id, find_address_by_text, get_address_by_id
)


def ask_llm(user_prompt: str, conversation_context: list = None):
    """
    Process user prompt using OpenAI with function calling for database operations.
    
    Args:
        user_prompt (str): The user's request in natural language
        conversation_context (list): Previous messages for context
        
    Returns:
        str: OpenAI's response after processing tools and data
    """
    client = OpenAI(api_key=private_settings.OPENAI_API_KEY)

    # Start med system message og tilføj samtale kontekst hvis den findes
    messages = [
        {"role": "system", "content": """Du er en assistent for et kundekartotek. 

ABSOLUT KRITISK REGEL: Du SKAL ALTID bruge de tilgængelige tools til at udføre opgaver. Du må ALDRIG, UNDER NOGEN OMSTÆNDIGHEDER, simulere, gætte eller opfinde resultater.

PÅKRÆVET ADFÆRD:
- Når brugeren beder om at oprette en aftale: SKAL kalde add_appointment funktionen
- Når brugeren beder om kunde-info: SKAL kalde relevante kunde-funktioner  
- Når brugeren beder om adresse-info: SKAL kalde adresse-funktioner
- Når brugeren beder om at finde noget: SKAL bruge søge-funktioner

Du må ALDRIG skrive noget som:
- "Jeg opretter aftalen nu" uden at kalde add_appointment
- "Aftalen er oprettet" uden at have modtaget resultat fra add_appointment
- JSON eksempler eller simulerede resultater

ALTID vent på det faktiske resultat fra funktionerne før du svarer brugeren.

Hvis du mangler information for at udføre en opgave, stil spørgsmål til brugeren."""}
    ]
    
    # Tilføj samtale kontekst hvis den findes
    if conversation_context:
        messages.extend(conversation_context)
    
    # Tilføj den nye bruger besked
    messages.append({"role": "user", "content": user_prompt})

    # Første kald: TVING modellen til at bruge tools eller stille spørgsmål
    resp = client.chat.completions.create(
        model="gpt-5",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"  # Tilbage til auto så den kan stille spørgsmål
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
        elif name == "add_appointment":
            result = add_appointment(**args)
        elif name == "get_customer_by_email":
            result = get_customer_by_email(**args)
        elif name == "get_customer_by_id":
            result = get_customer_by_id(**args)
        elif name == "add_address":
            result = add_address(**args)
        elif name == "update_customer_address":
            result = update_customer_address(**args)
        elif name == "get_appointments_by_address_id":
            result = get_appointments_by_address_id(**args)
        elif name == "get_appointment_by_id":
            result = get_appointment_by_id(**args)
        elif name == "delete_customer":
            result = delete_customer(**args)
        elif name == "get_customers_by_appointment_id":
            result = get_customers_by_appointment_id(**args)
        elif name == "get_customers_by_address_id":
            result = get_customers_by_address_id(**args)
        elif name == "find_address_by_text":
            result = find_address_by_text(**args)
        elif name == "get_address_by_id":
            result = get_address_by_id(**args)
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


# Interactive chat function
def interactive_chat():
    """
    Start an interactive chat session with the assistant.
    """
    print("=== DataCleaners Interactive Assistant ===")
    print("Skriv 'exit' for at afslutte\n")
    
    conversation_history = []
    
    while True:
        # Get user input
        user_input = input("Du: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'afslut']:
            print("Tak for denne gang!")
            break
            
        if not user_input:
            continue
            
        try:
            # Get response from assistant
            response = ask_llm(user_input, conversation_history)
            print(f"\nAssistent: {response}\n")
            
            # Add to conversation history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response})
            
            # Check if the response contains a question - if so, wait for follow-up
            if "?" in response and any(word in response.lower() for word in ["vil du", "skal", "godkend", "angiv", "præferenc", "titel", "varighed"]):
                follow_up = input("Dit svar: ").strip()
                if follow_up:
                    # Process the follow-up response
                    follow_response = ask_llm(follow_up, conversation_history)
                    print(f"\nAssistent: {follow_response}\n")
                    
                    # Add follow-up to history
                    conversation_history.append({"role": "user", "content": follow_up})
                    conversation_history.append({"role": "assistant", "content": follow_response})
            
        except Exception as e:
            print(f"Fejl: {e}\n")


# Demo function for testing
def run_demo():
    """
    Run the original appointment creation test.
    """
    print("=== DataCleaners Appointment Creation Demo ===\n")
    
    # Den originale test du kørte
    prompt = "lav en appointment den 28 november 2025 kl 14:00 for kunden med ID 1 som bor på adressen Danmarksgade 7 9000 aalborg. Der er ingen noter eller preferencer."
    
    print(f"Test prompt: {prompt}\n")
    print("Opretter appointment...\n")
    
    try:
        answer = ask_llm(prompt)
        print("=== Resultat ===")
        print(answer)
        
        # Check if it's asking a question - if so, allow interaction
        if "?" in answer and any(word in answer.lower() for word in ["vil du", "skal", "godkend", "angiv"]):
            print("\n--- Interaktiv del ---")
            response = input("Dit svar: ").strip()
            if response:
                follow_up = ask_llm(response, [
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": answer}
                ])
                print(f"\nAssistent: {follow_up}")
                
    except Exception as e:
        print(f"Fejl: {e}")


if __name__ == "__main__":
    print("Vælg mode:")
    print("1. Demo (original test)")
    print("2. Interaktiv chat")
    
    choice = input("Vælg (1 eller 2): ").strip()
    
    if choice == "1":
        run_demo()
    elif choice == "2":
        interactive_chat()
    else:
        print("Kører demo som standard...")
        run_demo()
