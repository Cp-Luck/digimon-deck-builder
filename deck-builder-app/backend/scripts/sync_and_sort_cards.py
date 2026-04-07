"""Run the full local card refresh workflow and rebuild derived card data.

Main function: `sync_and_sort_cards()`, which updates the cached card data, regenerates the `by_set` folder structure, and refreshes the field summary files used by the frontend filters.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.sortall_cards import main as sort_cards_by_set
from scripts.summarize_card_fields import main as summarize_card_fields
from scripts.update_cards import update_cards


def sync_and_sort_cards() -> None:
    """Update the local card cache, rebuild set exports, and refresh filter summaries."""
    print("Starting card update...")
    update_cards()
    print("Card update complete. Rebuilding set folders...")
    sort_cards_by_set()
    print("Set folders rebuilt. Generating field summaries...")
    summarize_card_fields()
    print("Sync and sort workflow complete.")


def main() -> None:
    """CLI entry point for running the combined card sync and sort workflow."""
    sync_and_sort_cards()


if __name__ == "__main__":
    main()
