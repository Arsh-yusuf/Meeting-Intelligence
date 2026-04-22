from sources.base import MeetingSource
from typing import List, Dict
import requests

class FathomSource(MeetingSource):
    def __init__(self, links: List[str]):
        self.links = links

    def fetch_meetings(self) -> List[Dict[str, str]]:
        meetings = []
        for i, link in enumerate(self.links):
            # In a real scenario, we would scrape the Fathom link or use their API
            # For now, we simulate fetching the transcript
            meetings.append({
                "meeting_id": f"fathom_{i}",
                "transcript": f"This is a simulated transcript from Fathom link: {link}. The discussion focused on project milestones and budget allocation.",
                "source": "fathom",
                "link": link
            })
        return meetings
