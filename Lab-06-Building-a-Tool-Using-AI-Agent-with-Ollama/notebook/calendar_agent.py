import os
import json
import urllib.request
from datetime import datetime, timedelta, timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")
TOKEN_PATH = os.path.join(BASE_DIR, "token.json")
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

TZ_NAME = "Asia/Colombo"
TZ = timezone(timedelta(hours=5, minutes=30))


# ---------- Google sign-in (OAuth) ----------
def get_calendar_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)


# ---------- Tool 1: Check schedule ----------
def get_todays_schedule(date=""):
    print("[EXECUTING] Reading Google Calendar...")
    try:
        if date:
            day = datetime.strptime(str(date), "%Y-%m-%d")
        else:
            day = datetime.now(TZ).replace(tzinfo=None)
    except ValueError:
        return "Invalid date. Use the format YYYY-MM-DD."
    start = datetime.combine(day.date(), datetime.min.time(), tzinfo=TZ)
    end = start + timedelta(days=1)
    events = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start.isoformat(),
            timeMax=end.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
        .get("items", [])
    )
    if not events:
        return f"No events on {start.strftime('%Y-%m-%d')}."
    lines = []
    for e in events:
        s = e["start"].get("dateTime", e["start"].get("date"))
        when = datetime.fromisoformat(s).strftime("%I:%M %p") if "T" in s else "All day"
        lines.append(f"{when} - {e.get('summary', '(no title)')}")
    return f"Events on {start.strftime('%Y-%m-%d')}:\n" + "\n".join(lines)


# ---------- Tool 2: Create event ----------
def create_calendar_event(summary, date, start_time, end_time):
    print("[EXECUTING] Creating Google Calendar event...")
    try:
        datetime.strptime(str(date), "%Y-%m-%d")
        datetime.strptime(str(start_time), "%H:%M")
        datetime.strptime(str(end_time), "%H:%M")
    except ValueError:
        return "Invalid date or time. Use YYYY-MM-DD for the date and 24-hour HH:MM for times."
    body = {
        "summary": summary,
        "start": {"dateTime": f"{date}T{start_time}:00", "timeZone": TZ_NAME},
        "end": {"dateTime": f"{date}T{end_time}:00", "timeZone": TZ_NAME},
    }
    event = service.events().insert(calendarId="primary", body=body).execute()
    return f"Event created: '{summary}' on {date} from {start_time} to {end_time}. Link: {event.get('htmlLink')}"


# ---------- Register tools ----------
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_todays_schedule",
            "description": "Check the user's Google Calendar schedule for a day. Use it when the user asks about their schedule, events or what is on today.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date as YYYY-MM-DD. Leave empty for today."}
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_calendar_event",
            "description": "Create a new event in the user's Google Calendar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Event title"},
                    "date": {"type": "string", "description": "Date as YYYY-MM-DD"},
                    "start_time": {"type": "string", "description": "Start time in 24-hour HH:MM, for example 14:00"},
                    "end_time": {"type": "string", "description": "End time in 24-hour HH:MM, for example 15:00"},
                },
                "required": ["summary", "date", "start_time", "end_time"],
            },
        },
    },
]

available_functions = {
    "get_todays_schedule": get_todays_schedule,
    "create_calendar_event": create_calendar_event,
}


# ---------- Talk to the LLM ----------
def chat(messages):
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": tools,
        "stream": False,
        "options": {"temperature": 0},
    }
    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())["message"]


# ---------- Start ----------
print("Signing in to Google Calendar (a browser window may open the first time)...")
service = get_calendar_service()
print("Google Calendar connected.")

now = datetime.now(TZ)
messages = [
    {
        "role": "system",
        "content": f"You are a university assistant. Today is {now.strftime('%A %Y-%m-%d')} and the "
                   f"time is {now.strftime('%H:%M')} (timezone {TZ_NAME}). "
                   "When the user asks about their schedule, call get_todays_schedule. "
                   "When the user asks to create, add or schedule an event, call create_calendar_event "
                   "with the date as YYYY-MM-DD and times in 24-hour HH:MM. "
                   "If no end time is given, make the event one hour long. "
                   "Never invent calendar information.",
    }
]

print("Calendar Agent ready. Type 'exit' to stop.")

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
        reply = chat(messages)
        messages.append(reply)

    print("\nAgent:", reply["content"])