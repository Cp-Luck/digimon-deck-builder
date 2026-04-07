"""Run the full local card refresh workflow and rebuild the per-set exports.

Main function: `sync_and_sort_cards()`, which updates the cached card data and then regenerates the `by_set` folder structure.
"""

from __future__ import annotations

from scripts.sortall_cards import main as sort_cards_by_set
from scripts.update_cards import update_cards


def sync_and_sort_cards() -> None:
    """Update the local card cache and then rebuild the sorted set exports."""
    print("Starting card update...")
    update_cards()
    print("Card update complete. Rebuilding set folders...")
    sort_cards_by_set()
    print("Sync and sort workflow complete.")


def main() -> None:
    """CLI entry point for running the combined card sync and sort workflow."""
    sync_and_sort_cards()


if __name__ == "__main__":
    main()
