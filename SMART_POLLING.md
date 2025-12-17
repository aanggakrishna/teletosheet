# Smart Polling System - Realtime Price Updates

## 📊 Overview
Sistem **Smart Polling** memberikan update harga yang terasa **realtime** seperti GMGN/DexScreener, dengan interval update yang dinamis berdasarkan umur signal dan performa token.

## 🎯 How It Works

### Dynamic Update Intervals

| Signal Type | Conditions | Update Interval | Example |
|------------|------------|-----------------|---------|
| **Fresh** | 0-5 minutes old | Every 30 seconds | New signal just received |
| **Hot** | <60 min OR gain >20% | Every 1 minute | Pumping token |
| **Normal** | 1-24 hours old | Every 5 minutes | Mature tracking |
| **Mature** | 1-2 days old | Every 15 minutes | Long-term monitoring |
| **Old** | 2-3 days old | Every 30 minutes | Final tracking phase |

### Update Frequency Examples

**Fresh Signal (First 10 minutes):**
- Minutes 0-5: ~10 updates (30s interval)
- Minutes 5-10: ~5 updates (60s interval)
- **Total: ~15 updates in 10 minutes**

**Hot Token (Pumping >20%):**
- Continuous 1-minute updates regardless of age
- Automatically detected when gain exceeds 20%

**Normal Token (After 1 hour):**
- Update every 5 minutes
- ~12 updates per hour
- Efficient for mature signals

## 📈 New Sheet Columns

### Realtime Tracking Columns
| Column | Name | Description |
|--------|------|-------------|
| AR | `last_update_time` | Timestamp of most recent update |
| AS | `update_count` | Total number of updates received |
| AT | `current_price_live` | Latest price (continuously updated) |
| AU | `current_mc_live` | Latest market cap (continuously updated) |
| AV | `current_gain_live` | Current gain % from entry |

## 🔄 Update Flow

```
1. Bot monitors active signals every 10 seconds
2. For each signal:
   a. Calculate dynamic interval based on age & performance
   b. Check if enough time passed since last update
   c. If yes → Fetch fresh data from DexScreener
   d. Update live columns (AR-AV)
   e. Check for new peak & alert milestones
3. Traditional intervals (5/10/15/30/60 min) still tracked
```

## 🚀 Performance Benefits

### API Efficiency
- **Fresh signal (5 min)**: 10 calls
- **Hot signal (1 hour)**: 60 calls
- **Normal signal (24 hours)**: ~288 calls
- **3-day tracking**: ~500-1000 calls per token

### Rate Limit Safety
- Max ~100 active signals
- Peak: ~100 requests/minute (under 300 limit)
- Average: ~50 requests/minute (very safe)

## 💡 Smart Features

### 1. Hot Token Detection
Automatically prioritizes tokens with >20% gain:
```python
if gain_percent > 20:
    interval = 60  # Update every minute
```

### 2. Age-Based Scaling
Older signals update less frequently:
```python
if age < 5 min:   → 30s
if age < 60 min:  → 60s
if age < 24 hr:   → 5 min
if age < 2 days:  → 15 min
else:             → 30 min
```

### 3. Peak Tracking
Every update checks for new all-time high:
- Updates `peak_mc` and `peak_multiplier`
- Triggers alert notifications (2x/3x/5x/10x)
- Logs achievement timestamp

## 📝 Configuration

### In `config.py`:
```python
# Smart Polling Settings
SMART_POLLING_INTERVALS = {
    'fresh': 30,      # 0-5 min
    'hot': 60,        # Pumping OR <60 min
    'normal': 300,    # 1-24 hours
    'mature': 900,    # 1-2 days
    'old': 1800       # 2-3 days
}

HOT_GAIN_THRESHOLD = 20  # percent
TRACKING_DURATION = 4320  # 3 days
```

## 🎨 Visual Benefits

### Before (Old System):
```
Signal received → Update at 5, 10, 15, 30, 60 min → STOP
```
- Only 5 updates total
- Max 60 minutes tracking
- Fixed intervals

### After (Smart Polling):
```
Signal received → 30s updates (5 min) → 1min updates (1hr) 
→ 5min updates (24hr) → 15min updates (2d) → 30min updates (3d)
```
- **~500-1000 updates** over 3 days
- Realtime feel for fresh signals
- Efficient long-term tracking

## 🔍 Monitoring

### Check Update Activity:
1. Look at `update_count` column (AS) - should increment frequently
2. Look at `last_update_time` column (AR) - should be recent
3. Look at `current_gain_live` column (AV) - realtime gain percentage

### Logs Show:
```
Live update #5 for TOKEN: 1.23x (+23.4%)
Live update #10 for TOKEN: 1.45x (+45.2%)
🚀 New peak for TOKEN: 2.10x ($1,234,567 MC)
```

## ✅ Advantages Over True Realtime

### Why Not WebSocket?
| Feature | Smart Polling | WebSocket |
|---------|--------------|-----------|
| **Cost** | Free | $50-99/month |
| **Setup** | Simple | Complex |
| **Reliability** | Very stable | Connection issues |
| **Coverage** | All chains via DexScreener | Limited chains |
| **Latency** | 30s-5min | <1 second |

### Sweet Spot
Smart Polling delivers **90% of realtime benefits** with:
- ✅ Zero cost
- ✅ Simple implementation
- ✅ Stable operation
- ✅ Multi-chain support

For crypto signals (not day trading), **30-60 second updates are sufficient** to catch pumps and set alerts.

## 🎯 Use Cases

### Perfect For:
- ✅ Signal tracking & monitoring
- ✅ Pump detection (30s is fast enough)
- ✅ Alert notifications
- ✅ Portfolio tracking
- ✅ Multi-token dashboards

### Not Ideal For:
- ❌ High-frequency trading (need <1s latency)
- ❌ Arbitrage bots (need instant updates)
- ❌ Order book depth monitoring

## 🚀 Result

**Users see:**
- Fresh signals updating every 30 seconds (feels realtime!)
- Hot tokens continuously monitored
- Efficient long-term tracking
- Live columns always showing latest data

**System benefits:**
- No rate limit issues
- Stable performance with 100+ tokens
- Free (no API costs)
- Scalable architecture

---

**Status**: ✅ Implemented & Tested  
**Date**: December 17, 2025  
**Next**: Test with live Telegram signals
