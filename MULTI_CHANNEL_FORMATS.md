# Multi-Channel Format Support

## 🎯 Fitur Baru: Support Multiple Channel Formats

Bot sekarang bisa handle **berbagai format signal** dari channel yang berbeda-beda!

## 📋 Format Yang Didukung

### 1. **Standard Format** (Default)
```
🚀 TOKEN NAME
Chain: Solana
Price: $0.00001
Market Cap: $100K
Liquidity: $50K
Volume 24h: $25K
Bundles: 5 (10%)
Snipers: 3 (5%)
Dev: 0%
Confidence: 85%
Contract: ABC123...XYZ789
```

### 2. **Compact Format**
```
💎 TOKEN NAME | SOL
💵 $0.00001 | MC: $100K | LIQ: $50K
📊 Vol: $25K | B: 10% | S: 5%
🔒 Dev: 0% | Score: 85%
📝 ABC123...XYZ789
```

### 3. **Simple Format**
```
🚀 TOKEN NAME
Solana
$100K MC
Contract: ABC123...XYZ789
```

### 4. **Detailed Format**
```
🔥 TOKEN NAME (SYMBOL)
⛓️ Chain: Solana
💰 Entry Price: $0.00001
📊 Market Cap: $100K (FDV: $120K)
💧 Liquidity: $50K (Locked: 80%)
📈 Volume 24h: $25K
🎯 Holders: 250
👥 Bundles: 5 (10%)
🎯 Snipers: 3 (5%)
👨‍💻 Dev Holdings: 0%
✅ Confidence Score: 85%
📝 Contract: ABC123...XYZ789
```

### 5. **List Format**
```
New Signal: TOKEN NAME
• Chain: Solana
• Price: $0.00001
• MC: $100K
• Liq: $50K
• Vol: $25K
• CA: ABC123...XYZ789
```

## 🔧 Cara Setup

### Step 1: Dapatkan Channel ID

Jalankan bot dan kirim message test ke channel. Bot akan log:
```
📩 New message from Channel Name (ID: -1001234567890)
```

Copy Channel ID-nya (angka yang diawali `-`)

### Step 2: Edit `channel_formats.py`

Buka file `channel_formats.py` dan tambahkan mapping:

```python
CHANNEL_FORMAT_MAPPING = {
    -1001234567890: 'standard',    # Channel 1 pakai format standard
    -1009876543210: 'compact',     # Channel 2 pakai format compact
    -1001111111111: 'simple',      # Channel 3 pakai format simple
    -1002222222222: 'detailed',    # Channel 4 pakai format detailed
    -1003333333333: 'list',        # Channel 5 pakai format list
}
```

### Step 3: Restart Bot

```bash
source venv/bin/activate
python main.py
```

Bot akan auto-detect format untuk setiap channel! 🎉

## 🎨 Buat Format Custom

Jika channel Anda punya format unik, tambahkan ke `CHANNEL_FORMATS`:

```python
CHANNEL_FORMATS = {
    # ... existing formats ...
    
    'your_custom_format': {
        'name': 'Your Custom Format',
        'example': '''
Your format example here
        ''',
        'patterns': {
            'token_name': r'your_regex_pattern_here',
            'chain': r'your_chain_pattern',
            'price': r'your_price_pattern',
            'market_cap': r'your_mc_pattern',
            'ca': r'your_ca_pattern',
            # Add more fields as needed
        }
    }
}
```

Kemudian mapping channel ID ke format custom:
```python
CHANNEL_FORMAT_MAPPING = {
    -1001234567890: 'your_custom_format',
}
```

## 📊 Field Yang Bisa Di-Parse

Bot akan extract fields ini (jika ada di format):

| Field | Description | Required |
|-------|-------------|----------|
| `token_name` | Nama token | ✅ Yes |
| `chain` | Blockchain (Solana, ETH, etc) | ⚠️ Recommended |
| `price` | Entry price | ⚠️ Recommended |
| `market_cap` | Market cap entry | ⚠️ Recommended |
| `liquidity` | Liquidity pool | Optional |
| `volume_24h` | 24h trading volume | Optional |
| `bundles` | Bundle percentage | Optional |
| `snipers` | Sniper percentage | Optional |
| `dev` | Dev holdings percentage | Optional |
| `confidence` | Confidence score | Optional |
| `ca` | Contract address | ✅ **Required** |

**Note**: Jika field tidak ada, bot akan:
- Set nilai 0 untuk numerik
- Auto-fetch dari DexScreener jika punya CA

## 🧪 Testing Format Baru

Test regex patterns Anda:

```python
import re

message = """
Your test message here
"""

# Test token name pattern
token_match = re.search(r'your_pattern', message, re.IGNORECASE)
if token_match:
    print(f"Token: {token_match.group(1)}")

# Test CA pattern
ca_match = re.search(r'your_ca_pattern', message, re.IGNORECASE)
if ca_match:
    print(f"CA: {ca_match.group(1)}")
```

## 🔍 Troubleshooting

### Format tidak terdetect?

Check logs:
```
Using format 'Standard Format' for channel Channel Name
```

Jika muncul format yang salah, periksa:
1. Channel ID di `CHANNEL_FORMAT_MAPPING` sudah benar?
2. Format key sudah ada di `CHANNEL_FORMATS`?

### Field tidak ter-extract?

1. Check log untuk warning:
   ```
   Parsed signal: TOKEN | CA: None...
   ```

2. Test regex pattern manual
3. Pastikan field name di patterns sesuai: `token_name`, `ca`, `price`, dll

### CA tidak valid?

Bot akan auto-validate CA length (32-44 chars). Jika invalid:
```
Invalid CA length for TOKEN: ABC
```

## 💡 Tips

1. **Start Simple**: Test dengan 1-2 channel dulu
2. **Use Existing Formats**: Cek apakah format yang ada sudah cocok
3. **Test Regex**: Gunakan regex101.com untuk test patterns
4. **Check Logs**: Bot akan log format yang digunakan per message
5. **Fallback Works**: Jika pattern gagal, bot akan coba extract basic info

## 📈 Example Multi-Channel Setup

```python
CHANNEL_FORMAT_MAPPING = {
    # Premium signals (detailed info)
    -1001111111111: 'detailed',
    -1002222222222: 'detailed',
    
    # Free signals (simple format)
    -1003333333333: 'simple',
    -1004444444444: 'simple',
    
    # Partner channels (compact)
    -1005555555555: 'compact',
    
    # Your own channel (custom format)
    -1006666666666: 'your_custom_format',
}
```

Bot akan handle semua channel secara otomatis dengan format yang sesuai! 🎯

---

**Status**: ✅ Implemented  
**Files**: `channel_formats.py`, `signal_parser.py`  
**Backward Compatible**: Yes (default ke 'standard' format)
