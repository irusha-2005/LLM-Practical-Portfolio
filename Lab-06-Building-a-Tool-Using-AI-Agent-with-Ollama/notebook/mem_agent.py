import os
import re
import json
import sqlite3
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"

# ---------- Long-term memory (SQLite) ----------
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "student_memory.db")
conn = sqlite3.connect(DB_PATH)
conn.execute(
    "CREATE TABLE IF NOT EXISTS memories "
    "(id INTEGER PRIMARY KEY AUTOINCREMENT, fact TEXT UNIQUE, created TEXT DEFAULT CURRENT_TIMESTAMP)"
)
conn.commit()

STOP_WORDS = {
    "what", "the", "and", "you", "your", "are", "who", "was", "did", "how", "can",
    "for", "with", "about", "tell", "know", "remember", "have", "has", "does",
    "from", "this", "that", "mine", "which", "where", "when", "please",
}


def save_memory(fact):
    cur = conn.execute("INSERT OR IGNORE INTO memories (fact) VALUES (?)", (fact,))
    conn.commit()
    return cur.rowcount > 0


# ---------- Tool 1: Calculator ----------
def calculator(expression):
    expression = str(expression).replace("x", "*").replace("×", "*").replace(" ", "")
    allowed = "0123456789+-*/()."
    if not expression or any(ch not in allowed for ch in expression):
        return "Invalid expression."
    try:
        return f"{expression} = {eval(expression)}"
    except Exception as error:
        return f"Calculation error: {error}"


# ---------- Tool 2: Memory Search ----------
def search_student_memory(query):
    words = re.findall(r"[a-z0-9']+", str(query).lower())
    words = [w for w in words if len(w) > 2 and w not in STOP_WORDS]
    facts = [row[0] for row in conn.execute("SELECT fact FROM memories")]
    matches = [f for f in facts if any(w in f.lower() for w in words)]
    if not matches:
        return "No matching memories found."
    return "Stored memories:\n- " + "\n- ".join(matches)


# ---------- Register tools ----------
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Perform a math calculation such as 25*4.",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string", "description": "Math expression, for example 25*4"}},
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_student_memory",
            "description": "Search previously stored information about the user, such as their name, degree, interests or goals. Use it when the user asks about themselves or something they told you before.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "What to look for, for example 'name'"}},
                "required": ["query"],
            },
        },
    },
]

available_functions = {
    "calculator": calculator,
    "search_student_memory": search_student_memory,
}


# ---------- Talk to the LLM ----------
def chat(messages, use_tools=True):
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0},
    }
    if use_tools:
        payload["tools"] = tools
    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())["message"]


def extract_new_facts(user_input):
    prompt = [
        {
            "role": "system",
            "content": "Extract personal facts the user states about themselves "
                       "(name, degree, university, interests, preferences, goals). "
                       "Write each fact as one short sentence in third person, for example "
                       "'The user's name is Alex.' One fact per line. "
                       "If the message has no personal fact, reply exactly: NONE",
        },
        {"role": "user", "content": user_input},
    ]
    reply = chat(prompt, use_tools=False)["content"]
    facts = []
    for line in reply.splitlines():
        line = line.strip("-• ").strip()
        if line and not line.upper().startswith("NONE"):
            facts.append(line)
    return facts[:3]


# ---------- Agent ----------
print("=" * 40)
print(" INTELLIGENT STUDENT AI AGENT")
print(" SHORT-TERM MEMORY")
print(" LONG-TERM SQLITE MEMORY")
print(" WORKING MEMORY")
print("=" * 40)
print("Type 'exit' to stop.")

# Short-term memory = the current conversation
messages = [
    {
        "role": "system",
        "content": "You are a friendly university student assistant. "
                   "If the user asks about themselves or something they told you before, "
                   "use the search_student_memory tool. "
                   "For maths, use the calculator tool. Otherwise answer directly and briefly.",
    }
]

# Working memory = what the agent is doing right now
working_memory = {"last_tool": None, "last_result": None}

while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ["exit", "quit"]:
        break

    # Save new information to long-term memory
    new_facts = [] if user_input.strip().endswith("?") else extract_new_facts(user_input)
    if new_facts:
        print("\n[NEW MEMORIES DETECTED]")
        for fact in new_facts:
            if save_memory(fact):
                print("[SAVED]", fact)
    else:
        print("\n[MEMORY] No new information to save.")

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
            working_memory = {"last_tool": name, "last_result": result}
            messages.append({"role": "tool", "content": result, "tool_name": name})
        reply = chat(messages)
        messages.append(reply)

    # Keep the short-term memory small
    if len(messages) > 21:
        messages = [messages[0]] + messages[-20:]
    print("\n[SHORT-TERM MEMORY] Conversation updated.")
    print("\nAgent:", reply["content"])