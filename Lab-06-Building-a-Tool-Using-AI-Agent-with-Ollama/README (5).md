# Lab 6: Building a Tool-Using AI Agent with Ollama

**Module:** PUSL3205 Large Language Models and Generative AI


## 1. Overview

This lab builds AI agents that can use tools. An agent is an LLM that can decide to call a function (a tool), such as a calculator, a database search or a calendar, and then use the result in its answer. The agents run on a local LLM (`llama3.2:3b`) through Ollama, so no paid API key is needed. The lab starts with a simple calculator agent and ends with an Intelligent University Assistant built in n8n.

| Part | What was built | Main files |
|---|---|---|
| A | Calculator agent and a multi-tool agent | `agent.py`, `agent2.py` |
| B | Agent with memory (SQLite) | `mem_agent.py` |
| C | RAG powered agent | `rag_agent.py` |
| D | Google Calendar tools | `calendar_agent.py` |
| E | n8n workflow in Docker | screenshots |
| Final | Intelligent University Assistant | `n8n_university_assistant.json`, screenshots |

**Technologies:** Python, Ollama (`llama3.2:3b`, `qwen3-embedding:0.6b`), SQLite, Google Calendar API, Docker, n8n, Google Sheets, Google Docs, Gmail.

## 2. Folder structure

```
Lab-06-Tool-Using-AI-Agent/
├── README.md
├── notebooks/
│   ├── agent.py
│   ├── agent2.py
│   ├── mem_agent.py
│   ├── rag_agent.py
│   ├── calendar_agent.py
│   ├── test.txt
│   └── n8n_university_assistant.json
└── screenshots/
```

| File | Description |
|---|---|
| `agent.py` | Part A: calculator agent |
| `agent2.py` | Part A exercise: agent with 6 tools |
| `mem_agent.py` | Part B: agent with short-term, long-term and working memory |
| `rag_agent.py` | Part C: agent with calculator, memory search and RAG search tools |
| `calendar_agent.py` | Part D: agent with Google Calendar tools |
| `test.txt` | File created by the file creation tool during testing |
| `n8n_university_assistant.json` | Exported n8n workflow of the final exercise (no passwords or keys inside) |

Private files (Google `credentials.json`, `token.json`, the n8n OAuth client file) and temporary files (`student_memory.db`, `kb_cache.json`, the `data` folder) are not included in this repository.

## 3. How an agent works

Every agent in this lab follows the same loop:

1. The user types a request.
2. The request and a list of the available tools are sent to the LLM.
3. The LLM decides whether to answer directly or to call a tool, and it chooses the tool arguments.
4. The program runs the chosen tool and sends the result back to the LLM.
5. The LLM writes the final answer.

The Python agents call the Ollama REST API directly (`http://localhost:11434/api/chat`) and use the tool calling feature of `llama3.2:3b`.

## 4. Part A: Calculator agent

`agent.py` has one tool, `open_calculator`. When the user asks for a calculation, the LLM calls the tool. The tool opens Windows Calculator and types the expression automatically using `pyautogui`.

![Part A calculator agent](screenshots/partA_calculator.png)
![Part A calculator agent](screenshots/partA_calculator1.png)

### Exercise: multiple tools

`agent2.py` adds five more tools: date and time, Notepad, file search, file creation and system information.

| No. | User query | Tool used |
|---|---|---|
| 1 | Calculate 25 x 4 | `open_calculator` |
| 2 | What is the date today? | `get_date_time` |
| 3 | Open Notepad and write Hello Students | `open_notepad` |
| 4 | Find all PDF files in a folder | `search_files` |
| 5 | Create a file called test.txt with Hello World | `create_file` |
| 6 | Show my computer specifications | `get_system_info` |

![Multi-tool agent](screenshots/exercise_multitool_1.png)
![Multi-tool agent](screenshots/exercise_multitool_1.1.png)
![Multi-tool agent](screenshots/exercise_multitool2.png)
![Multi-tool agent](screenshots/exercise_multitool_3.png)
![Multi-tool agent](screenshots/exercise_multitool_3.1.png)
![Multi-tool agent](screenshots/exercise_multitool_4.png)
![Multi-tool agent](screenshots/exercise_multitool_4.1.png)
![Multi-tool agent](screenshots/exercise_multitool_5.png)
![Multi-tool agent](screenshots/exercise_multitool_6.png)

## 5. Part B: Agent with memory

`mem_agent.py` gives the agent three kinds of memory:

- **Short-term memory:** the current conversation, kept in a list (only the last 20 messages are kept).
- **Long-term memory:** facts about the user, stored in a SQLite database. After each message, the LLM extracts new personal facts and they are saved.
- **Working memory:** the last tool used and its result.

The agent has two tools: `calculator` and `search_student_memory`. In the test, I told the agent my name, closed the program, started it again, and the agent still answered correctly. This shows that the SQLite memory survives a restart.

![Memory](screenshots/partB_memory.png)
![Memory](screenshots/partB_memory_1.png)
![Memory](screenshots/partB_memory_1.1.png)
![Memory](screenshots/partB_memory_2.png)
![Memory](screenshots/partB_memory_2.1.png)

## 6. Part C: RAG powered agent

`rag_agent.py` adds a third tool, `search_university_knowledge`, which searches a PDF knowledge base:

1. The PDF in the `data` folder is read with `pypdf` and split into chunks of 800 characters (100 characters of overlap).
2. Each chunk is converted into a vector by `qwen3-embedding:0.6b` through Ollama.
3. The question is embedded the same way, and the 3 most similar chunks are found with cosine similarity.
4. The chunks are given to the LLM, which writes the answer from them.

The vectors are cached in `kb_cache.json`, so the PDF is only processed once.

In my test the knowledge base was a small PDF (RAG architecture notes), and the agent answered "What is LangChain?" from it. In the same chat the agent also used the memory tool to remember my name.

![RAG agent](screenshots/partC_rag.png)
![RAG agent](screenshots/partC_rag_1.png)

## 7. Part D: Google Calendar

`calendar_agent.py` connects the agent to Google Calendar through the Google Calendar API with OAuth sign-in. It has two tools:

- `get_todays_schedule`: reads the events of a day.
- `create_calendar_event`: creates an event with a title, a date, a start time and an end time (timezone Asia/Colombo).

Setup: a Google Cloud project, the Calendar API enabled, an OAuth consent screen with my account as a test user, and a Desktop app OAuth client.

![Calendar agent in the terminal](screenshots/partD_terminal.png)
![Event in Google Calendar](screenshots/partD_calendar.png)

## 8. Part E: n8n

n8n runs locally in Docker:

```
docker volume create n8n_data
docker run -d --name n8n --restart unless-stopped -p 5678:5678 -e GENERIC_TIMEZONE=Asia/Colombo -e TZ=Asia/Colombo -e N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
```

n8n reaches the Ollama model on my computer through `http://host.docker.internal:11434`.

First, a simple workflow with a manual trigger and an Edit Fields node, to check that n8n works:

![Simple workflow](screenshots/partE_simple_workflow.png)

Then, an AI Agent workflow with a chat trigger, the Ollama Chat Model, Simple Memory and two Google Calendar tools (get events and create event):

![AI agent workflow](screenshots/partE_agent_workflow.png)

## 9. Final exercise: Intelligent University Assistant

One n8n AI Agent handles all the requirements of the exercise. The exported workflow is in `notebooks/university assistant.json`.

| No. | Requirement | How it is done |
|---|---|---|
| 1 | Receive requests through a chat interface | n8n chat trigger |
| 2 | Understand the request using an AI agent | AI Agent node with Ollama `llama3.2:3b` and Simple Memory |
| 3 | Retrieve university information using RAG | Simple Vector Store with `qwen3-embedding:0.6b` embeddings, loaded by a second workflow ("Load University Knowledge") |
| 4 | Check Google Calendar for available times | Google Calendar get events tool |
| 5 | Create calendar events after approval | Google Calendar create event tool. The system message makes the agent ask "Shall I create it?" first |
| 6 | Read and update student records | Google Sheets get rows and update row tools |
| 7 | Generate documents | Google Docs create and update tools |
| 8 | Send notifications | Gmail send tool |

The agent's system message lists every tool and says when to use it. It also tells the agent not to invent information.
### Reading events (Google Calaeder)

![Google Calender](screenshots/google_calender.png)

### Reading student records (Google Sheets)

![Google Sheets](screenshots/google_sheets.png)

### Document generation and email notification

![Docs and Gmail chat](screenshots/final_docs_gmail_chat.png)
![Docs and Gmail chat](screenshots/final_docs_gmail_chat_1.png)
![Generated Google Doc](screenshots/final_google_doc.png)
![Notification email](screenshots/final_gmail.png)

### RAG search of the university knowledge base

![RAG search](screenshots/final_rag_search.png)
![RAG search](screenshots/final_rag_search_1.png)

### Calendar check and event creation after approval

![Approval flow](screenshots/final_approval_flow.png)
![Approval flow](screenshots/final_approval_flow_1.png)

## 10. Problems and what I learned

- **A Windows security policy blocked LangChain.** An Application Control policy on my computer blocked one of the LangChain files, so I rebuilt the agents to call the Ollama API directly. The behaviour is the same: the LLM still chooses the tool and its arguments.
- **Google Drive API needed.** The Google Sheets node in n8n could not list my spreadsheets until the Google Drive API was also enabled.
- **A small model makes mistakes.** `llama3.2:3b` sometimes picks the wrong tool or gets a date wrong. Clear tool descriptions and a detailed system message made it much more reliable.
- **Approval step.** Asking for approval in the system message stops the agent from creating calendar events by mistake.
- **The n8n vector store is temporary.** It is kept in memory, so the knowledge workflow must be run again after n8n restarts.
- **Memory makes agents more useful.** With memory, the agent keeps context and remembers information between sessions.

## 11. Differences from the lab sheet

- LangChain was not used (see above).
- Part C searches a small PDF (the Lab Sheet 5 notes) instead of the university handbook, and it uses its own cosine similarity search with a JSON cache instead of ChromaDB.
- In the exercise, the file tests used folders in my Documents folder instead of `D:\MSC AI`.

## 12. How to run

1. Install Ollama, then run:

```
ollama pull llama3.2:3b
ollama pull qwen3-embedding:0.6b
```

2. Install the Python libraries:

```
python -m pip install pyautogui pypdf google-api-python-client google-auth-oauthlib google-auth-httplib2
```

3. Run a part, for example:

```
python notebooks\agent.py
```

**Notes**
- Part C needs a PDF named `handbook.pdf` in a folder called `data` next to `rag_agent.py`.
- Part D needs a Google `credentials.json` file next to `calendar_agent.py`. It is not included in this repository because it is private.
- The n8n workflow needs Docker Desktop and my own Google credentials, so it cannot be run directly from this repository. Import `university_assistant.json` in n8n and connect your own credentials to use it. The screenshots show it working.
