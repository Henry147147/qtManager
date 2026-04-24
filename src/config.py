"""Configuration schema and CLI parsing for qtManager."""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


DEFAULT_RENAME_TEMPLATE = "{title} ({year}) [{imdb_id}]{ext}"
VALID_MEDIA_TYPES = {"movie", "shows"}


def _coerce_string_list(value: Any, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list of strings.")
    if not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field_name} must contain only strings.")
    return value


def _coerce_dict(value: Any, field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object.")
    return value


@dataclass(slots=True)
class QBittorrentConfig:
    host: str = "localhost"
    port: int = 8080
    username: str = ""
    password: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QBittorrentConfig":
        return cls(
            host=str(data.get("host", "localhost")),
            port=int(data.get("port", 8080)),
            username=str(data.get("username", "")),
            password=str(data.get("password", "")),
        )

    def validate(self) -> None:
        if self.port <= 0:
            raise ValueError("qbittorrent.port must be a positive integer.")
        if bool(self.username) != bool(self.password):
            raise ValueError(
                "qbittorrent.username and qbittorrent.password must both be set or both be empty."
            )


@dataclass(slots=True)
class LLMConfig:
    enabled: bool = False
    api_base_url: str = ""
    api_key: str = ""
    model: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LLMConfig":
        return cls(
            enabled=bool(data.get("enabled", False)),
            api_base_url=str(data.get("api_base_url", "")),
            api_key=str(data.get("api_key", "")),
            model=str(data.get("model", "")),
        )


@dataclass(slots=True)
class IMDbConfig:
    enabled: bool = False
    insert_id_into_filename: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IMDbConfig":
        return cls(
            enabled=bool(data.get("enabled", False)),
            insert_id_into_filename=bool(data.get("insert_id_into_filename", True)),
        )


@dataclass(slots=True)
class CategoryConfig:
    name: str
    media_type: str = "movie"
    source_directories: list[str] = field(default_factory=list)
    destination_directory: str = ""
    rename_template: str = DEFAULT_RENAME_TEMPLATE
    post_move_category: str = ""
    extract_rars: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CategoryConfig":
        name = str(data.get("name", "")).strip()
        if not name:
            raise ValueError("Each category must define a non-empty name.")

        return cls(
            name=name,
            media_type=str(data.get("media_type", "movie")).strip().lower(),
            source_directories=_coerce_string_list(
                data.get("source_directories"), f"categories[{name}].source_directories"
            ),
            destination_directory=str(data.get("destination_directory", "")).strip(),
            rename_template=str(data.get("rename_template", DEFAULT_RENAME_TEMPLATE)),
            post_move_category=str(data.get("post_move_category", "")).strip(),
            extract_rars=bool(data.get("extract_rars", True)),
        )

    def validate(self) -> None:
        if self.media_type not in VALID_MEDIA_TYPES:
            raise ValueError(
                f"categories[{self.name}].media_type must be one of {sorted(VALID_MEDIA_TYPES)}."
            )
        if not self.source_directories:
            raise ValueError(f"categories[{self.name}].source_directories is required.")
        if not self.destination_directory:
            raise ValueError(f"categories[{self.name}].destination_directory is required.")


@dataclass(slots=True)
class AppConfig:
    qbittorrent: QBittorrentConfig = field(default_factory=QBittorrentConfig)
    categories: list[CategoryConfig] = field(default_factory=list)
    imdb: IMDbConfig = field(default_factory=IMDbConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    log_level: str = "INFO"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppConfig":
        categories_data = data.get("categories", [])
        if not isinstance(categories_data, list):
            raise ValueError("categories must be a list of objects.")

        config = cls(
            qbittorrent=QBittorrentConfig.from_dict(
                _coerce_dict(data.get("qbittorrent"), "qbittorrent")
            ),
            categories=[
                CategoryConfig.from_dict(
                    _coerce_dict(category, f"categories[{index}]")
                )
                for index, category in enumerate(categories_data)
            ],
            imdb=IMDbConfig.from_dict(_coerce_dict(data.get("imdb"), "imdb")),
            llm=LLMConfig.from_dict(_coerce_dict(data.get("llm"), "llm")),
            log_level=str(data.get("log_level", "INFO")).upper(),
        )
        config.validate()
        return config

    @classmethod
    def from_json_file(cls, path: str | Path) -> "AppConfig":
        config_path = Path(path)
        raw_data = json.loads(config_path.read_text(encoding="utf-8"))
        if not isinstance(raw_data, dict):
            raise ValueError("Config file root must be a JSON object.")
        return cls.from_dict(raw_data)

    def validate(self) -> None:
        self.qbittorrent.validate()

        if not self.categories:
            raise ValueError("At least one category must be defined.")

        if getattr(logging, self.log_level, None) is None:
            raise ValueError(f"Unsupported log_level: {self.log_level}")

        seen_names: set[str] = set()
        for category in self.categories:
            if category.name in seen_names:
                raise ValueError(f"Duplicate category name: {category.name}")
            seen_names.add(category.name)
            category.validate()

    def to_pretty_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Load and validate qtManager configuration from JSON."
    )
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to the JSON config file.",
    )
    parser.add_argument(
        "--dump-config",
        action="store_true",
        help="Print the normalized config and exit.",
    )
    parser.add_argument(
        "--check-qbittorrent",
        action="store_true",
        help="Connect to qBittorrent using the loaded config and print version info.",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)
