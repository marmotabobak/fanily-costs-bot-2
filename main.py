#!/usr/bin/env python3
"""Main entry point for the Family Costs Bot."""

import asyncio

from src.bot import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
