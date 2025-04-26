from langchain.tools import Tool
from agent.prompts.description import TOOL_DESCRIPTION

TOOLS = {}

def tool(name):
    def decorator(func):
        desc = TOOL_DESCRIPTION.get(name, "No description available.")
        tool = Tool.from_function(
            name = name,
            func = func,
            description = desc
        )
        TOOLS[name] = tool
        return func
    return decorator
