# Tax Calculation Library

Thư viện Python dùng để validate dữ liệu dạng bảng và tính tiền trước thuế, VAT, tiền sau thuế theo từng dòng và cho toàn bộ đơn hàng.

Thư viện không cần database, web server hoặc framework ứng dụng. Tiền tệ mặc định là KRW.

## Cài đặt

Khuyến nghị sử dụng virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
```

Nếu chỉ sử dụng thư viện, có thể cài không kèm test dependency:

```powershell
python -m pip install -e .
```

## Gọi thư viện

Public API duy nhất là:

```python
calculate(data, metadata)
```

Ví dụ đầy đủ:

```python
from decimal import Decimal

from shared_calculation import calculate

data = [
    {
        "name": "Notebook",
        "count": 2,
        "price": 1500,
        "tax": Decimal("0.1"),
        "sku": "NB-001",
    },
    {
        "name": "Pen",
        "count": 3,
        "price": 100,
        "tax": Decimal("0"),
        "sku": "P-001",
    },
]

metadata = {
    "has_header": True,
    "column_mapping": {
        "item_name": "name",
        "quantity": "count",
        "unit_price": "price",
        "vat_rate": "tax",
    },
}

result = calculate(data, metadata)

print(result.items)
print(result.total_before_tax)  # Decimal("3300.00")
print(result.total_after_tax)   # Decimal("3600.00")
```

## Input

### `data`

`data` là một iterable các record dạng mapping, thông thường là `list[dict]`.

Mỗi record phải cung cấp bốn logical field bắt buộc. Tên key thực tế có thể khác và được khai báo trong `metadata["column_mapping"]`.

| Logical field | Kiểu | Điều kiện |
|---|---|---|
| `item_name` | `str` | Không được rỗng |
| `quantity` | `int` | Số nguyên dương |
| `unit_price` | `int` | Số nguyên dương |
| `vat_rate` | `Decimal` | Trong khoảng `0..1`, bao gồm hai biên |

VAT được biểu diễn dưới dạng tỷ lệ:

- `Decimal("0")`: 0%.
- `Decimal("0.1")`: 10%.
- `Decimal("1")`: 100%.

Không dùng `float` cho VAT hoặc tiền. Ví dụ đúng là `Decimal("0.1")`, không phải `0.1`.

### `metadata`

```python
metadata = {
    "has_header": True,
    "column_mapping": {
        "item_name": "name",
        "quantity": "count",
        "unit_price": "price",
        "vat_rate": "tax",
    },
}
```

- `has_header`: mô tả source có header hay không.
- `column_mapping`: ánh xạ logical field sang tên cột thực tế.
- Các cột bổ sung không nằm trong mapping vẫn được giữ nguyên.

## Output

`calculate` trả về một `CalculationResult` gồm:

```python
result.items
result.total_before_tax
result.total_after_tax
```

Mỗi phần tử trong `result.items` là `CalculationItem`:

```python
item.original_data  # toàn bộ record ban đầu, gồm extra columns
item.before_tax     # Decimal, 2 chữ số thập phân
item.vat            # Decimal, 2 chữ số thập phân
item.after_tax      # Decimal, 2 chữ số thập phân
```

Với record Notebook ở trên:

```python
item = result.items[0]

assert item.original_data["sku"] == "NB-001"
assert item.before_tax == Decimal("3000.00")
assert item.vat == Decimal("300.00")
assert item.after_tax == Decimal("3300.00")
assert result.total_before_tax == Decimal("3300.00")
assert result.total_after_tax == Decimal("3600.00")
```

Công thức cho mỗi dòng:

```text
before_tax = quantity * unit_price
vat        = before_tax * vat_rate
after_tax  = before_tax + vat
```

Mỗi dòng được tính độc lập. Hai dòng có cùng `item_name` không bị gộp. Giá trị dòng được làm tròn đến hai chữ số bằng `ROUND_HALF_UP` trước khi cộng total.

## Validation và lỗi

Thư viện fail-fast và không tự động bỏ qua dòng lỗi. Khi input không hợp lệ, thư viện raise `ValidationError`:

```python
from decimal import Decimal

from shared_calculation import ValidationError, calculate

try:
    calculate(
        [{"name": "Notebook", "count": 0, "price": 1500, "tax": Decimal("0.1")}],
        metadata,
    )
except ValidationError as error:
    print(error.code)    # invalid_integer
    print(error.row)     # 0
    print(error.field)   # quantity
    print(error.value)   # 0
    print(error.message)
```

Các lỗi được kiểm tra gồm thiếu mapping, thiếu field, tên item rỗng, quantity/price không dương, VAT ngoài `0..1` và giá trị không thể chuyển đổi.

## CSV adapter tùy chọn

Nếu cần đọc CSV ở boundary, có thể dùng adapter:

```python
from shared_calculation.adapters import read_csv_records

records = read_csv_records("items.csv")
result = calculate(records, metadata)
```

CSV chỉ là adapter đầu vào; calculation core vẫn làm việc với records và metadata.

## Chạy test

```powershell
python -m pytest
```

Hoặc với môi trường đã tạo trong repository:

```powershell
.venv\Scripts\python.exe -m pytest
```

## Cấu trúc dự án

```text
src/shared_calculation/
├── __init__.py
├── api.py           # calculate()
├── models.py        # CalculationResult, CalculationItem
├── validation.py    # metadata và input validation
├── calculation.py   # Decimal calculations
├── exceptions.py    # ValidationError
├── adapters.py      # CSV boundary adapter
└── tests/
```
