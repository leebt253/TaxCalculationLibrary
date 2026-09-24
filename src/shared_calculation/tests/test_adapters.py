import io

from shared_calculation.adapters import read_csv_records


def test_read_csv_records_from_file_like_object():
    records = read_csv_records(io.StringIO("name,count\nNotebook,2\n"))

    assert records == [{"name": "Notebook", "count": "2"}]


def test_read_csv_records_from_path(tmp_path):
    source = tmp_path / "items.csv"
    source.write_text("name|count\nPen|3\n", encoding="utf-8")

    records = read_csv_records(source, delimiter="|")

    assert records == [{"name": "Pen", "count": "3"}]