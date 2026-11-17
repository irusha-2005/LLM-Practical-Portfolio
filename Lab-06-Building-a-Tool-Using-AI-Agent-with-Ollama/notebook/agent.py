import json
import time
import subprocess
import urllib.request
import pyautogui

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"

# ---------- Calculator tool ----------
def open_calculator(expression):
    expression = str(expression).replace("x", "*").replace("×", "*").replace(" ", "")
    allowed = "0123456789+-*/()."
    if not expression or any(ch not in allowed for ch in expression):
        return "Invalid expression."

    print("[EXECUTING] Opening Windows Calculator...")
    subprocess.Popen("calc.exe")
    time.sleep(2)
    pyautogui.typewrite(expression, interval=0.1)
    pyautogui.press("enter")

    answer = eval(expression)
    return f"Entered {expression} into Calculator. Result = {answer}"

# ---------- Register the tool with the LLM ----------
tools = [
    {
        "type": "function",
        "function": {
            "name": "open_calculator",
            "description": "Open Windows Calculator and calculate a math expression such as 7*4. Use only numbers and + - * / ( )",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "The math expression, for example 7*4"}
                },
                "required": ["expression"],
            },
        },
    }
]

available_functions = {"open_calculator": open_calculator}

# ---------- Talk to the LLM ----------
def chat(messages):
    body = json.dumps({
        "model": MODEL,
        "messages": messages,
        "tools": tools,
        "stream": False,
        "options": {"temperature": 0},
    }).encode("utf-8")
    request = urllib.request.Request(
        OLLAMA_URL, data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())["message"]

# ---------- Agent execution loop ----------
messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant. When the user asks you to calculate "
                   "something, you MUST call the open_calculator tool. "
                   "Never calculate the answer yourself.",
    }
]

print("Calculator Agent ready. Type 'exit' to stop.")

while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ["exit", "quit"]:
        break

    messages.append({"role": "user", "content": user_input})
    reply = chat(messages)
    messages.append(reply)

    if reply.get("tool_calls"):
        for call in reply["tool_calls"]:
            name = call["function"]["name"]
            args = call["function"]["arguments"]
            print("\n[TOOL SELECTED]", name)
            print("[TOOL ARGUMENTS]", args)
            result = available_functions[name](**args)
            print("[TOOL RESULT]", result)
            messages.append({"role": "tool", "content": result, "tool_name": name})
        final = chat(messages)
        messages.append(final)
        print("\nAgent:", final["content"])
    else:
        print("\nAgent:", reply["content"])