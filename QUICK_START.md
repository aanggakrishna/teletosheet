# Quick Start Guide - Alert Update System

## 🎯 Ringkasan Perubahan

Sekarang bot **TIDAK LAGI** membuat row baru untuk setiap alert (2x, 3x, 5x, 10x).  
Semua alert akan **UPDATE ROW YANG SAMA** menggunakan system reply Telegram.

---

## 📊 Struktur Data Baru

### Google Sheets Columns (41 total)
```
1.  nomor
2.  timestamp_received
3.  channel_id
4.  channel_name
5.  message_id          ← 🆕 BARU!
6.  ca
7.  token_name
8.  chain
9.  price_entry
10. mc_entry
11. liquidity
12. volume_24h
13. bundles_percent
14. snipers_percent
15. dev_percent
16. confidence_score
17-31. [Tracking data 5min, 10min, 15min, 30min, 60min]
32. peak_mc
33. peak_multiplier
34. current_status
35. alert_2x_time
36. alert_3x_time
37. alert_5x_time
38. alert_10x_time
39. alert_history_last
40. update_history      ← 🆕 BARU!
41. error_log
42. link_dexscreener
43. link_pump
```

---

## 🚀 Cara Kerja

### 1️⃣ Signal Baru Masuk
```
Input: Signal message dari Telegram
       Message ID: 12345

Bot Action:
  ✅ Parse signal
  ✅ Simpan ke row baru dengan message_id = 12345
  ✅ Status: active

Result:
  Row #10 created
  - message_id: 12345
  - token: "Kung Fu Hamster"
  - mc_entry: $50,200
  - update_history: (kosong)
```

### 2️⃣ Alert 2x Masuk (Reply ke Signal)
```
Input: 2x ALERT message
       Reply to Message ID: 12345

Bot Action:
  ✅ Detect alert message
  ✅ Find row by message_id = 12345
  ✅ Update row tersebut

Result:
  Row #10 updated (BUKAN row baru!)
  - peak_multiplier: 2.07
  - alert_2x_time: "2025-12-15 10:47:30"
  - update_history: "2025-12-15 10:47:30 | 2x alert | Gain: 2.07x | MC: $104,120 | Time: 47m"
```

### 3️⃣ Alert 3x Masuk (Reply ke Signal)
```
Input: 3x ALERT message
       Reply to Message ID: 12345

Bot Action:
  ✅ Find row by message_id = 12345
  ✅ Update row tersebut (lagi!)

Result:
  Row #10 updated again
  - peak_multiplier: 3.12
  - alert_3x_time: "2025-12-15 11:05:15"
  - update_history: 
      "2025-12-15 10:47:30 | 2x alert | Gain: 2.07x | MC: $104,120 | Time: 47m
       2025-12-15 11:05:15 | 3x alert | Gain: 3.12x | MC: $156,600 | Time: 65m"
```

---

## 📋 Data yang Diparse

### Signal Message Format
```
Token Name Here
✅ Dex Paid
⛓️ Chain: Solana
💵 Price: $0.00005
💰 Market Cap: $50.20K
💧 Liquidity: $0.00
📊 Volume 24h: $129.99K
📦 Bundles: 14 (14%)
🎯 Snipers: 14 (20%)
👨‍💻 Dev: 0%
🎯 Confidence: 85%
📋 Contract: [CA_ADDRESS]
```

**Extracted Data:**
- token_name, chain, price, MC, liquidity, volume
- bundles %, snipers %, dev %, confidence %
- Contract Address (CA)
- Message ID (auto)

### Alert Message Format
```
2x ALERT

🪙 Token Name
⛓️ Chain: Solana
⏱️ Time: 47m

📊 Entry MC: $50.20K
💰 Current MC: $104.12K
📈 Gain: 2.07x
🏆 Peak: 2.07x
```

**Extracted Data:**
- Multiplier (2x, 3x, 5x, 10x)
- Token name
- Time elapsed
- Entry MC, Current MC
- Gain, Peak
- Reply to Message ID (auto)

---

## 🔍 Finding Logic

Bot mencari row untuk update dengan prioritas:

1. **First:** Cari by `message_id` (dari reply_to)
   - Paling akurat
   - Langsung ketemu row yang tepat

2. **Fallback:** Cari by `CA` (Contract Address)
   - Jika alert tidak ada reply
   - Parse CA dari message body

---

## 💡 Use Cases

### ✅ Normal Case (Ada Reply)
```
Signal → message_id = 12345 → Row #10
Alert 2x → reply_to = 12345 → Update Row #10
Alert 3x → reply_to = 12345 → Update Row #10
Alert 5x → reply_to = 12345 → Update Row #10
```
**Result:** 1 row, lengkap dengan semua alert history

### ✅ Fallback Case (Tidak Ada Reply)
```
Signal → CA = "GQx3p7a..." → Row #10
Alert 2x → CA in body = "GQx3p7a..." → Update Row #10
```
**Result:** Tetap update row yang sama via CA matching

### ❌ Edge Case (CA Not Found)
```
Alert 2x → no reply, no CA → Skip
```
**Result:** Log warning, tidak ada update

---

## 🧪 Testing

### Manual Test
```bash
# Activate venv
source venv/bin/activate

# Run test script
python test_alert_system.py
```

**Expected Output:**
```
✅ Signal parsed successfully!
✅ Alert parsed successfully!
✅ Update history format correct
```

### Live Test
```bash
# Run bot
python main.py

# Monitor logs
tail -f logs/bot.log

# Look for:
📥 New signal: [Token] from [Channel]
🚨 Alert triggered: 2x [Token]
✅ Alert updated: 2x for message_id [ID]
```

---

## 📖 Reading Update History

Update history format (multiline):
```
2025-12-15 10:47:30 | 2x alert | Gain: 2.07x | MC: $104,120 | Time: 47m
2025-12-15 11:05:15 | 3x alert | Gain: 3.12x | MC: $156,600 | Time: 65m
2025-12-15 11:25:10 | 5x alert | Gain: 5.00x | MC: $251,000 | Time: 1h 25m
```

Each line contains:
- Timestamp
- Alert type (2x, 3x, 5x, 10x)
- Gain multiplier
- Current Market Cap
- Time elapsed from signal

---

## 🔧 Troubleshooting

### Problem: Alert tidak update row
**Solution:**
1. Check apakah alert message adalah reply dari signal
2. Check message_id tersimpan di sheet
3. Check logs untuk error
4. Enable debug: `ENABLE_DEBUG_LOGS=true`

### Problem: Update history tidak muncul
**Solution:**
1. Pastikan kolom AN (update_history) ada di sheet
2. Check headers updated
3. Re-run bot untuk refresh headers

### Problem: Duplicate rows masih terjadi
**Solution:**
1. Check apakah alert message punya reply_to
2. Check parsing `reply_to_msg_id` di main.py
3. Check logs: `Message ID: xxx, Reply to: xxx`

---

## 📚 Documentation Files

- `CHANGELOG_ALERT_UPDATE.md` - Detailed changelog
- `ALERT_SYSTEM_VISUAL.md` - Visual diagrams
- `README.md` - General documentation
- `test_alert_system.py` - Test script

---

## ⚡ Quick Commands

```bash
# Run bot
python main.py

# Run tests
python test_alert_system.py

# Check logs
tail -f logs/bot.log

# Debug mode
ENABLE_DEBUG_LOGS=true python main.py
```

---

## 🎓 Key Takeaways

1. ✅ **1 Token = 1 Row** (tidak ada duplicate)
2. ✅ **Message ID = Unique Identifier**
3. ✅ **Reply System = Relationship Tracker**
4. ✅ **Update History = Complete Timeline**
5. ✅ **Fallback to CA** (jika tidak ada reply)

---

Need help? Check:
- Main code: `main.py`, `signal_parser.py`, `sheets_handler.py`
- Logs: `logs/bot.log`
- Test: `python test_alert_system.py`
