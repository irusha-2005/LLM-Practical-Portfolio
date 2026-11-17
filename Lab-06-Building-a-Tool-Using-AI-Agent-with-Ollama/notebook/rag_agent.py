import os
import re
import json
import math
import sqlite3
import urllib.request
from pypdf import PdfReader

OLLAMA_URL = "http://localhost:11434/api/chat"
EMBED_URL = "http://localhost:11434/api/embed"
MODEL = "llama3.2:3b"
EMBED_MODEL = "qwen3-embedding:0.6b"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CACHE_PATH = os.path.join(BASE_DIR, "kb_cache.json")
DB_PATH = os.path.join(BASE_DIR, "student_memory.db")


def post_json(url, payload):
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())


# ---------- Long-term memory (SQLite) ----------
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


# ---------- Knowledge base (RAG) ----------
def embed(texts):
    return post_json(EMBED_URL, {"model": EMBED_MODEL, "input": texts})["embeddings"]


def split_text(text, size=800, overlap=100):
    text = " ".join(text.split())
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks


def load_knowledge_base():
    pdfs = []
    if os.path.isdir(DATA_DIR):
        pdfs = sorted(f for f in os.listdir(DATA_DIR) if f.lower().endswith(".pdf"))
    signature = [[f, os.path.getsize(os.path.join(DATA_DIR, f))] for f in pdfs]

    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            cache = json.load(f)
        if cache.get("signature") == signature:
            return cache["chunks"]

    chunks = []
    for name in pdfs:
        reader = PdfReader(os.path.join(DATA_DIR, name))
        for page_no, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            for piece in split_text(text):
                if len(piece.strip()) > 30:
                    chunks.append({"source": f"data\\{name}", "page": page_no, "text": piece})

    for i in range(0, len(chunks), 16):
        batch = chunks[i:i + 16]
        vectors = embed([c["text"] for c in batch])
        for c, v in zip(batch, vectors):
            c["embedding"] = v
        print(f"  embedded {min(i + 16, len(chunks))} of {len(chunks)} chunks")

    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump({"signature": signature, "chunks": chunks}, f)
    return chunks


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


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


# ---------- Tool 3: RAG Search ----------
def search_university_knowledge(query):
    print(f"[EXECUTING] Searching university knowledge for: '{query}'...")
    if not knowledge_base:
        return "The knowledge base is empty. Put a PDF in the data folder."
    query_vector = embed([str(query)])[0]
    scored = sorted(
        knowledge_base, key=lambda c: cosine(query_vector, c["embedding"]), reverse=True
    )[:3]
    parts = []
    for c in scored:
        parts.append(f"Source: {c['source']}, Page: {c['page']}\n{c['text'][:600]}")
    return "\n\n".join(parts)


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
            "description": "Search previously stored information about the user, such as their name, degree, interests or goals.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "What to look for, for example 'name'"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_university_knowledge",
            "description": "Search the university knowledge base (handbook PDF) for information about degree programs, subjects, modules, rules and policies.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "The question to search for"}},
                "required": ["query"],
            },
        },
    },
]

available_functions = {
    "calculator": calculator,
    "search_student_memory": search_student_memory,
    "search_university_knowledge": search_university_knowledge,
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
    return post_json(OLLAMA_URL, payload)["message"]


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
print(" RAG POWERED STUDENT AI AGENT")
print(" SHORT-TERM MEMORY")
print(" LONG-TERM SQLITE MEMORY")
print(" RAG KNOWLEDGE BASE")
print("=" * 40)
print("Building the knowledge base (the first time can take a few minutes)...")
knowledge_base = load_knowledge_base()
print(f"Knowledge base ready: {len(knowledge_base)} chunks.")
print("Type 'exit' to stop.")

messages = [
    {
        "role": "system",
        "content": "You are a friendly university student assistant. "
                   "For questions about degree programs, subjects, modules, rules or "
                   "university information, use the search_university_knowledge tool and "
                   "answer only from its result. "
                   "If the user asks about themselves or something they told you before, "
                   "use the search_student_memory tool. "
                   "For maths, use the calculator tool. Otherwise answer directly and briefly.",
    }
]

while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ["exit", "quit"]:
        break

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
            messages.append({"role": "tool", "content": result, "tool_name": name})
        reply = chat(messages)
        messages.append(reply)

    if len(messages) > 21:
        messages = [messages[0]] + messages[-20:]
    print("\n[SHORT-TERM MEMORY] Conversation updated.")
    print("\nAgent:", reply["content"])