from langchain.tools import tool
import requests
from config.settings import CLICKUP_API_KEY,CLICKUP_TASK_ID

@tool
def post_to_clickup_tool(message: str, task_id: str = None) -> str:
    """Posts a comment or update to a specified ClickUp task.
    If task_id is not provided, it defaults to the CLICKUP_TASK_ID in environment variables.
    """
    
    target_task_id = task_id or CLICKUP_TASK_ID
    if not target_task_id:
        return "Error: No ClickUp Task ID provided or found in settings."

    url = f"https://api.clickup.com/api/v2/task/{target_task_id}/comment"
    
    headers = {
        "Authorization": CLICKUP_API_KEY,
        "Content-Type": "application/json"
    }
    data = {"comment_text": message}

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return f"Successfully posted to ClickUp task {target_task_id}."
        else:
            return f"Failed to post to ClickUp: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error posting to ClickUp: {str(e)}"

