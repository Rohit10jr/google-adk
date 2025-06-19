# main_agent.py

from google.adk.agents import Agent
import pandas as pd
from typing import List, Dict, Union, Any, Optional
import os
from google.adk.sessions import InMemorySessionService
from google.adk.tools.tool_context import ToolContext
from google.adk.runners import Runner
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
import random 
from google.adk.tools.base_tool import BaseTool

def block_keyword_model_guardrail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Inspects the latest user message blocked words. If found, rejects the LLM call
    and returns a predefined LlmResponse. Otherwise, returns None to proceed.
    """
    agent_name = callback_context.agent_name # Get the name of the agent whose model call is being intercepted
    print(f"--- Callback: block_keyword_guardrail running for agent: {agent_name} ---")

    # Extract the text from the latest user message in the request history
    last_user_message_text = ""
    if llm_request.contents:
        # Find the most recent message with role 'user'
        for content in reversed(llm_request.contents):
            if content.role == 'user' and content.parts:
                # Assuming text is in the first part for simplicity
                if content.parts[0].text:
                    last_user_message_text = content.parts[0].text
                    break # Found the last user message text

    print(f"--- Callback: Inspecting last user message: '{last_user_message_text[:100]}...' ---") # Log first 100 chars

    # --- Guardrail Logic ---
    # keyword_to_block = "BLOCK"
    keywords_to_block = ["STUPID", "BLOCK"]

    blocked_responses = [
        "I'm sorry, I cannot process this request as it contains inappropriate language.",
        "This query cannot be processed due to the presence of a blocked word.",
        "To maintain a respectful environment, I am unable to respond to messages containing certain terms.",
        "Your request has been flagged and cannot be completed.",
        "I cannot proceed with this request. Please rephrase your query without using blocked words."
    ]

    for keyword in keywords_to_block:
        if keyword in last_user_message_text.upper():
            print(f"--- Callback: Found '{keyword}'. Blocking LLM call! ---")
            callback_context.state["guardrail_block_keyword_triggered"] = True
            print(f"--- Callback: Set state 'guardrail_block_keyword_triggered': True ---")

            random_message = random.choice(blocked_responses)

            # Return a response indicating the block
            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=random_message)],
                    # parts=[types.Part(text=f"I cannot process this request because it contains a blocked term.")],
                )
            )

    # If the loop completes without finding any blocked keywords
    print(f"--- Callback: No blocked keywords found. Allowing LLM call for {agent_name}. ---")
    return None # Returning None signals ADK to continue normally

# print("block_keyword_guardrail function defined.")

def block_hsn_codes_tool_guardrail(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """
    Checks if 'get_weather_stateful' is called for 'Paris'.
    If so, blocks the tool execution and returns a specific error dictionary.
    Otherwise, allows the tool call to proceed by returning None.
    """
    tool_name = tool.name
    agent_name = tool_context.agent_name # Agent attempting the tool call
    print(f"--- Callback: block_hsn_codes_tool_guardrail running for tool '{tool_name}' in agent '{agent_name}' ---")
    print(f"--- Callback: Inspecting args: {args} ---")

    # --- Guardrail Logic ---
    # 1. Check if the correct tool is being called
    target_tool_name = "hsn_code_validation_tool"
    if tool_name == target_tool_name:
        
        # 2. Get the list of HSN codes from 'args' using the correct keyword: "hsn_inputs"
        # Provide an empty list as a default to prevent errors if it's missing.
        hsn_codes_to_check = args.get("hsn_inputs", [])

        guardrail_blocked_responses = [
            "I'm sorry, but I cannot process the validation for the provided code due to a policy restriction.",
            "This particular HSN/SAC code cannot be validated using this tool. Please check the code or try a different method.",
            "The request was blocked. There is a restriction on processing this specific type of input.",
            "Validation for this category of codes is currently restricted. The operation could not be completed.",
            "I am unable to complete the validation as the provided code falls under a restricted category.",
            "This request could not be processed. The input is valid in format but is restricted by system policy.",
            "Processing for this code has been disabled. Please verify your input or contact support for more information on this category."
        ]

        if not hsn_codes_to_check:
            # No codes found in the arguments, so nothing to block. Allow to proceed.
            return None

        # 3. Implement your blocking logic
        for code in hsn_codes_to_check:
            if isinstance(code, str) and code.strip().startswith("99"):
                blocked_code = code
                print(f"--- Callback: Detected blocked HSN code '{blocked_code}'. Blocking tool execution! ---")
                
                # Optionally update state to record the block
                tool_context.state["guardrail_hsn_block_triggered"] = True
                
                # 4. Return a dictionary that matches the tool's expected error output format.
                # This becomes the tool's result, skipping the actual tool run.
                error_message = random.choice(guardrail_blocked_responses)
                # error_message = f"Policy restriction: Validation for HSN code '{blocked_code}' (Services) is not allowed through this tool."

                
                # This should be a list of dictionaries, just like your real tool's output
                return [{
                    "input_hsn": blocked_code,
                    "is_valid": False,
                    "reason_code": "BLOCKED_BY_GUARDRAIL",
                    "message": error_message
                }]
        
        # If the loop completes without finding any blocked codes
        print(f"--- Callback: All HSN codes are allowed. Proceeding with tool execution. ---")

    # If it's not the target tool or no codes were blocked, allow the call to proceed.
    return None


print("✅ block_paris_tool_guardrail function defined.")

# def load_hsn_data(file_path: str):
def load_hsn_data(file_path: str) -> Dict[str, str]:
    """
    Loads HSN data from an Excel file into an efficient in-memory dictionary.
    This function is called once when the application starts.
    """
    print(f"--- Initializing HSN Data Store from: {file_path} ---")
    if not os.path.exists(file_path):
        print(f"--- CRITICAL ERROR: HSN master file not found at '{file_path}'. The validation tool will be non-functional. ---")
        return {}

    try:
        df = pd.read_excel(file_path, dtype={'HSNCode': str})

        if 'HSNCode' not in df.columns or 'Description' not in df.columns:
            print("--- CRITICAL ERROR: Excel file must contain 'HSNCode' and 'Description' columns. ---")
            return {}

        df.dropna(subset=['HSNCode'], inplace=True)
        df['HSNCode'] = df['HSNCode'].str.strip()
        hsn_map = pd.Series(df.Description.values, index=df.HSNCode).to_dict()
        
        print(f"--- Successfully loaded {len(hsn_map)} HSN codes into memory. ---")
        return hsn_map

    except Exception as e:
        print(f"--- CRITICAL ERROR: An error occurred while reading the Excel file: {e} ---")
        return {}

# Load the data into a global variable. This is our in-memory data store.
script_dir = os.path.dirname(__file__) # The directory where main_agent.py is located
file_path = os.path.join(script_dir, "HSN_SAC.xlsx")
hsn_master_data = load_hsn_data(file_path)
# hsn_master_data = load_hsn_data("HSN_SAC.xlsx")


# def hsn_code_validation_tool(hsn_inputs: Union[str, List[str]]):
def hsn_code_validation_tool(hsn_inputs: List[str], tool_context:ToolContext) -> List[Dict[str, Any]]:
    """
    Validates one or more HSN codes against the pre-loaded HSN master data.
    This tool should be used for all HSN validation requests. It takes either a 
    single HSN code as a string or a list of HSN codes as strings.
    """
    print(f"--- Tool 'hsn_code_validation_tool' called with: {hsn_inputs} ---")
    
    # Check if the data store was loaded successfully at 
    if not hsn_master_data:
         return [{
            "input_hsn": str(hsn_inputs),
            "is_valid": False,
            "reason_code": "DATASTORE_UNAVAILABLE",
            "message": "The HSN master data failed to load at startup. Cannot perform validation."
        }]

    # The agent will call this tool with a list, so we can remove redundant type checks.
    if not isinstance(hsn_inputs, list):
         return [{
            "input_hsn": str(hsn_inputs), "is_valid": False,
            "reason_code": "INVALID_INPUT_TYPE",
            "message": "Input must be a list of strings."
        }]

    results = []
    for code in hsn_inputs:
    # for code in codes_to_validate:
        # Perform all validation checks as before
        if not isinstance(code, str):
            results.append({"input_hsn": str(code), "is_valid": False, "reason_code": "INVALID_ITEM_TYPE", "message": "Each HSN code must be a string."})
            continue

        clean_code = code.strip()

        if not clean_code.isdigit() or len(clean_code) not in {2, 4, 6, 8}:
            results.append({"input_hsn": code, "is_valid": False, "reason_code": "INVALID_FORMAT", "message": "HSN code must be numeric and 2, 4, 6, or 8 digits long."})
            continue

        # This is now an extremely fast lookup in the in-memory dictionary
        description = hsn_master_data.get(clean_code)

        if description:
            results.append({"input_hsn": code, "is_valid": True, "description": description, "message": "HSN code is valid."})
        else:
            results.append({"input_hsn": code, "is_valid": False, "reason_code": "NOT_FOUND", "message": "HSN code not found in master data."})

    tool_context.state["hsn_tool_last_result"] = results

    return results


session_service_stateful = InMemorySessionService()

APP_NAME = "hsn_code_agent"
SESSION_ID_STATEFUL = "session_state_demo_001"
USER_ID_STATEFUL = "user_state_demo"

# initial_state = {
#     "user_preference": "give funny response"
# }


session_stateful = session_service_stateful.create_session(
    app_name=APP_NAME, 
    user_id=USER_ID_STATEFUL,
    session_id=SESSION_ID_STATEFUL
    # state=initial_state 
)

# session_service_stateful.create_session(
#     app_name=APP_NAME, 
#     user_id=USER_ID_STATEFUL,
#     session_id=SESSION_ID_STATEFUL
# )

print(f"Session '{SESSION_ID_STATEFUL}' created for user '{USER_ID_STATEFUL}'.")

retrieved_session = session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id=USER_ID_STATEFUL,
                                                         session_id = SESSION_ID_STATEFUL)

# print("\n--- Initial Session State ---")
# if retrieved_session:
#     print(retrieved_session)
# else:
#     print("Error: Could not retrieve session.")

# --- Part 3: Initialize the Root Agent ---

root_agent_stateful = None
runner_root_stateful = None

# if hsn_code_validation_tool in globals():  

root_agent = Agent(
    name="hsn_code_agent",
    # Consider using the latest flash model for best performance
    model="gemini-2.0-flash",
    description="Agent to validate and look up HSN codes using a preloaded master data file.",
    instruction="""
    You are a helpful and efficient assistant for validating HSN codes.
    Your primary goal is to understand the user's request, identify any HSN codes mentioned,
    and use the provided 'hsn_code_validation_tool' to check their validity.
    Present the results from the tool to the user in a clear, easy-to-read format.
    If a code is valid, state its description. If invalid, state the reason.
    """,
    tools=[hsn_code_validation_tool],
    output_key="hsn_agent_last_response",
    before_model_callback=block_keyword_model_guardrail, 
    before_tool_callback=block_hsn_codes_tool_guardrail
)

print("\n--- Agent configuration complete. Ready for 'adk web' command. ---")

# else:
#     print(" Cannot create stateful root agent. Prerequisites missing.")
#     if 'hsn_code_validation_tool' not in globals(): print(" - hsn_code_validation_tool  missing.")
