import os
import json
import time
import ctypes
import platform
import subprocess
import urllib.request
from datetime import datetime
import pyautogui

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"


# ---------- Tool 1: Calculator ----------
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
    return f"Entered {expression} into Calculator. Result = {eval(expression)}"


# ---------- Tool 2: Date and Time ----------
def get_date_time():
    now = datetime.now()
    return now.strftime("Today is %A, %d %B %Y. The time is %I:%M %p.")


# ---------- Tool 3: Notepad ----------
def open_notepad(text):
    print("[EXECUTING] Opening Notepad...")
    subprocess.Popen("notepad.exe")
    time.sleep(2)
    pyautogui.typewrite(str(text), interval=0.05)
    return f"Notepad opened and the text '{text}' was written."


# ---------- Tool 4: File Search ----------
def search_files(directory, query):
    if not os.path.isdir(directory):
        return f"The folder {directory} does not exist."
    q = str(query).lower().lstrip("*.")
    matches = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.lower().endswith("." + q) or q in f.lower():
                matches.append(os.path.join(root, f))
                if len(matches) >= 20:
                    break
        if len(matches) >= 20:
            break
    if not matches:
        return f"No files matching '{query}' found in {directory}."
    return f"Found {len(matches)} file(s):\n" + "\n".join(matches)


# ---------- Tool 5: File Creation ----------
def create_file(directory, filename, content):
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(str(content))
    return f"File created: {path}"


# ---------- Tool 6: System Information ----------
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def get_system_info():
    stat = MEMORYSTATUSEX()
    stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
    ram_gb = stat.ullTotalPhys / (1024 ** 3)
    return (
        f"Operating system: {platform.system()} {platform.release()} ({platform.version()})\n"
        f"Processor: {platform.processor()}\n"
        f"Total memory (RAM): {ram_gb:.1f} GB"
    )


# ---------- Register all tools with the LLM ----------
def make_tool(name, description, properties, required):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": properties, "required": required},
        },
    }


tools = [
    make_tool("open_calculator",
              "Open Windows Calculator and calculate a math expression such as 25*4.",
              {"expression": {"type": "string", "description": "Math expression, for example 25*4"}},
              ["expression"]),
    make_tool("get_date_time",
              "Get the current date and time.",
              {}, []),
    make_tool("open_notepad",
              "Open Windows Notepad and write the given text in it.",
              {"text": {"type": "string", "description": "The text to write in Notepad"}},
              ["text"]),
    make_tool("search_files",
              "Search for files by name or extension (for example pdf) inside a folder.",
              {"directory": {"type": "string", "description": "Folder path, for example C:\\Users"},
               "query": {"type": "string", "description": "File name part or extension, for example pdf"}},
              ["directory", "query"]),
    make_tool("create_file",
              "Create a text file with the given content.",
              {"directory": {"type": "string", "description": "Folder path where the file is created"},
               "filename": {"type": "string", "description": "File name, for example test.txt"},
               "content": {"type": "string", "description": "Text to put inside the file"}},
              ["directory", "filename", "content"]),
    make_tool("get_system_info",
              "Get the operating system, processor and memory information of this computer.",
              {}, []),
]

available_functions = {
    "open_calculator": open_calculator,
    "get_date_time": get_date_time,
    "open_notepad": open_notepad,
    "search_files": search_files,
    "create_file": create_file,
    "get_system_info": get_system_info,
}


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
        "content": "You are a helpful assistant with tools. Always use a tool when the "
                   "user asks to calculate, get the date or time, open Notepad, find "
                   "files, create a file, or show computer specifications. "
                   "Never answer these yourself.",
    }
]

print("Multi-Tool Agent ready. Type 'exit' to stop.")

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
            try:
                result = available_functions[name](**args)
            except Exception as error:
                result = f"Tool error: {error}"
            print("[TOOL RESULT]", result)
            messages.append({"role": "tool", "content": result, "tool_name": name})
        final = chat(messages)
        messages.append(final)
        print("\nAgent:", final["content"])
    else:
        print("\nAgent:", reply["content"])