from typing import Callable, Union
import logging
from pathlib import Path
from consts import (
    COMPRESSED_FILE_EXTENSIONS,
    TARGET_MEDIA_LOOKUP,
    ScanResult,
    ScanResultType,
    TargetMedia,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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

    def parse_path_result(self, path: Path) -> ScanResult:
        if path.is_dir():
            classified_sub_files = []
            for file in path.iterdir():
                if file.is_dir():
                    sub_file_result = self.parse_path_result(file)
                    classified_sub_files.append(sub_file_result)
            if any(sub_result.result_type != ScanResultType.Other for sub_result in classified_sub_files):
                result_type = ScanResultType.TargetDir
            else:
                result_type = ScanResultType.Other
            return ScanResult(path, result_type, classified_sub_files)
        else:
            if self.is_target_file_type(path):
                return ScanResult(path, ScanResultType.SingleFile)
            elif self.is_compressed(path):
                return ScanResult(path, ScanResultType.RARFile)
            return ScanResult(path, ScanResultType.Other)

    
    def is_target_file_type(self, path: Path) -> bool:
        target_exts = TARGET_MEDIA_LOOKUP[self.target_media]
        if path.is_dir():
            return False

        suffix = path.suffix.lower().lstrip(".")
        if not suffix:
            return False

        return suffix in target_exts

    @staticmethod
    def is_compressed(path: Path):
        if path.is_dir():
            return False

        suffix = path.suffix.lower().lstrip(".")
        if not suffix:
            return False

        return suffix in COMPRESSED_FILE_EXTENSIONS


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG, format="%(levelname)s %(name)s: %(message)s"
    )
    scanner = Scanner("test_assets", 10, lambda x: x)
    paths = scanner.scan_once()
    for path in paths:
        scanner.parse_path_result(path)
