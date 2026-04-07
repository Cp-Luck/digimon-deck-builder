import scripts.sortall_cards as sorter


def test_parse_card_id_extracts_set_and_number():
    assert sorter.parse_card_id("ST19-03") == ("ST19", 3, "")
    assert sorter.parse_card_id("P-021") == ("P", 21, "")
    assert sorter.parse_card_id("EX10-055") == ("EX10", 55, "")


def test_group_cards_by_set_sorts_within_each_folder():
    cards = [
        {"id": "ST19-10", "name": "Card B"},
        {"id": "ST19-03", "name": "Card A"},
        {"id": "BT1-005", "name": "Card D"},
        {"id": "BT1-001", "name": "Card C"},
    ]

    grouped = sorter.group_cards_by_set(cards)

    assert list(grouped.keys()) == ["BT1", "ST19"]
    assert [card["id"] for card in grouped["ST19"]] == ["ST19-03", "ST19-10"]
    assert [card["id"] for card in grouped["BT1"]] == ["BT1-001", "BT1-005"]
