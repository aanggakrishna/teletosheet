# Changelog: Alert Update System

## Tanggal: 15 Desember 2025

### 🎯 Tujuan Perubahan
Mengubah sistem alert agar **tidak membuat row baru** setiap kali ada alert update (2x, 3x, 5x, 10x), melainkan **update row yang sama** menggunakan `message_id` dan reply system.

---

## 📝 Perubahan Detail

### 1. **Struktur Google Sheets** - Penambahan 2 Kolom Baru

#### Header Lama (39 kolom):
```
nomor, timestamp_received, channel_id, channel_name, ca, token_name, ...
```

#### Header Baru (41 kolom):
```
nomor, timestamp_received, channel_id, channel_name, message_id, ca, token_name, ...
... , alert_history_last, update_history, error_log, link_dexscreener, link_pump
```

**Kolom Baru:**
- **`message_id`** (Kolom E): Menyimpan Telegram message ID dari signal awal
- **`update_history`** (Kolom AN): Menyimpan history semua alert update dalam format:
  ```
  2025-12-15 10:30:45 | 2x alert | Gain: 2.07x | MC: $104,120 | Time: 47m
  2025-12-15 10:45:20 | 3x alert | Gain: 3.12x | MC: $156,600 | Time: 62m
  ```

---

### 2. **Perubahan di `signal_parser.py`**

#### A. Function `parse_new_signal()`
**Sebelum:**
```python
def parse_new_signal(message_text, channel_id, channel_name):
```

**Sesudah:**
```python
def parse_new_signal(message_text, channel_id, channel_name, message_id):
    data['message_id'] = message_id
    data['update_history'] = ''
```

#### B. Function `parse_alert_update()`
**Penambahan parsing:**
- ✅ Token name dari emoji 🪙
- ✅ Time elapsed (⏱️ Time: 47m)
- ✅ Gain value (📈 Gain: 2.07x)
- ✅ Peak value (🏆 Peak: 2.07x)
- ✅ Entry MC dan Current MC

---

### 3. **Perubahan di `sheets_handler.py`**

#### A. Function `update_alert_from_message()` - MAJOR CHANGE

**Sebelum:**
```python
def update_alert_from_message(self, ca, alert_data):
    row_index = self.find_row_by_ca(ca)  # Cari berdasarkan CA
```

**Sesudah:**
```python
def update_alert_from_message(self, reply_to_message_id, alert_data):
    # 1. Cari berdasarkan message_id (reply)
    row_index = self.find_row_by_message_id(reply_to_message_id)
    
    # 2. Fallback: cari berdasarkan CA jika tidak ada reply
    if not row_index and alert_data.get('ca'):
        row_index = self.find_row_by_ca(ca)
    
    # 3. Update peak, alert timestamps, dan history
    self.append_update_history(row_index, update_msg)
```

#### B. Function Baru: `find_row_by_message_id()`
```python
def find_row_by_message_id(self, message_id):
    message_id_column = self.sheet.col_values(5)  # Column E
    if message_id_str in message_id_column:
        return message_id_column.index(message_id_str) + 1
```

#### C. Function Baru: `append_update_history()`
```python
def append_update_history(self, row_index, update_msg):
    existing_history = self.sheet.cell(row_index, 39).value
    new_history = f"{existing_history}\n{update_msg}" if existing_history else update_msg
    self.sheet.update(f"AN{row_index}", [[new_history]])
```

#### D. Penyesuaian Kolom (semua bergeser +1 karena penambahan message_id)
| Item | Kolom Lama | Kolom Baru |
|------|-----------|-----------|
| CA | E | F |
| price_5min | P | Q |
| mc_5min | Q | R |
| ... | ... | ... |
| peak_mc | AE | AF |
| peak_multiplier | AF | AG |
| current_status | AG | AH |
| alert_2x_time | AH | AI |
| alert_history_last | AL | AM |
| update_history | - | AN |
| error_log | AM | AO |

---

### 4. **Perubahan di `main.py`**

#### Event Handler `handle_new_message()`

**Sebelum:**
```python
@client.on(events.NewMessage(chats=CHANNEL_IDS))
async def handle_new_message(event):
    message_text = event.message.message
    
    if is_signal_message(message_text):
        signal_data = parse_new_signal(message_text, channel_id, channel_name)
    elif is_alert_message(message_text):
        sheets_handler.update_alert_from_message(alert_data['ca'], alert_data)
```

**Sesudah:**
```python
@client.on(events.NewMessage(chats=CHANNEL_IDS))
async def handle_new_message(event):
    message_id = event.message.id
    reply_to_message_id = event.message.reply_to_msg_id
    
    # Alert update PERTAMA (check dulu sebelum signal)
    if is_alert_message(message_text):
        alert_data = parse_alert_update(message_text)
        if reply_to_message_id:
            # Update row yang sama menggunakan reply_to_message_id
            sheets_handler.update_alert_from_message(reply_to_message_id, alert_data)
        elif alert_data.get('ca'):
            # Fallback jika tidak ada reply
            sheets_handler.update_alert_from_message(None, alert_data)
    
    # Signal baru KEDUA
    elif is_signal_message(message_text):
        signal_data = parse_new_signal(message_text, channel_id, channel_name, message_id)
```

**Key Changes:**
1. ✅ Capture `message_id` dan `reply_to_message_id`
2. ✅ Prioritas check: Alert dulu, baru Signal (karena alert lebih critical)
3. ✅ Pass `message_id` ke `parse_new_signal()`
4. ✅ Pass `reply_to_message_id` ke `update_alert_from_message()`

---

## 🔄 Workflow Baru

### Scenario 1: Signal Baru Masuk
```
1. Bot terima pesan signal baru (message_id: 12345)
2. Parse signal → dapat data lengkap
3. Simpan ke Google Sheets row baru dengan message_id = 12345
```

**Hasil di Sheet:**
| nomor | timestamp | message_id | token_name | ca | mc_entry | ... |
|-------|-----------|------------|------------|-----|----------|-----|
| 5 | 2025-12-15 10:00 | 12345 | Kung Fu Hamster | GQx3p7... | 50200 | ... |

---

### Scenario 2: Alert Update (2x) - ADA REPLY
```
1. Bot terima pesan "2x ALERT" (message_id: 12346, reply_to: 12345)
2. Parse alert → dapat multiplier, gain, current MC, time
3. Cari row dengan message_id = 12345
4. Update row tersebut:
   - peak_multiplier = 2.07
   - alert_2x_time = "2025-12-15 10:47:30"
   - update_history += "2025-12-15 10:47:30 | 2x alert | Gain: 2.07x | MC: $104,120 | Time: 47m"
```

**Hasil di Sheet (row yang sama):**
| ... | peak_multiplier | alert_2x_time | update_history |
|-----|----------------|---------------|----------------|
| ... | 2.07 | 2025-12-15 10:47:30 | 2025-12-15 10:47:30 \| 2x alert \| Gain: 2.07x \| MC: $104,120 \| Time: 47m |

---

### Scenario 3: Alert Update (3x) - ADA REPLY
```
1. Bot terima "3x ALERT" (reply_to: 12345)
2. Update row yang sama lagi
3. update_history bertambah baris baru
```

**Hasil:**
```
update_history:
2025-12-15 10:47:30 | 2x alert | Gain: 2.07x | MC: $104,120 | Time: 47m
2025-12-15 11:05:15 | 3x alert | Gain: 3.12x | MC: $156,600 | Time: 65m
```

---

### Scenario 4: Alert Update TANPA REPLY (Fallback)
```
1. Bot terima "2x ALERT" tapi TIDAK ada reply_to_message_id
2. Parse alert → extract CA dari pesan
3. Cari row berdasarkan CA
4. Update row tersebut
```

---

## ✅ Keuntungan Sistem Baru

1. **📊 Data Terorganisir**: Semua update untuk 1 token ada di 1 row
2. **📈 History Lengkap**: Kolom `update_history` menyimpan semua alert chronologically
3. **🔗 Relationship Jelas**: `message_id` dan reply system menghubungkan signal dan alert
4. **💾 Hemat Space**: Tidak ada duplicate row untuk token yang sama
5. **📱 Easy Tracking**: Tinggal lihat 1 row untuk semua info token
6. **🔍 Debugging**: Bisa trace alert kembali ke signal awal via message_id

---

## 🧪 Testing

### Test Case 1: Signal Baru
```
Input: Pesan signal "Kung Fu Hamster..." (message_id: 12345)
Expected: Row baru dengan message_id = 12345
```

### Test Case 2: Alert dengan Reply
```
Input: "2x ALERT" (reply_to: 12345)
Expected: Update row dengan message_id = 12345, tambah update_history
```

### Test Case 3: Alert tanpa Reply (Fallback)
```
Input: "2x ALERT" dengan CA di body (no reply)
Expected: Cari row by CA, update row tersebut
```

---

## 📌 Notes

- **Backward Compatibility**: Row lama tanpa message_id tetap bisa diupdate via CA (fallback)
- **Column Shift**: Semua column setelah message_id bergeser +1 kolom
- **Update History Format**: Multiline string, setiap alert = 1 baris baru
- **Peak Tracking**: Peak tetap diupdate otomatis jika ada nilai lebih tinggi

---

## 🚀 Next Steps

1. ✅ Test dengan signal real dari Telegram
2. ✅ Monitor update_history format di Google Sheets
3. ✅ Verifikasi reply_to_message_id detection
4. 🔄 (Optional) Add visualization untuk update_history
5. 🔄 (Optional) Add alert notification summary

