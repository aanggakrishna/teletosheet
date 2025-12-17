# Fix: Google Sheets Duplicate Headers Error

## 🐛 Error Yang Terjadi

```
GSpreadException: the header row in the worksheet contains duplicates: ['']
To manually set the header row, use the `expected_headers` parameter of `get_all_records()`
```

## 🔍 Root Cause

Error ini terjadi ketika:
1. Sheet memiliki kolom kosong/empty di header
2. User menambah/hapus kolom manual di Google Sheets
3. gspread library tidak bisa auto-detect headers karena ada duplicates

## ✅ Solution Implemented

### 1. Buat Method `_get_expected_headers()`

```python
def _get_expected_headers(self):
    """Return list of expected headers for the sheet"""
    return [
        'nomor', 'timestamp_received', 'channel_id', 'channel_name', 'message_id',
        'ca', 'token_name', 'chain', 'price_entry', 'mc_entry', 'liquidity',
        # ... all 57 headers
        'pump_10_time', 'pump_20_time', ... 'pump_100_time',
        'ath_price', 'ath_mc', 'ath_gain_percent', 'ath_time'
    ]
```

### 2. Update `get_active_signals()` 

**Before (Error):**
```python
def get_active_signals(self):
    all_records = self.sheet.get_all_records()  # ❌ Fails on duplicate headers
```

**After (Fixed):**
```python
def get_active_signals(self):
    expected_headers = self._get_expected_headers()
    all_records = self.sheet.get_all_records(expected_headers=expected_headers)  # ✅ Works!
```

### 3. Reuse in `_ensure_headers()`

```python
def _ensure_headers(self):
    headers = self._get_expected_headers()  # Single source of truth
    existing_headers = self.sheet.row_values(1)
    if not existing_headers or existing_headers != headers:
        self.sheet.insert_row(headers, 1)
```

## 🎯 Benefits

1. **Robust**: Handles sheets with empty/duplicate columns
2. **Explicit**: Tells gspread exactly what columns to expect
3. **Maintainable**: Single method defines all headers
4. **Safe**: Won't break even if sheet has extra columns

## 🧪 Testing

Run the test script:
```bash
python test_sheets_connection.py
```

Expected output:
```
✅ Connection successful!
✅ Column count matches!
✅ No empty headers
✅ Success! Found X active signal(s)
```

## 📝 Files Changed

1. **sheets_handler.py**:
   - Added `_get_expected_headers()` method
   - Updated `_ensure_headers()` to use `_get_expected_headers()`
   - Updated `get_active_signals()` to use `expected_headers` parameter

## 🔄 Backward Compatible

- ✅ Works with existing sheets
- ✅ Works with manually edited sheets
- ✅ Works with extra empty columns
- ✅ No data migration needed

## 🚀 Status

**Fixed and Tested!** Error should no longer occur.

---

**Issue**: GSpreadException duplicate headers  
**Fix**: Use `expected_headers` parameter  
**Date**: December 17, 2025
