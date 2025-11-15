# main.py - Entry point for DataCleaners system with OpenAI GPT-5 integration.
# Enables natural language database interaction through function calling.

from openai import OpenAI
import json
import private_settings  # Contains OPENAI_API_KEY - referenced from private_settings.py
from backend.service.llm_tools import TOOLS  # Tool definitions for OpenAI function calling - referenced from backend/llm_tools.py
from database.DB_read import DB_read
from database.DB_write import DB_write
import LLM_prompts

def ask_llm(
        user_prompt: str, 
        conversation_context: list[dict[str, str]] | None = None
        ) -> str:
    """
    Process natural language prompts through OpenAI with database function calling.
    
    Args:
        user_prompt (str): Natural language request
        conversation_context (list): Previous messages for context
        
    Returns:
        str: Natural language response with database results
    """
    client = OpenAI(api_key=private_settings.OPENAI_API_KEY)

    # Instantiate DB access classes (read/write),
    # that open connections only when their methods are called.
    reader = DB_read()
    writer = DB_write()

    # Rules:
    # 0'th dict in messages list is the prompt with general rules for the chatbot.
    # 1'st dict is the case we are using to further guide the model on specific choices.

    # Start med system message og tilføj samtale kontekst hvis den findes
    messages: list[dict[str, str | List[ChatCompletionMessageToolCallUnion] | None]] = [{ #type: ignore
        "role": "system", "content": LLM_prompts.rules
        }]
    
    # Appending the case of anna and mikkel to the rules prompt
    # messages[0]["content"] += LLM_prompts.case_anna_mikkel
    messages.extend([{
        "role": "system", "content": LLM_prompts.case_anna_mikkel
        }])
    
    # Tilføj samtale kontekst hvis den findes
    if conversation_context:
        messages.extend(conversation_context)
    
    # Tilføj den nye bruger besked
    messages.append({"role": "user", "content": user_prompt})

    # Første kald: TVING modellen til at bruge tools eller stille spørgsmål 
    # (hvordan tvinges?)
    # resp er et objekt af klassen ChatCompletion
    resp = client.chat.completions.create(
        model="gpt-5",
        messages = messages,
        tools = TOOLS,
        tool_choice = "auto"  # Tilbage til auto så den kan stille spørgsmål
    )

    # 'choices[]' is a list of Choice objects
    # each Choice object has a 'message' attribute of type ChatCompletionMessage
    # 'tool_calls' er en liste af ChatCompletionMessageFunctionToolCall

    assistant_msg = resp.choices[0].message
    tools_used: list[ChatCompletionMessageToolCallUnion] | None = assistant_msg.tool_calls #type: ignore
    
    messages.append({
        "role": "assistant", 
        "content": assistant_msg.content, 
        "tool_calls": tools_used
    })

    # Hvis modellen vil kalde et tool, udfør det og send resultatet tilbage som role="tool"
    # If a tool was used, then ChatCompletionMessageFunctionToolCall has a 'function' object with a name and a json list of arguments (str)
    
    # Hvis det første create() kald til chatten resulterede i et tool-kald, skal der kaldes igen for et få et svar på menneske sprog
    if tools_used:

        last_tool_call: list = messages[-1]['tool_calls'][0] #type: ignore

        call_id = last_tool_call.id #type:ignore
        call_name = last_tool_call.function.name #type:ignore

        args = json.loads(last_tool_call.function.arguments or "{}")

        # the '*' before 'keys' says that the function can take any number of string arguments, and packs them together in a tuple
        def _pick(*keys: str, default = None):
            for key in keys:
                if key in args:
                    return args.get(key)
            return default

        if call_name == "list_customers":
            result = reader.get_all_customers()
        elif call_name == "list_customers_by_name":
            # model may pass 'query' or 'name'
            q = _pick('query', 'name')
            result = reader.search_customers_by_name(q) if q else reader.search_customers_by_name(None)
        elif call_name == "add_customer":
            # map to create_customer(name, surname, email)
            name_v = _pick('name')
            surname_v = _pick('surname')
            email_v = _pick('email')
            result = writer.create_customer(name_v, surname_v, email_v)
        elif call_name == "add_appointment":
            # expect address_id, date, time, notes (notes optional)
            addr = _pick('address_id', 'addressId', 'address')
            date = _pick('date')
            time = _pick('time')
            notes = _pick('notes', '')
            result = writer.create_appointment(addr, date, time, notes)
        elif call_name == "get_customer_by_email":
            result = reader.get_customer_by_email(**args)
        elif call_name == "get_customer_by_id":
            result = reader.get_customer_by_id(**args)
        elif call_name == "add_address":
            street = _pick('street_and_number', 'street', 'streetAndNumber')
            postal = _pick('postal_code', 'postalCode', 'postal')
            city = _pick('city_name', 'city', 'cityName')
            result = writer.create_address(street, postal, city)
        elif call_name == "update_customer_address":
            # normalize various possible arg names
            customer_id = _pick('customer_id', 'customerId', 'id')
            address_id = _pick('address_id', 'addressId', 'id')
            city = _pick('city_name', 'city', 'cityName')
            postal = _pick('postal_code', 'postalCode', 'postal')
            street = _pick('street_and_number', 'street', 'streetAndNumber')
            result = writer.update_customer_address(customer_id, address_id, city, postal, street)
        elif call_name == "get_appointments_by_address_id":
            result = reader.get_appointments_by_address_id(**args)
        elif call_name == "get_appointment_by_id":
            result = reader.get_appointment_by_id(**args)
        elif call_name == "delete_customer":
            cid = _pick('customer_id', 'id')
            result = writer.delete_customer_by_id(cid)
        elif call_name == "get_customers_by_appointment_id":
            result = reader.get_customers_by_appointment_id(**args)
        elif call_name == "get_customers_by_address_id":
            result = reader.get_customers_by_address_id(**args)
        elif call_name == "find_address_by_text":
            result = reader.find_address_by_text(**args)
        elif call_name == "get_address_by_id":
            result = reader.get_address_by_id(**args)
        else:
            result = {"error": f"Ukendt funktion: {call_name}"}
        
        # add the tool result to messages (chat history)
        messages.append({
            "role": "tool",
            "tool_call_id": call_id,
            "name": call_name,
            "content": json.dumps(result, ensure_ascii=False)
        })
    
        # get a natural language response from the chat, which uses the result from the tool call that was just appended to messages (chat history)
        final = client.chat.completions.create(
            model = "gpt-5",
            messages = messages,
        )

        # adding the natural language response to messages and returning it
        response2 = final.choices[0].message
        messages.append({"role": "assistant", "content": response2.content})
        print('All messages: ')
        print(messages)
        return response2.content #type: ignore

    print('All messages: ')
    print(messages)
    # the 'content' instance variable is a string
    return assistant_msg.content #type: ignore

def interactive_chat() -> None:
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
        # input is a blocking function, meaning that it's call pauses the program until the user inputs something
        user_input: str = input("Du: ").strip()
        
        if 'exit' in user_input.lower():
            print("Tak for denne gang!")
            break
        
        # If user_input == None, then 'continue' will skip the rest of this iteration of the loop and start the loop over
        if not user_input:
            continue
            
        try:
            # Get response from assistant
            response: str = ask_llm(user_input, conversation_history)
            print(f"\nAssistent: {response}\n")
            
            # Add to conversation history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response})
        

        except Exception as e:
            print(f"Fejl: {e}\n")

if __name__ == "__main__":
    # Start the interactive chat session
    interactive_chat()