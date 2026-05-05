import os
import json
import logging
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from agents.orchestrator import create_orchestrator

# Load environment variables from .env
load_dotenv()

logging.basicConfig(level=logging.INFO)

# Initialize the "Brain"
# Currently using your existing LangGraph Orchestrator while we prepare the Hermes Agent.
orchestrator = create_orchestrator()

# --- MOCK TOOLS FOR HERMES AGENT ---

def fetch_fathom_meetings_mock() -> str:
    """
    Fetches the latest meeting transcripts from the Fathom API.
    (Currently mocked using dummy data from meetings.json)
    """
    logging.info("[TOOL] Fetching latest meetings...")
    try:
        with open("data/meetings.json", "r") as f:
            meetings = json.load(f)
            # Just return the first 2 meetings for the mock
            latest = meetings[:2]
            return json.dumps(latest)
    except Exception as e:
        return json.dumps({"error": str(e)})

def summarize_meetings(meeting_json_str: str) -> str:
    """
    Summarizes the provided meeting transcripts, extracting key decisions, 
    blockers, and action items.
    """
    logging.info("[TOOL] Summarizing meetings...")
    # In a real implementation, this tool might call another LLM prompt or simply 
    # rely on the Hermes Agent's internal reasoning if the agent is powerful enough.
    # For now, we mock the result.
    return "Summary: Discussed API integration issues. Action Items: - [ ] Fix PostgreSQL connection."

def create_clickup_task(title: str, description: str) -> str:
    """
    Creates a task in ClickUp.
    """
    logging.info(f"[TOOL] Creating ClickUp task: {title}")
    # Mocking ClickUp API call
    return f"Success! Task '{title}' created in ClickUp with ID #MockID123"

# --- HERMES AGENT INITIALIZATION ---

# Note: The exact syntax will depend on the hermes-agent package API. 
# This represents the intended structure.
"""
tools = [
    Tool(name="fetch_fathom_meetings", func=fetch_fathom_meetings_mock, description="Fetch latest meeting transcripts"),
    Tool(name="summarize_meetings", func=summarize_meetings, description="Summarize meeting text"),
    Tool(name="create_clickup_task", func=create_clickup_task, description="Create a task in ClickUp")
]

agent = AIAgent(
    system_prompt=\"\"\"
    You are an autonomous Meeting Intelligence Assistant. 
    Your objective is to:
    1. Fetch the latest meeting transcripts.
    2. Summarize them and extract Action Items.
    3. Create ClickUp tasks for the Action Items.
    4. Provide a formatted summary of what you did.
    \"\"\",
    tools=tools,
    model="hermes-2-pro" # or whatever model identifier is configured
)
"""

# --- SLACK BOT (THE INTERFACE) ---

# Initialize Slack app with your bot token
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.event("app_mention")
def handle_mention(event, say):
    """
    Handles when a user mentions @MeetingAI in Slack.
    """
    user = event.get('user')
    text = event.get('text', '')
    
    # Clean the bot mention from the text
    clean_text = text.split(">")[-1].strip()
    
    say(f"Hello <@{user}>! I am analyzing your request: '{clean_text}'... 🤖")
    
    # 1. Ask the Brain to think (using your existing LangGraph setup)
    result = orchestrator.invoke({"query": clean_text})
    summary = result.get("summary", "No insights found.")
    
    say(summary)

@app.event("message")
def handle_direct_message(event, say):
    """
    Handles direct messages to the bot.
    """
    # 1. Ignore bot's own messages
    if event.get("bot_id"):
        return
        
    # 2. Only process Direct Messages (channel_type == "im")
    if event.get("channel_type") != "im":
        return
        
    # 3. Prevent duplicate firing if user tagged bot in DM
    text = event.get('text', '')
    if "<@" in text:
        return

    say("I received your message! Let me analyze that for you... 🤖")
    
    # Ask the Brain to think
    result = orchestrator.invoke({"query": text})
    summary = result.get("summary", "No insights found.")
    
    say(summary)

# --- SCHEDULER (AUTOMATED SELF-LEARNING) ---

def scheduled_intelligence_sync():
    """
    Runs autonomously on a schedule to check for new meetings.
    """
    logging.info("--- Starting Scheduled Intelligence Sync ---")
    # Passive Mode: The agent wakes up and decides what to do based on its system prompt.
    # report = agent.run("Check for new meetings. If any, summarize them, create tasks, and return a report.")
    
    # If the report indicates new activity, post it to the main channel
    # app.client.chat_postMessage(
    #     channel="#meeting-summaries",
    #     text=report
    # )
    logging.info("--- Scheduled Sync Complete ---")

if __name__ == "__main__":
    # 1. Start the Background Scheduler
    scheduler = BackgroundScheduler()
    # Schedule to run every 4 hours (adjust as needed)
    scheduler.add_job(scheduled_intelligence_sync, 'interval', hours=4)
    scheduler.start()
    
    print("⚡️ Hermes Meeting Agent & Slack Bot is running!")
    
    # 2. Start the Slack Bot in Socket Mode
    # Requires SLACK_APP_TOKEN environment variable
    try:
        SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
    except Exception as e:
        print("Note: Slack tokens not found. Set SLACK_BOT_TOKEN and SLACK_APP_TOKEN to run the bot.")
