"""Main entry point for the git-workflow tool"""

import logging

from .cli import cli

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    cli()
