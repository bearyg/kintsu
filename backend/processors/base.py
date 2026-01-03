from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseProcessor(ABC):
    @abstractmethod
    def can_process(self, file_path: str, source_type: str) -> bool:
        """
        Determine if this processor can handle the given file/context.
        """
        pass

    @abstractmethod
    def process(self, file_path: str, original_filename: str) -> List[Dict[str, Any]]:
        """
        Process the file and return a list of Shard data dictionaries.
        """
        pass
