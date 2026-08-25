"""Incrementally sync Digimon card data into the local JSON cache.

Main function: `update_cards()`, which fetches missing or incomplete cards and saves progress along the way.
"""

import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.api import get_all_cards_basic, search_card_by_number
from app.storage import (
    card_needs_refresh,
    dedupe_cards,
    get_card_identifier,
    load_cards,
    save_cards,
    save_last_updated,
)


def fetch_card_details(
    card_id: str, retries: int = 3, retry_delay: float = 2.0
) -> list[dict[str, Any]]:
    """Fetch card details with retry handling for transient API failures."""
    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            details = search_card_by_number(card_id)
            if isinstance(details, list):
                return [item for item in details if isinstance(item, dict)]
            if isinstance(details, dict):
                return [details]
            return []
        except Exception as exc:  # noqa: BLE001 — retry loop: any failure should trigger a retry, not just specific exception types
            last_error = exc
            if attempt < retries:
                print(f"Retrying {card_id} ({attempt}/{retries}) after error: {exc}")
                time.sleep(retry_delay)

    raise RuntimeError(str(last_error)) from last_error


def update_cards() -> None:
    """Update the local card cache by fetching only missing or incomplete cards."""
    basic_cards = get_all_cards_basic()
    existing_cards = dedupe_cards(load_cards())
    existing_ids = {
        card_id
        for card in existing_cards
        if (card_id := get_card_identifier(card)) is not None
    }
    refresh_ids = {
        card_id
        for card in existing_cards
        if (card_id := get_card_identifier(card)) is not None
        and card_needs_refresh(card)
    }

    pending_ids: list[str] = []
    seen_ids: set[str] = set()
    missing_count = 0
    refresh_count = 0

    for card in basic_cards:
        if not isinstance(card, dict):
            continue

        card_id = get_card_identifier(card)
        if card_id is None or card_id in seen_ids:
            continue

        seen_ids.add(card_id)

        if card_id not in existing_ids:
            pending_ids.append(card_id)
            missing_count += 1
        elif card_id in refresh_ids:
            pending_ids.append(card_id)
            refresh_count += 1

    print(f"Loaded {len(existing_cards)} unique saved cards.")
    print(f"Found {len(seen_ids)} unique API card ids.")
    print(
        f"Need to fetch {len(pending_ids)} cards "
        f"({missing_count} missing, {refresh_count} incomplete refreshes)."
    )

    if not pending_ids:
        save_cards(existing_cards)
        save_last_updated()
        print(f"Card database already up to date. Total saved: {len(existing_cards)}")
        return

    full_cards = list(existing_cards)
    failed_ids: list[str] = []
    total_pending = len(pending_ids)

    for index, card_id in enumerate(pending_ids, start=1):
        try:
            details = fetch_card_details(card_id)
            if details:
                full_cards.extend(details)
                full_cards = dedupe_cards(full_cards)
                save_cards(full_cards)

            print(f"[{index}/{total_pending}] Saved {card_id}")
        except Exception as exc:  # noqa: BLE001 — one bad card ID shouldn't abort the whole batch update
            failed_ids.append(card_id)
            print(f"[{index}/{total_pending}] Failed for {card_id}: {exc}")

    deduped_cards = dedupe_cards(full_cards)
    save_cards(deduped_cards)
    save_last_updated()

    added_count = len(deduped_cards) - len(existing_cards)
    print(
        f"Card database updated. Added {added_count} new unique cards. Total saved: {len(deduped_cards)}"
    )

    if failed_ids:
        print(f"Missing after update ({len(failed_ids)}): {', '.join(failed_ids)}")


if __name__ == "__main__":
    update_cards()
