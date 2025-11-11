# main.py - Entry point for DataCleaners system with OpenAI GPT-5 integration.
# Enables natural language database interaction through function calling.

from openai import OpenAI
import json
import private_settings  # Contains OPENAI_API_KEY - referenced from private_settings.py
from backend.service.llm_tools import TOOLS  # Tool definitions for OpenAI function calling - referenced from backend/llm_tools.py
from database.DB_read import DB_read
from database.DB_write import DB_write


def ask_llm(user_prompt: str, conversation_context: list = None):
    """
    Process natural language prompts through OpenAI with database function calling.
    
    Args:
        user_prompt (str): Natural language request
        conversation_context (list): Previous messages for context
        
    Returns:
        str: Natural language response with database results
    """
    client = OpenAI(api_key=private_settings.OPENAI_API_KEY)

    # Instantiate DB access classes (read/write). These are thin, stateless wrappers
    # that open connections only when their methods are called.
    reader = DB_read()
    writer = DB_write()

    # Start med system message og tilføj samtale kontekst hvis den findes
    messages = [
        {"role": "system", "content": """Du er en assistent for et rengøringsfirma med fokus på deres kundekartotek. 

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

        # Map tool names to DB class methods. Accept multiple common argument
        # key variants to be resilient to different model argument naming.
        def _pick(*keys, default=None):
            for k in keys:
                if k in args:
                    return args.get(k)
            return default

        if name == "list_customers":
            result = reader.get_all_customers()
        elif name == "list_customers_by_name":
            # model may pass 'query' or 'name'
            q = _pick('query', 'name')
            result = reader.search_customers_by_name(q) if q else reader.search_customers_by_name(None)
        elif name == "add_customer":
            # map to create_customer(name, surname, email)
            name_v = _pick('name')
            surname_v = _pick('surname')
            email_v = _pick('email')
            result = writer.create_customer(name_v, surname_v, email_v)
        elif name == "add_appointment":
            # expect address_id, date, time, notes (notes optional)
            addr = _pick('address_id', 'addressId', 'address')
            date = _pick('date')
            time = _pick('time')
            notes = _pick('notes', '')
            result = writer.create_appointment(addr, date, time, notes)
        elif name == "get_customer_by_email":
            result = reader.get_customer_by_email(**args)
        elif name == "get_customer_by_id":
            result = reader.get_customer_by_id(**args)
        elif name == "add_address":
            street = _pick('street_and_number', 'street', 'streetAndNumber')
            postal = _pick('postal_code', 'postalCode', 'postal')
            city = _pick('city_name', 'city', 'cityName')
            result = writer.create_address(street, postal, city)
        elif name == "update_customer_address":
            # normalize various possible arg names
            customer_id = _pick('customer_id', 'customerId', 'id')
            address_id = _pick('address_id', 'addressId', 'id')
            city = _pick('city_name', 'city', 'cityName')
            postal = _pick('postal_code', 'postalCode', 'postal')
            street = _pick('street_and_number', 'street', 'streetAndNumber')
            result = writer.update_customer_address(customer_id, address_id, city, postal, street)
        elif name == "get_appointments_by_address_id":
            result = reader.get_appointments_by_address_id(**args)
        elif name == "get_appointment_by_id":
            result = reader.get_appointment_by_id(**args)
        elif name == "delete_customer":
            cid = _pick('customer_id', 'id')
            result = writer.delete_customer_by_id(cid)
        elif name == "get_customers_by_appointment_id":
            result = reader.get_customers_by_appointment_id(**args)
        elif name == "get_customers_by_address_id":
            result = reader.get_customers_by_address_id(**args)
        elif name == "find_address_by_text":
            result = reader.find_address_by_text(**args)
        elif name == "get_address_by_id":
            result = reader.get_address_by_id(**args)
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
        messages = messages
    )
    return final.choices[0].message.content


def interactive_chat():
    """
    Terminal-based chat interface with conversation memory.
    
    Returns:
        None
    """
    print("=== DataCleaners Interactive Assistant ===")
    print("Skriv 'exit' for at afslutte\n")
    
    conversation_history: list = []
    
    while True:
        # Get user input
        user_input: str = input("Du: ").strip()
        
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


if __name__ == "__main__":
    # Start the interactive chat session
    interactive_chat()
