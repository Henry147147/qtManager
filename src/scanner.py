from typing import Callable, Union, List
import logging
from pathlib import Path
from enum import StrEnum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ScanResultType(StrEnum):
    SingleFile = "Single File"
    FilePack = "File Pack"
    RARFile = "RAR File"
    RARPack = "RAR Pack"
    SingleFileDir = "Single File Directory"
    Other = "Other File not of interest"


@dataclass
class ScanResult:
    path: Path
    result_type: ScanResultType
    sub_files: List["ScanResult"] = field(default_factory=list)


class TargetMedia(StrEnum):
    Video = "Video"
    Audio = "Audio"
    Photo = "Photo"
    Application = "Application"
    Other = "Other"


class Scanner:
    def __init__(
        self,
        path: Union[Path, str],
        interval: int,
        on_scan_result: Callable[Path, None],
        target_media: TargetMedia = TargetMedia.Video,
    ):
        self.path = Path(path)
        self.interval = interval
        self.on_scan_result = on_scan_result
        self.target_media = target_media
        self.to_process = set()
        self.processing = set()
        logger.debug(
            f"Created scanner for path=[{path}] with scan interval: {interval}"
        )

    def scan_once(self):
        for item in self.path.iterdir():
            logger.debug(f"Found item=[{item}] in scan")
        return list(self.path.iterdir())

    @staticmethod
    def parse_path_result(path: Path):
        if path.is_dir():
            classified_sub_files = []
            for file in list(path.iterdir()):
                print(f"\t{file}")
        else:
            pass

    @staticmethod
    def is_target_file_type(path: Path):
        pass


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG, format="%(levelname)s %(name)s: %(message)s"
    )
    scanner = Scanner("test_assets", 10, lambda x: x)
    paths = scanner.scan_once()
    for path in paths:
        scanner.parse_path_result(path)
