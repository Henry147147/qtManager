from typing import Callable
import logging

logger = logging.getLogger(__name__)
logger.info = print
logger.error = print
logger.debug = print

class Scanner:
    def __init__(self, path: Path, interval: int, on_scan_result: Callable[Path, None]):
        self.path = path
        self.interval = interval
        self.on_scan_result = on_scan_result
        self.to_process = set()
        self.processing = set()
        logger.debug(f"Created scanner for path=[{path}] with scan interval: {interval}")
    
    def scan_once(self):
        for item in self.path.iterdir():
            print(item)

if __name__ == "__main__":
    Scanner("")
    

    
