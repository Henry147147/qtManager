"""Shared scanner constants, enums, and dataclasses."""

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path


class ScanResultType(StrEnum):
    SingleFile = "Single File"
    RARFile = "RAR File"
    RARPack = "RAR Pack"
    TargetDir = "Target Directory"
    Other = "Other File not of interest"


@dataclass
class ScanResult:
    path: Path
    result_type: ScanResultType
    sub_files: list["ScanResult"] = field(default_factory=list)


class TargetMedia(StrEnum):
    Video = "Video"
    Audio = "Audio"
    Photo = "Photo"
    Application = "Application"
    Other = "Other"


TARGET_MEDIA_LOOKUP = {
    TargetMedia.Video: {
        "3gp",
        "avi",
        "flv",
        "m4v",
        "mkv",
        "mov",
        "mp4",
        "mpeg",
        "mpg",
        "ts",
        "webm",
        "wmv",
    },
    TargetMedia.Audio: {
        "aac",
        "flac",
        "m4a",
        "mp3",
        "ogg",
        "opus",
        "wav",
        "wma",
    },
    TargetMedia.Photo: {
        "bmp",
        "gif",
        "heic",
        "jpeg",
        "jpg",
        "png",
        "tif",
        "tiff",
        "webp",
    },
    TargetMedia.Application: {
        "apk",
        "appimage",
        "deb",
        "dmg",
        "exe",
        "iso",
        "msi",
        "pkg",
        "rpm",
    },
    TargetMedia.Other: set(),
}


COMPRESSED_FILE_EXTENSIONS = {
    "rar",
}
