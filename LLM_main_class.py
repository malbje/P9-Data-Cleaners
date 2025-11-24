# ---------------------------------------------
# This file holds the class used to handle our chat_gpt prompts, 
# Used by creating a LLM_conversation object and calling its ask_llm() method.
# 
# This is supposed to work just like the LLM_main.py file and it's funcitons, 
# but it's a class to each chat-gpt conversation can remember it's own chat history with all the tool calls.
# ---------------------------------------------

from openai import OpenAI
import private_settings  # Contains OPENAI_API_KEY - referenced from private_settings.py
from database.DB_read import DB_read
from database.DB_write import DB_write
import LLM_prompts
from backend.service.llm_tools import TOOLS  # Tool definitions for OpenAI function calling - referenced from backend/llm_tools.py
from backend.service.weather_service import get_precipitation
import json

class LLM_Conversation:
    """
    Class to handle a conversation with chat_gpt that can call tools and remember chat history.
    """

    # A conversation needs the model:
    client: OpenAI

    # Tool use tracker. Should never be more than 10 tool calls in a conversation
    tool_use_count: int = 0
    
    # Constructor
    def __init__(self):
        """
        Constructor for LLM_Conversation class.
        Initializes Chat_GPT client, Database access, and chat history with rules and case.
        """
        # A conversation needs the model:
        LLM_Conversation.client = OpenAI(api_key=private_settings.OPENAI_API_KEY)

        # Our model needs access to out database:
        self.reader = DB_read()
        self.writer = DB_write()

        # A conversation needs a chat history:
        # That history starts with the rules we have for the chat.
        self.messages: list[dict[str, str | List[ChatCompletionMessageToolCallUnion] | None]] = [{ #type:ignore
            "role": "system", "content": LLM_prompts.rules}]
        
        # A conversation needs a case
        self.messages.append({"role": "system", "content": LLM_prompts.case_anna_mikkel})

    # Method for tool that prompts chat to change intent.
    def choose_case(self) -> str | None:
        
        # Append the request to chat history

        temp_messages: list[dict] = self.messages.copy()

        temp_messages.pop() # To remove the last message, which is a list of tool_calls

        temp_messages.append({"role": "user", "content": """
                              Based on the chat history and your rules-based approtch, categorize the user as belonging to one of these two cases, 
                              then respond only with the name of each case in lower case. The two cases are:
                              1 - name: jonas, defintion: would like appointments to be placed on the day of the week with the least rain.
                              2 - name: anna_mikkel, definition: would like appointments to be places on the day of the week after the day where it rains the most"""
                              })

        # Ask chat_gpt to choose case
        resp = LLM_Conversation.client.chat.completions.create(
            model="gpt-5",
            messages = temp_messages, #type: ignore
            # tools = TOOLS,            #type: ignore
            # tool_choice = "auto"
        )

        case_chosen: str | None = resp.choices[0].message.content

        if case_chosen == "jonas":
            self.messages[1] = {"role": "system", "content": LLM_prompts.case_jonas}
        elif case_chosen == "anna_mikkel":
            self.messages[1] = {"role": "system", "content": LLM_prompts.case_anna_mikkel}

        print(f'Case chosen: {case_chosen}')

        return case_chosen

    # Private method *only* called by ask_llm()
    def __asking_llm(self) -> None:
        """
        Private method to prompt chat_gpt, handle tool calls, and update chat history recursively.

        Recustion stops when no new tool calls are made and a natural language response is returned by chat_gpt.
        """

        print("called __asking_llm() :D")
        if LLM_Conversation.tool_use_count >= 10:
            raise RuntimeError("Using Too Many Tools (10) - Elia")

        # Now it's time to ask the chat.
        # resp er et objekt af klassen ChatCompletion
        resp = LLM_Conversation.client.chat.completions.create(
            model="gpt-5",
            messages = self.messages, #type: ignore
            tools = TOOLS,            #type: ignore
            tool_choice = "auto"
        )

        # Now it's time to get the result of the prompt:
        # 'choices[]' is a list of Choice objects
        # Choice object has a 'message' attribute of type ChatCompletionMessage
        message_role: str = resp.choices[0].message.role
        text_response: str | None = resp.choices[0].message.content
        tools_used: list[ChatCompletionMessageToolCallUnion] | None = resp.choices[0].message.tool_calls #type: ignore

        # Appending those results to the chat history to be remembered:
        self.messages.append({
            "role": "assistant", 
            "content": text_response, 
            "tool_calls": tools_used
        })

        # Get result of chosen tool and append it to 'self.messages'
        if tools_used and message_role == "assistant":

            LLM_Conversation.tool_use_count += 1
            print(f"TOOL was decided. This is nr. {LLM_Conversation.tool_use_count}")

            # If tool used, get the info from the latest list of tool calls
            last_tool_call: list = self.messages[-1]['tool_calls'][0] #type: ignore

            # Form that tool call, get id and name
            call_id = last_tool_call.id #type:ignore
            call_name = last_tool_call.function.name #type:ignore

            # Don't ask me, honestly
            args = json.loads(last_tool_call.function.arguments or "{}") #type: ignore

            # Gets the diffente words form the list of args (generally)
            # the '*' before 'keys' says that the function can take any number of string arguments, and packs them together in a tuple
            def _pick(*keys: str, default = None):
                for key in keys:
                    if key in args:
                        return args.get(key)
                return default
                   
            if call_name == "list_customers":
                result = self.reader.get_all_customers()
            elif call_name == "list_customers_by_name":
                # model may pass 'query' or 'name'
                q = _pick('query', 'name')
                result = self.reader.search_customers_by_name(q) if q else self.reader.search_customers_by_name(None)
            elif call_name == "add_customer":
                # map to create_customer(name, surname, email)
                name_v = _pick('name')
                surname_v = _pick('surname')
                email_v = _pick('email')
                result = self.writer.create_customer(name_v, surname_v, email_v)
            elif call_name == "add_appointment":
                # expect address_id, date, time, notes (notes optional)
                addr = _pick('address_id', 'addressId', 'address')
                date = _pick('date')
                time = _pick('time')
                notes = _pick('notes', '')
                result = self.writer.create_appointment(addr, date, time, notes) #type: ignore
            elif call_name == "get_customer_by_email":
                result = self.reader.get_customer_by_email(**args)
            elif call_name == "get_customer_by_id":
                result = self.reader.get_customer_by_id(**args)
            elif call_name == "add_address":
                street = _pick('street_and_number', 'street', 'streetAndNumber')
                postal = _pick('postal_code', 'postalCode', 'postal')
                city = _pick('city_name', 'city', 'cityName')
                result = self.writer.create_address(street, postal, city)
            elif call_name == "update_customer_address":
                # normalize various possible arg names
                customer_id = _pick('customer_id', 'customerId', 'id')
                address_id = _pick('address_id', 'addressId', 'id')
                city = _pick('city_name', 'city', 'cityName')
                postal = _pick('postal_code', 'postalCode', 'postal')
                street = _pick('street_and_number', 'street', 'streetAndNumber')
                result = self.writer.update_customer_address(customer_id, address_id, city, postal, street)
            elif call_name == "get_appointments_by_address_id":
                result = self.reader.get_appointments_by_address_id(**args)
            elif call_name == "get_appointment_by_id":
                result = self.reader.get_appointment_by_id(**args)
            elif call_name == "delete_customer":
                cid = _pick('customer_id', 'id')
                result = self.writer.delete_customer_by_id(cid)
            elif call_name == "get_customers_by_appointment_id":
                result = self.reader.get_customers_by_appointment_id(**args)
            elif call_name == "get_customers_by_address_id":
                result = self.reader.get_customers_by_address_id(**args)
            elif call_name == "find_address_by_text":
                result = self.reader.find_address_by_text(**args)
            elif call_name == "get_address_by_id":
                result = self.reader.get_address_by_id(**args)
            elif call_name == "get_precipitation":
                result = get_precipitation()
            elif call_name == "choose_case":
                result = self.choose_case()
            else:
                result = {"error": f"Ukendt funktion: {call_name}"}
            
            # add the tool result to messages (chat history)
            self.messages.append({
                "role": "tool",
                "tool_call_id": call_id,
                "name": call_name,
                "content": json.dumps(result, ensure_ascii=False)
            })

            print(self.messages)

            # Recursion. Calls asking_llm to prompt chat_gpt until tools_used = None and it returns a natural language text_response
            self.__asking_llm()

        # Now we have the tool result, time to ask chat_gpt again to get another tool call or a natural language response
        if message_role == "tool" and text_response:
            # Recursion. Calls asking_llm to prompt chat_gpt until tools_used = None and it returns a natural language text_response
            self.__asking_llm()

    # Public method to ask chat_gpt a prompt
    def ask_llm(self, user_prompt: str) -> str:
        """
        The method to ask chat_gpt a prompt. 
        ONLY this method should call __asking_llm().

        Args: user_prompt (str): The prompt from the user, that the chatbot should answer.

        Returns: str: Natural language response from chat_gpt.
        """

        # When asking the chatbot a prompt, it first needs to be appended to the existing chat history:
        self.messages.append({"role": "user", "content": user_prompt})

        # Ask chat_gpt for potential tool calls and natural language response
        self.__asking_llm()

        # Get the final text response from the last message
        text_response: str | None = self.messages[-1]["content"]
        if text_response == None:
            text_response = 'Failed to ask Chat_GPT'
        
        return text_response 

# Used for chatting with our chat_gpt in the terminal
if __name__ == "__main__":
    # Start the interactive chat session
    print("=== DataCleaners Interactive Assistant ===")
    print("Skriv 'exit' for at afslutte\n")

    chatbot = LLM_Conversation()

    while True:
        # Get user input
        # input is a blocking function, meaning that it's call pauses the program until the user inputs something
        user_input: str = input("Brugeren skriver: ").strip()
        
        if 'exit' in user_input.lower():
            print("Tak for denne gang!")
            break
        
        # If user_input == None, then 'continue' will skip the rest of this iteration of the loop and start the loop over
        if not user_input:
            continue

        # Get response from assistant
        response: str = chatbot.ask_llm(user_input)

        print(f"The whole chat history: {chatbot.messages}")

        print(f"\nAssistent: {response}\n")
