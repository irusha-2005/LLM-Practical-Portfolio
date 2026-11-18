# Lab 6 Complete Summary: Building a Tool-Using AI Agent with Ollama

**Module:** PUSL3205 Large Language Models and Generative AI
**Student:** [Your Name] | **Student ID:** [Your ID]

This document summarises everything in Lab Sheet 6: what the sheet asked for, what I built for each item, how it works, and what happened when I tested it.

## 1. The lab at a glance

| Part | What the lab sheet asked for | What I built | Files |
|---|---|---|---|
| A | Calculator agent with Ollama (8 steps) | An agent that opens Windows Calculator and types the sum | `agent.py` |
| A exercise | Add 5 more tools and test 6 queries | An agent with 6 tools | `agent2.py` |
| B | Give the agent memory using SQLite | An agent with short-term, long-term and working memory | `mem_agent.py` |
| C | RAG powered agent with 3 tools | An agent that searches a PDF knowledge base | `rag_agent.py` |
| D | Google Calendar tools with Google OAuth | An agent that reads and creates calendar events | `calendar_agent.py` |
| E | n8n in Docker, an AI agent with a local LLM | An n8n agent workflow with memory and calendar tools | n8n workflow |
| Final | Build an Intelligent University Assistant (8 requirements) | An n8n agent with RAG, Calendar, Sheets, Docs and Gmail | `n8n_university_assistant.json` |
| Further | Read how to plan 5 project ideas | Planning notes (section 9) | none |

**Core idea:** an LLM cannot press buttons or open files. In an agent, the LLM decides which tool to use and with which arguments, my program runs the tool, and the result goes back to the LLM, which writes the final answer.

## 2. Part A: Calculator agent

The lab sheet gave eight steps. Here is what each one did:

| Step | Lab sheet step | What I did |
|---|---|---|
| 1 | Check that `llama3.2:3b` is available | Ran `ollama list`. Ollama was not installed on my computer, so I installed it and ran `ollama pull llama3.2:3b` (about 2 GB). |
| 2 | Install libraries | Installed `pyautogui` (types and clicks for the computer) and `pygetwindow`. LangChain was blocked on my computer (see section 10). |
| 3 | Import the libraries | Imported `json`, `subprocess`, `urllib`, `time` and `pyautogui`. |
| 4 | Initialise the LLM | The agent calls the Ollama API at `http://localhost:11434/api/chat` with model `llama3.2:3b` and temperature 0, so answers are repeatable. |
| 5 | Create the calculator tool | `open_calculator(expression)` accepts only digits and `+ - * / ( ) .`, opens `calc.exe`, waits 2 seconds, types the expression and presses Enter. |
| 6 | Register the tool with the LLM | The tool is described to the LLM as a JSON schema: its name, a description and a parameter called `expression`. |
| 7 | Implement the agent execution loop | Read the user input, send it to the LLM, run the tool if the LLM asks for one, send the tool result back and print the final answer. |
| 8 | Run and test | `Calculate 7*4` opened Calculator, typed the sum and showed 28. The terminal printed `[TOOL SELECTED]`, `[TOOL ARGUMENTS]` and `[TOOL RESULT]`. |

The system message tells the LLM it must call the calculator tool and never work out the answer itself.

## 3. Part A exercise: multiple tools

`agent2.py` has six tools. Each tool has a name, a description and parameters, and the LLM picks one from the user's sentence.

| Tool | What it does |
|---|---|
| `open_calculator` | Opens Calculator and types a calculation |
| `get_date_time` | Returns the current date and time |
| `open_notepad` | Opens Notepad and types the given text |
| `search_files` | Searches a folder for files by name or extension |
| `create_file` | Creates a text file with the given content |
| `get_system_info` | Returns the operating system, processor and total memory |

Test table from the lab sheet:

| No. | User query | Tool the agent used | Result |
|---|---|---|---|
| 1 | Calculate 25 x 4 | `open_calculator` | Calculator opened and showed 100 |
| 2 | What is the date today? | `get_date_time` | Gave today's date |
| 3 | Open Notepad and write Hello Students | `open_notepad` | Notepad opened and typed the text |
| 4 | Find all PDF files in a folder | `search_files` | Listed the PDFs found |
| 5 | Create a file called test.txt with Hello World | `create_file` | Created `test.txt` |
| 6 | Show my computer specifications | `get_system_info` | Showed OS, processor and memory |

For tests 4 and 5 I used folders inside my Documents folder instead of `D:\MSC AI`, because I do not have that folder.

## 4. Part B: Agent with memory

**The problem:** without memory, the agent forgets everything between messages ("What is my name?" gets "I don't know your name"). With memory it answers "Your name is Alex".

`mem_agent.py` uses SQLite, which is built into Python. It has three kinds of memory:

| Memory type | How it works |
|---|---|
| Short-term | The current conversation is kept in a list. Only the last 20 messages are kept so the prompt stays small. |
| Long-term | Facts about the user are saved in the SQLite table `memories` (columns `id`, `fact`, `created`). After every message the LLM extracts new personal facts, for example "The user's name is Alex", and they are saved. Duplicates are ignored. |
| Working memory | A small record of the last tool used and its result. |

The agent has the two tools the lab sheet asked for:

- `calculator`: performs mathematical calculations.
- `search_student_memory`: finds stored facts by keyword.

**Test:** I said "My name is Alex", then closed the program, started it again and asked "What is my name?". The agent answered "Your name is Alex", which shows the memory lasts after a restart because it is stored in the database file.

## 5. Part C: RAG powered agent

RAG (Retrieval-Augmented Generation) lets the agent answer from a document instead of guessing. `rag_agent.py` has three tools: the calculator, the memory search, and `search_university_knowledge`.

How the RAG tool works:

1. **Load:** `pypdf` reads the PDF in the `data` folder.
2. **Split:** the text is cut into chunks of 800 characters with 100 characters of overlap.
3. **Embed:** each chunk is turned into a vector by `qwen3-embedding:0.6b` through Ollama.
4. **Cache:** the vectors are saved in `kb_cache.json`, so the PDF is processed only once.
5. **Retrieve:** the question is embedded and the 3 chunks with the highest cosine similarity are found.
6. **Answer:** the chunks, with their source and page number, are given to the LLM.

**Test:** the agent answered "What is LangChain?" from the PDF and showed the source. In the same chat it used the memory tool to recall my name.

## 6. Part D: Google Calendar

**Google setup (done once):**

1. Created a Google Cloud project called "University AI assistant".
2. Enabled the Google Calendar API.
3. Set up the OAuth consent screen (type External) and added my own account as a test user.
4. Created an OAuth client of type Desktop app and downloaded it as `credentials.json`.

**How sign-in works:** the first time the program runs, a browser window opens and I sign in to Google. Google warns that the app is not verified, which is normal for my own test app. After I allow access, the program saves a login token in `token.json` and does not ask again. The program only asks for permission to manage calendar events.

**Tools in `calendar_agent.py`:**

| Tool | What it does |
|---|---|
| `get_todays_schedule` | Reads the events of a day (today by default) and lists them with their times |
| `create_calendar_event` | Creates an event from a title, a date, a start time and an end time. The timezone is Asia/Colombo. It checks that the date and times are valid first. |

The system message tells the LLM today's date and that events are one hour long when no end time is given. I tested checking my schedule and creating a "Study Group" event, and the event appeared in Google Calendar.

## 7. Part E: n8n

n8n is a visual workflow tool. I ran it locally in Docker:

```
docker volume create n8n_data
docker run -d --name n8n --restart unless-stopped -p 5678:5678 -e GENERIC_TIMEZONE=Asia/Colombo -e TZ=Asia/Colombo -e N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
```

Then I opened `http://localhost:5678`, created the owner account, and built two workflows.

**1. Simple workflow:** a manual trigger and an Edit Fields node, to check that n8n works. Both nodes showed a green tick.

**2. AI agent workflow:**

| Node | Settings |
|---|---|
| When chat message received | Chat trigger |
| AI Agent | System message with today's date and rules for the tools |
| Ollama Chat Model | Base URL `http://host.docker.internal:11434` (so the Docker container can reach Ollama on my computer), model `llama3.2:3b` |
| Simple Memory | Keeps the conversation |
| Google Calendar tool: get many events | Resource Event, operation Get Many, limit 50, events from now to one week ahead |
| Google Calendar tool: create event | Resource Event, operation Create. Start, End and Summary are "Defined by agent", so the LLM fills them in. |

n8n needs its own Google key. I created an OAuth client of type Web application with the redirect address `http://localhost:5678/rest/oauth2-credential/callback`. In n8n, I pasted its client ID and secret, then signed in with Google.

**Test:** I asked the agent in the n8n chat to create an event, and it created "Study Group" in my Google Calendar.

## 8. Final exercise: Intelligent University Assistant

**Problem:** university staff and students spend time on repetitive administrative tasks. I extended the n8n agent with more tools so that one chat can handle all eight requirements.

| No. | Requirement | How it is done |
|---|---|---|
| 1 | Receive requests through a chat interface | n8n chat trigger |
| 2 | Understand the request using an AI agent | AI Agent node with Ollama `llama3.2:3b` and Simple Memory |
| 3 | Retrieve university information using RAG | A second workflow, "Load University Knowledge", saves sample university text into a Simple Vector Store using `qwen3-embedding:0.6b` embeddings and a Default Data Loader. The agent has a retrieve tool, `search_university_knowledge`, that searches it and returns the 3 best matches. |
| 4 | Check Google Calendar for available times | Google Calendar get events tool |
| 5 | Create calendar events after approval | Google Calendar create event tool. The system message tells the agent to state the title, date and time and ask "Shall I create it?", and to create the event only after the user says yes. |
| 6 | Read and update student records in Google Sheets | A sheet called "Student Records" (columns StudentID, Name, Degree, Year, Email). Tool 1 reads rows. Tool 2 updates a row, matching on StudentID, and only changes Degree, Year and Email. |
| 7 | Generate documents using Google Docs | Tool 1 creates a document with a title. Tool 2 writes text into it, using the document ID. |
| 8 | Send notifications through Gmail | Gmail send tool, with To, Subject and Message filled in by the agent |

**Setup needed for this part:**

- I enabled five Google APIs: Calendar, Gmail, Sheets, Docs and Drive. The Drive API is needed so that n8n can list my spreadsheets.
- Each Google tool in n8n uses the same OAuth client and my Google sign-in.
- The university knowledge text is made-up sample text (library hours, student services, modules, late submission rules), not real university data.

**Tests I ran through the n8n chat:** a student record question and update, creating a Welcome Letter document, sending a test email, library hours and late submission questions answered from the knowledge base, and the approval flow for a Project Meeting.

## 9. Further reading: how to plan

The lab sheet ends with five project ideas to read about. I did not build them. This is how each could be planned with the same pieces:

| Idea | Possible plan |
|---|---|
| Weather Notification System | A schedule trigger runs each morning, an HTTP request gets the forecast, the agent writes a short message and Gmail sends it. |
| GitHub Activity Monitor | A trigger checks a repository through the GitHub API, the agent summarises new commits and issues, and a message is sent. |
| Currency Rate Monitoring | A schedule trigger gets exchange rates, a condition checks a threshold and an alert is sent when it is crossed. |
| Multi-agent university assistant | One main agent sends each request to a specialist agent (calendar, records, documents or knowledge) and combines the answers. |
| Automated Research monitoring | A schedule trigger searches for new papers on a topic, the agent summarises them, and the results are saved in a Google Doc or Sheet. |

## 10. Problems and how I solved them

| Problem | Solution |
|---|---|
| Ollama was not installed (`ollama` was not recognised) | Installed Ollama and pulled the models. |
| A Windows Application Control policy blocked LangChain | Rebuilt the agents to call the Ollama REST API directly. The behaviour is the same: the LLM still chooses the tool and its arguments. |
| n8n could not list my Google Sheets (403 error) | Enabled the Google Drive API in Google Cloud. |
| The 3B model sometimes picks the wrong tool or a wrong date | Wrote clear tool descriptions and a detailed system message that includes today's date. |
| The agent could create events by mistake | Added the approval step in the system message. |
| The n8n vector store is kept in memory and is lost on restart | Run the "Load University Knowledge" workflow again after n8n restarts. |

## 11. Differences from the lab sheet

- LangChain was not used (see section 10).
- Part C searched a small PDF (the Lab Sheet 5 notes) instead of the university handbook. It used its own cosine similarity search with a JSON cache instead of ChromaDB.
- In the exercise, the file tests used folders in my Documents folder instead of `D:\MSC AI`.

## 12. What I learned

- An agent is an LLM, plus tools, plus a loop. Clear tool descriptions matter as much as the model.
- Memory turns a chatbot into an assistant that keeps context, and SQLite makes that memory last after a restart.
- RAG makes answers depend on real documents. The answer is only as good as the text that was retrieved.
- Small local models are free and private, but they make mistakes, so important actions need an approval step.
- OAuth lets a program use my Google account without my password, and the key files must never be uploaded to GitHub.
- Workflow tools such as n8n make it quick to connect an LLM to many services.

## 13. Files in this repository

| File | Description |
|---|---|
| `README.md` | Full report of the lab, with screenshots |
| `SUMMARY.md` | This summary |
| `agent.py`, `agent2.py`, `mem_agent.py`, `rag_agent.py`, `calendar_agent.py` | Code for Parts A to D |
| `n8n_university_assistant.json` | Exported n8n workflow of the final exercise (it contains no passwords or keys) |
| `test.txt` | File created by the file creation tool during testing |
| `*.png` | Screenshots of each part working |

Private files (`credentials.json`, `token.json`, the n8n OAuth client file) and temporary files (`student_memory.db`, `kb_cache.json`, the `data` folder) are not included.
