import chainlit as cl
import os
import json
from agents.orchestrator import create_orchestrator
from server import _ensure_data

# Initialize the orchestrator
app = create_orchestrator()

@cl.on_chat_start
async def start():
    # 1. Ensure proactive intelligence is synced on startup
    cl.user_session.set("orchestrator", app)
    
    msg = cl.Message(content="🔄 Synchronizing Meeting Intelligence...")
    await msg.send()
    
    # Run the ingestion/sync logic
    _ensure_data()
    
    msg.content = "✅ Meeting Intelligence Synced. How can I help you today?"
    await msg.update()

@cl.on_message
async def main(message: cl.Message):
    orchestrator = cl.user_session.get("orchestrator")
    
    # Show a loader/step for the thinking process
    async with cl.Step(name="Analyzing Meetings") as step:
        inputs = {"query": message.content}
        # Run the LangGraph app
        # Since cl.on_message is async, and orchestrator.invoke is sync (usually), 
        # we wrap it in a thread or just call it if it's fast.
        result = await cl.make_async(orchestrator.invoke)(inputs)
        
        step.output = "Analysis Complete."

    final_report = result.get("summary", "No summary generated.")
    
    # Check for Action Items in the report to highlight them
    # We can detect "- [ ]" and create a separate view for them
    lines = final_report.split("\n")
    action_items = [line for line in lines if "- [ ]" in line or "- [x]" in line]
    
    # Prepare the main message
    await cl.Message(
        content=final_report,
        author="Meeting AI"
    ).send()
    
    # If there are action items, show them as a separate "Task List" element
    if action_items:
        actions_text = "\n".join(action_items)
        await cl.Message(
            content="### 📋 Detected Action Items",
            elements=[
                cl.Text(name="Action Items", content=actions_text, display="inline")
            ]
        ).send()

    # If clickup was involved, show status
    clickup_status = result.get("clickup_status")
    if clickup_status and "Skipped" not in clickup_status:
        await cl.Message(
            content=f"🚀 **ClickUp Sync**: {clickup_status}",
            author="System"
        ).send()

if __name__ == "__main__":
    # This allows running the script directly with 'python app_chainlit.py'
    # though 'chainlit run app_chainlit.py' is the standard way.
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)
