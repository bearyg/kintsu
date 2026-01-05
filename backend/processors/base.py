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
    def process(self, file_path: str, original_filename: str, sibling_files: List[str] = None, **kwargs) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Process the file and return:
        1. A list of valid Shard data dictionaries.
        2. A list of debug/excluded item dictionaries (if debug mode is enabled).
        """
        pass
