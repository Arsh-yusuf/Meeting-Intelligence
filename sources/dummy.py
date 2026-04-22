from sources.base import MeetingSource
from typing import List, Dict
from llm.llm_client import call_llm
from concurrent.futures import ThreadPoolExecutor

class DummyMeetingSource(MeetingSource):
    def __init__(self, count: int = 3):
        self.count = count

    def _generate_single_meeting(self, i: int) -> Dict[str, str]:
        prompt = f"Generate a unique, realistic business meeting transcript for meeting #{i+1}. Include discussion on project updates, technical challenges, and next steps."
        transcript = call_llm(prompt)
        return {
            "meeting_id": f"dummy_{i}",
            "transcript": transcript,
            "source": "dummy"
        }

    def fetch_meetings(self) -> List[Dict[str, str]]:
        print(f"Generating {self.count} dummy meeting transcripts in parallel...")
        with ThreadPoolExecutor() as executor:
            meetings = list(executor.map(self._generate_single_meeting, range(self.count)))
        return meetings
