# ✅ KONFIRMASI: 1 Token = 1 Row

## 🎯 Alur Data yang Benar

### 1️⃣ Signal Baru Masuk
```
📥 Signal: "Kung Fu Hamster"
   Message ID: 12345
   
   ↓
   
🆕 BUAT ROW BARU
   Row #10: message_id=12345, token="Kung Fu Hamster", mc=$50K
```

### 2️⃣ Alert 2x Masuk (Reply ke Signal)
```
📈 2x ALERT (reply_to: 12345)
   Current MC: $104K
   
   ↓
   
🔄 UPDATE ROW YANG SAMA (Row #10)
   ✅ Tidak buat row baru!
   ✅ Update kolom di KANAN:
      - alert_2x_time = "10:47:30"
      - peak_multiplier = 2.07
      - update_history += "2x alert..."
```

### 3️⃣ Alert 3x Masuk (Reply ke Signal)
```
📈 3x ALERT (reply_to: 12345)
   Current MC: $156K
   
   ↓
   
🔄 UPDATE ROW YANG SAMA (Row #10) LAGI
   ✅ Tidak buat row baru!
   ✅ Update kolom di KANAN:
      - alert_3x_time = "11:05:15"
      - peak_multiplier = 3.12
      - update_history += "3x alert..."
```

---

## 📊 Visual Google Sheets

### ❌ SISTEM LAMA (Salah - banyak row)
```
Row 10: Kung Fu Hamster | Signal | MC: $50K
Row 11: Kung Fu Hamster | 2x Alert | MC: $104K  ← DUPLICATE!
Row 12: Kung Fu Hamster | 3x Alert | MC: $156K  ← DUPLICATE!
Row 13: Kung Fu Hamster | 5x Alert | MC: $251K  ← DUPLICATE!
```

### ✅ SISTEM BARU (Benar - 1 row saja)
```
Row 10: Kung Fu Hamster | $50K → $251K | Peak: 5x | History: 2x→3x→5x
        [Semua data entry di KIRI] | [Semua update alert di KANAN]
```

---

## 🔍 Struktur Row (1 Token = 1 Row)

```
| A-P: DATA ENTRY (Signal)          | Q-AQ: DATA UPDATE (Tracking & Alerts) |
|------------------------------------|---------------------------------------|
| - nomor                            | - price_5min, mc_5min, change_5min   |
| - timestamp                        | - price_10min, mc_10min, change_10min|
| - channel_id, channel_name         | - price_15min, mc_15min, change_15min|
| - message_id                       | - price_30min, mc_30min, change_30min|
| - ca, token_name, chain            | - price_60min, mc_60min, change_60min|
| - price_entry, mc_entry            | - peak_mc, peak_multiplier           |
| - liquidity, volume_24h            | - alert_2x_time ← UPDATE DI SINI!    |
| - bundles%, snipers%, dev%         | - alert_3x_time ← UPDATE DI SINI!    |
| - confidence_score                 | - alert_5x_time ← UPDATE DI SINI!    |
|                                    | - alert_10x_time ← UPDATE DI SINI!   |
|                                    | - update_history ← UPDATE DI SINI!   |
```

---

## 💡 Kenapa Dijamin 1 Row Saja?

### Code Logic:
1. **Alert Detection:**
   ```python
   if is_alert_message(message_text):
       # HANYA UPDATE, tidak append!
       sheets_handler.update_alert_from_message(...)
   ```

2. **Signal Detection:**
   ```python
   elif is_signal_message(message_text):
       # HANYA APPEND untuk signal baru
       sheets_handler.append_signal(signal_data)
   ```

3. **Update Function:**
   ```python
   def update_alert_from_message(...):
       row_index = self.find_row_by_message_id(...)  # Cari row yang ada
       self.sheet.update(f"AI{row_index}", ...)      # Update cell di row itu
       # TIDAK ADA self.sheet.append_row() ← Tidak buat row baru!
   ```

---

## ✅ Jaminan:

1. ✅ **Alert TIDAK pernah membuat row baru**
2. ✅ **Alert HANYA update kolom di kanan**
3. ✅ **1 Token = 1 Row selamanya**
4. ✅ **History lengkap di 1 row**

---

## 🧪 Cara Verifikasi

Setelah bot running, check Google Sheets:

```
Scenario: 1 token dapat 3 alert (2x, 3x, 5x)

Expected Result:
✅ Total row bertambah 1 (untuk signal)
✅ Row tersebut di-update 3 kali (untuk 3 alert)
✅ BUKAN total row bertambah 4!

Cara Check:
1. Lihat nomor row terakhir sebelum signal
2. Signal masuk → row bertambah 1
3. Alert 2x masuk → row TIDAK bertambah (cek alert_2x_time terisi)
4. Alert 3x masuk → row TIDAK bertambah (cek alert_3x_time terisi)
5. Alert 5x masuk → row TIDAK bertambah (cek alert_5x_time terisi)
```

---

## 🎯 Summary

**Q: Apakah alert buat row baru?**
**A: TIDAK! Alert hanya update kolom di kanan (alert_2x_time, alert_3x_time, dll)**

**Q: Kapan row baru dibuat?**
**A: Hanya saat signal BARU masuk (token baru)**

**Q: Berapa row untuk 1 token dengan 4 alert?**
**A: Tetap 1 row! (signal di kiri, 4 alert update di kanan)**

✅ DIJAMIN 1 TOKEN = 1 ROW!
