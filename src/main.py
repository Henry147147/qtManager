"""Runtime entrypoint for qtManager."""

import logging
from config import AppConfig, parse_args
from typing import Optional, List


def configure_logging(level_name: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level_name),
        format="%(levelname)s %(name)s: %(message)s",
    )


def check_qbittorrent(config: AppConfig) -> None:
    if not config.qbittorrent.username or not config.qbittorrent.password:
        raise ValueError(
            "qBittorrent credentials are required when --check-qbittorrent is used."
        )

    try:
        from .api import APIWrapper
    except ImportError:
        from api import APIWrapper

    wrapper = APIWrapper(
        host=config.qbittorrent.host,
        port=config.qbittorrent.port,
        username=config.qbittorrent.username,
        password=config.qbittorrent.password,
    )
    wrapper.display_conn_info()


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    config = AppConfig.from_json_file(args.config)
    configure_logging(config.log_level)

    if args.dump_config:
        print(config.to_pretty_json())
        if not args.check_qbittorrent:
            return 0

    logger = logging.getLogger(__name__)
    logger.info(
        "Loaded config from %s with %d categories.",
        args.config,
        len(config.categories),
    )

    for category in config.categories:
        logger.info(
            "Category '%s' (%s) scans %s -> %s",
            category.name,
            category.media_type,
            category.source_directories,
            category.destination_directory,
        )

    if args.check_qbittorrent:
        check_qbittorrent(config)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
