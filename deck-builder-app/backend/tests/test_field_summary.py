"""Tests for the card field summary script.

Main coverage: grouping repeated values by field, merging `digi_type*` fields, and removing single-occurrence values.
"""

from pathlib import Path

import scripts.summarize_card_fields as summary_script


def test_build_field_summary_groups_digi_type_variants_and_removes_singletons():
    """Ensure repeated values are counted correctly and singletons are excluded from the final summary."""
    cards = [
        {
            "id": "AD1-001",
            "name": "Greymon",
            "xros_req": "Some requirement",
            "alt_effect": "Should be excluded",
            "color": "Red",
            "digi_type": "Dinosaur",
            "digi_type2": "ADVENTURE",
            "rarity": "R",
            "artist": None,
        },
        {
            "id": "AD1-002",
            "color2": "Red",
            "digi_type": "Dinosaur",
            "digi_type2": "Dragonkin",
            "rarity": "SR",
        },
        {
            "id": "AD1-003",
            "color": "Blue",
            "digi_type": "Beast",
            "digi_type2": "ADVENTURE",
            "rarity": "R",
        },
    ]

    summary = summary_script.build_field_summary(cards)

    assert summary["digi_type"] == {"ADVENTURE": 2, "Dinosaur": 2}
    assert summary["rarity"] == {"R": 2}
    assert summary["color"] == {"Red": 2}
    assert "artist" not in summary
    assert "name" not in summary
    assert "xros_req" not in summary
    assert "alt_effect" not in summary
    assert "color2" not in summary


def test_build_field_summary_normalizes_and_orders_rarity_values():
    """Ensure rarity values are merged by case and kept in Digimon rarity order."""
    cards = [
        {"id": "BT1-001", "rarity": "C"},
        {"id": "BT1-002", "rarity": "c"},
        {"id": "BT1-003", "rarity": "U"},
        {"id": "BT1-004", "rarity": "u"},
        {"id": "BT1-005", "rarity": "R"},
        {"id": "BT1-006", "rarity": "r"},
        {"id": "BT1-007", "rarity": "SR"},
        {"id": "BT1-008", "rarity": "sr"},
        {"id": "BT1-009", "rarity": "SEC"},
        {"id": "BT1-010", "rarity": "sec"},
        {"id": "BT1-011", "rarity": "P"},
        {"id": "BT1-012", "rarity": "p"},
        {"id": "BT1-013", "rarity": "UR"},
        {"id": "BT1-014", "rarity": "ur"},
    ]

    summary = summary_script.build_field_summary(cards)

    assert list(summary["rarity"].keys()) == ["C", "U", "R", "SR", "SEC", "P", "UR"]
    assert summary["rarity"] == {"C": 2, "U": 2, "R": 2, "SR": 2, "SEC": 2, "P": 2, "UR": 2}


def test_write_summary_markdown_outputs_grouped_bullets(tmp_path: Path):
    """Ensure the markdown writer formats the summary as grouped bullet lists."""
    summary = {
        "digi_type": {"ADVENTURE": 2, "Dinosaur": 2},
        "rarity": {"R": 2},
    }
    output_path = tmp_path / "field_summary.md"

    summary_script.write_summary_markdown(summary, output_path)

    content = output_path.read_text(encoding="utf-8")
    assert "## `digi_type`" in content
    assert "- `ADVENTURE`: 2" in content
    assert "## `rarity`" in content
