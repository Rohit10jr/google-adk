from google.adk.agents import Agent

def get_hsn_code(code: str):
    """
    returns the matching hsn code values
    """
    if code == "100":
        return {
            "status" : "success",
            "result" : "automobile"
        }
    elif code == "1000":
        return { 
            "status" : "success",
            "result" : "bike and cars"
            }
    return {
        "status" : "not found",
        "result": "none"
        }        

root_agent = Agent(
    name = "hsn_code_agent",
    model="gemini-2.0-flash",
    # model = "gemini-2.0-flash-exp",
    # model="gemini-2.0-flash-live-001",
    description = "agent to find the hsn code from given code number",
    instruction = "your are a helpful agent who can have conversation and find hsn code details using the given tools",
    tools = [get_hsn_code]
)
