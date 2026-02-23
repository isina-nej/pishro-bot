#!/usr/bin/env python3
"""Entry point for the Pishro investment bot."""

import asyncio
import sys
from pathlib import Path

# Add app to path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from app.bot import main


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✓ Bot stopped")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
