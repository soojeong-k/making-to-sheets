from sheets_client import _col_letter, _build_data_batch


def test_col_letter_single_digits():
    assert _col_letter(1) == "A"
    assert _col_letter(26) == "Z"


def test_col_letter_double_digits():
    assert _col_letter(27) == "AA"
    assert _col_letter(28) == "AB"
    assert _col_letter(52) == "AZ"


def test_col_letter_triple_digits():
    assert _col_letter(703) == "AAA"


def test_build_data_batch_formats_rows():
    rows = [("booth1", 5000, 2000), ("booth2", 3000, 1000)]
    batch = _build_data_batch(rows)
    assert batch[0] == [1, "booth1", 5000, 2000]
    assert batch[1] == [2, "booth2", 3000, 1000]


def test_build_data_batch_empty():
    assert _build_data_batch([]) == []
