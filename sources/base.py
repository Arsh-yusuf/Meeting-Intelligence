from abc import ABC, abstractmethod
from typing import List, Dict

class MeetingSource(ABC):
    @abstractmethod
    def fetch_meetings(self) -> List[Dict[str, str]]:
        """
        Fetches meetings from the source.
        Returns a list of dictionaries with 'meeting_id' and 'transcript'.
        """
        pass
