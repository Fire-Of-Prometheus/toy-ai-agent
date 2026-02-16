import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
import argparse
from call_function import available_functions, call_function

parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument("user_prompt", type=str, help="User prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()

def main ():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    if api_key == None:
        raise RuntimeError("GEMINI_API key is not present")


    model_name = "gemini-2.5-flash"
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]


    client = genai.Client(api_key=api_key)

    for _ in range(20):
        response = client.models.generate_content(
            model=model_name,
            contents=messages,
            config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt),
        )

        if response.usage_metadata == None:
            raise RuntimeError("GEMINI_API Request Failed")

        if response.candidates:
            for cdt in response.candidates:
                messages.append(cdt.content)

        if args.verbose:
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

        function_responses = []
        if response.function_calls:
            for function_call in response.function_calls:
                print(f"Calling function: {function_call.name}({function_call.args})")
                function_call_result = call_function(function_call, args.verbose)
                if not function_call_result.parts:
                    raise Exception("Error: Something went wrong with the function call.")
                if not function_call_result.parts[0].function_response:
                    raise Exception("Error: Something went wrong with the function call.")
                if not function_call_result.parts[0].function_response.response:
                    raise Exception("Error: Something went wrong with the function call.")
                
                function_responses.append(function_call_result.parts[0])

                if args.verbose:
                    print(f"-> {function_call_result.parts[0].function_response.response}")

            messages.append(types.Content(role="user", parts=function_responses))
        else:
            print(response.text)
            return
    print("Error: Function loop entered, no answer was found")
    exit(1)
        
main()

