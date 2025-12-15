# Visualisasi Sistem Alert Update Baru

## 🔄 Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    TELEGRAM CHANNEL                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  MESSAGE TYPE DETECTION                                          │
│  • is_signal_message() → New Token Signal                       │
│  • is_alert_message() → Alert Update (2x, 3x, 5x, 10x)         │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
         ┌──────────────────┐  ┌──────────────────┐
         │  SIGNAL BARU     │  │  ALERT UPDATE    │
         └──────────────────┘  └──────────────────┘
                    │                   │
                    ▼                   ▼
         ┌──────────────────┐  ┌──────────────────┐
         │ parse_new_signal │  │parse_alert_update│
         │ + message_id     │  │+ reply_to_msg_id │
         └──────────────────┘  └──────────────────┘
                    │                   │
                    ▼                   ▼
         ┌──────────────────┐  ┌──────────────────┐
         │ APPEND NEW ROW   │  │  UPDATE SAME ROW │
         │ (sheets_handler) │  │  (find by msg_id)│
         └──────────────────┘  └──────────────────┘
                    │                   │
                    ▼                   ▼
         ┌──────────────────────────────────────┐
         │        GOOGLE SHEETS                 │
         │  Row: nomor | timestamp | message_id │
         │       | ca | token | ... | history   │
         └──────────────────────────────────────┘
```

---

## 📊 Data Structure

### Signal Message (Input)
```
Kung Fu Hamster               ← token_name
✅ Dex Paid
⛓️ Chain: Solana              ← chain
💵 Price: $0.00005019992763   ← price_entry
💰 Market Cap: $50.20K        ← mc_entry
💧 Liquidity: $0.00           ← liquidity
📊 Volume 24h: $129.99K       ← volume_24h
📦 Bundles: 14 (14%)          ← bundles_percent
🎯 Snipers: 14 (20%)          ← snipers_percent
👨‍💻 Dev: 0%                   ← dev_percent
🎯 Confidence: 85%            ← confidence_score
📋 Contract: GQx3p7a...       ← ca
```

### Alert Message (Input)
```
2x ALERT                      ← multiplier

🪙 Kung Fu Hamster            ← token_name
⛓️ Chain: Solana              ← chain
⏱️ Time: 47m                  ← time_elapsed

📊 Entry MC: $50.20K          ← entry_mc
💰 Current MC: $104.12K       ← current_mc
📈 Gain: 2.07x                ← gain
🏆 Peak: 2.07x                ← peak
```

### Google Sheets Row (Output)
```
| A    | B           | C          | D            | E          | F    | ... | AN                |
|------|-------------|------------|--------------|------------|------|-----|-------------------|
| nomor| timestamp   | channel_id | channel_name | message_id | ca   | ... | update_history    |
| 1    | 2025-12-15  | -10031...  | Test Channel | 12345      | GQx..| ... | 2025-12-15 10:47:30 | 2x alert | Gain: 2.07x | MC: $104,120 | Time: 47m
                                                                              2025-12-15 11:05:15 | 3x alert | Gain: 3.12x | MC: $156,600 | Time: 65m
```

---

## 🔗 Message Relationship

### Scenario: Signal → Multiple Alerts

```
┌─────────────────────────────────────────┐
│  Original Signal Message                │
│  ID: 12345                              │
│  "Kung Fu Hamster... CA: GQx3p7a..."   │
└─────────────────────────────────────────┘
                │
                │ Saved to Sheet Row #5
                │ with message_id = 12345
                ▼
┌─────────────────────────────────────────┐
│  Google Sheet Row #5                    │
│  message_id: 12345                      │
│  token: Kung Fu Hamster                 │
│  mc_entry: $50,200                      │
│  update_history: (empty)                │
└─────────────────────────────────────────┘
                │
                │ 47 minutes later...
                ▼
┌─────────────────────────────────────────┐
│  Alert Message (2x)                     │
│  ID: 12346                              │
│  reply_to: 12345  ◄─── IMPORTANT!      │
│  "2x ALERT... Current MC: $104.12K"    │
└─────────────────────────────────────────┘
                │
                │ Find row by message_id = 12345
                │ Update same row
                ▼
┌─────────────────────────────────────────┐
│  Google Sheet Row #5 (UPDATED)          │
│  message_id: 12345                      │
│  peak_multiplier: 2.07                  │
│  alert_2x_time: 2025-12-15 10:47:30    │
│  update_history:                        │
│    "2025-12-15 10:47:30 | 2x alert..." │
└─────────────────────────────────────────┘
                │
                │ 18 minutes later...
                ▼
┌─────────────────────────────────────────┐
│  Alert Message (3x)                     │
│  ID: 12347                              │
│  reply_to: 12345  ◄─── Same original   │
│  "3x ALERT... Current MC: $156.60K"    │
└─────────────────────────────────────────┘
                │
                │ Find row by message_id = 12345
                │ Update same row AGAIN
                ▼
┌─────────────────────────────────────────┐
│  Google Sheet Row #5 (UPDATED AGAIN)    │
│  message_id: 12345                      │
│  peak_multiplier: 3.12                  │
│  alert_3x_time: 2025-12-15 11:05:15    │
│  update_history:                        │
│    "2025-12-15 10:47:30 | 2x alert..." │
│    "2025-12-15 11:05:15 | 3x alert..." │
└─────────────────────────────────────────┘
```

---

## 🎯 Key Benefits Visualization

### Before (Old System)
```
Google Sheet:
Row 1: Kung Fu Hamster | Signal | MC: $50K  | ...
Row 2: Kung Fu Hamster | 2x Alert | MC: $104K | ... ← DUPLICATE!
Row 3: Kung Fu Hamster | 3x Alert | MC: $156K | ... ← DUPLICATE!
Row 4: Kung Fu Hamster | 5x Alert | MC: $251K | ... ← DUPLICATE!

❌ Problem: Multiple rows for same token
❌ Hard to track history
❌ Wastes space
```

### After (New System)
```
Google Sheet:
Row 1: Kung Fu Hamster | MC: $50K | Peak: 5.45x | History: [2x→3x→5x] ✅

✅ Benefit: ONE row per token
✅ Complete history in update_history column
✅ Easy to track progression
✅ Clean data structure
```

---

## 📱 Real Example Timeline

```
T+0m   │ 🆕 Signal Received
       │ Token: Kung Fu Hamster
       │ MC: $50.2K
       │ → CREATE Row #5 with message_id=12345
       │
T+47m  │ 📈 2x Alert (reply_to: 12345)
       │ Current MC: $104.12K
       │ → UPDATE Row #5
       │   • alert_2x_time = "10:47:30"
       │   • peak_multiplier = 2.07
       │   • update_history += "2x alert..."
       │
T+65m  │ 📈 3x Alert (reply_to: 12345)
       │ Current MC: $156.60K
       │ → UPDATE Row #5
       │   • alert_3x_time = "11:05:15"
       │   • peak_multiplier = 3.12
       │   • update_history += "3x alert..."
       │
T+85m  │ 📈 5x Alert (reply_to: 12345)
       │ Current MC: $251.00K
       │ → UPDATE Row #5
       │   • alert_5x_time = "11:25:10"
       │   • peak_multiplier = 5.45
       │   • update_history += "5x alert..."
       │
Result │ ✅ ONE row with complete journey
       │ From $50K → $251K (5x)
       │ All timestamps recorded
       │ Full history preserved
```

---

## 🔍 Column Index Reference

```
A  = nomor (1)
B  = timestamp_received (2)
C  = channel_id (3)
D  = channel_name (4)
E  = message_id (5)          ← NEW!
F  = ca (6)                   ← Shifted from E
G  = token_name (7)
...
Q  = price_5min (17)          ← Shifted from P
R  = mc_5min (18)
S  = change_5min (19)
...
AF = peak_mc (32)             ← Shifted from AE
AG = peak_multiplier (33)     ← Shifted from AF
AH = current_status (34)      ← Shifted from AG
AI = alert_2x_time (35)       ← Shifted from AH
AJ = alert_3x_time (36)
AK = alert_5x_time (37)
AL = alert_10x_time (38)
AM = alert_history_last (39)  ← Shifted from AL
AN = update_history (40)      ← NEW!
AO = error_log (41)           ← Shifted from AM
AP = link_dexscreener (42)
AQ = link_pump (43)
```

---

## 🚀 Implementation Checklist

- [x] Add `message_id` column to headers
- [x] Add `update_history` column to headers
- [x] Update `parse_new_signal()` to accept message_id
- [x] Update `parse_alert_update()` to extract more data
- [x] Create `find_row_by_message_id()` function
- [x] Create `append_update_history()` function
- [x] Update `update_alert_from_message()` to use reply_to
- [x] Update `main.py` event handler to capture IDs
- [x] Shift all column mappings by +1
- [x] Create test script
- [x] Create documentation

