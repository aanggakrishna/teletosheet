# Crypto Signal Tracker Bot

Bot Telegram untuk melacak sinyal crypto trading dan menyimpan data ke Google Sheets dengan tracking harga otomatis.

## Features

✅ **Monitoring Telegram Channels** - Memantau channel sinyal crypto secara real-time  
✅ **Auto Parse Signals** - Ekstrak data token (harga, market cap, dll) otomatis  
✅ **Price Tracking** - Melacak perubahan harga setiap 5, 10, 15, 30, 60 menit  
✅ **Google Sheets Integration** - Simpan semua data ke spreadsheet  
✅ **Alert System** - Notifikasi saat token mencapai 2x, 3x, 5x, 10x  
✅ **Smart Update** - Alert update di row yang sama menggunakan reply system
✅ **Update History** - Tracking lengkap semua alert dalam 1 row
✅ **Advanced Logging** - Log berwarna dengan level yang berbeda  
✅ **Heartbeat Monitoring** - Status bot secara berkala  
✅ **Error Handling** - Log error lengkap untuk debugging  

## Installation

1. Clone repository:
```bash
git clone <repo-url>
cd teletosheet
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup environment variables di file `.env`:
```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash  
TELEGRAM_PHONE=+your_phone
CHANNEL_IDS=-1001234567890,-1001234567891
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_SERVICE_ACCOUNT_JSON=service-account.json
LOG_LEVEL=INFO
ENABLE_DEBUG_LOGS=false
```

4. Setup Google Sheets:
   - Buat Google Sheets baru
   - Setup Service Account dan download JSON key
   - Rename file JSON ke `service-account.json`
   - Share sheet dengan email service account

## Usage

Jalankan bot:
```bash
python main.py
```

## Monitoring & Logs

### Log Files
- **Console**: Log berwarna real-time
- **File**: `logs/bot.log` untuk semua log level

### Heartbeat
- Heartbeat setiap 5 menit menunjukkan bot masih hidup
- Status report detail setiap jam
- Tracking jumlah signal aktif dan channel

### Log Levels
- **🚀 STARTUP**: Informasi saat bot mulai
- **✅ SUCCESS**: Operasi berhasil  
- **📥 SIGNAL**: Signal baru diterima
- **🚨 ALERT**: Alert multiplier triggered
- **🔄 TRACKING**: Update tracking data
- **💓 HEARTBEAT**: Bot status heartbeat
- **⚠️ WARNING**: Peringatan (non-fatal)
- **❌ ERROR**: Error dengan stack trace
- **🔍 DEBUG**: Detail debugging (jika enabled)

### Error Handling
- Semua error dicatat dengan stack trace lengkap
- Error disimpan ke kolom `error_log` di spreadsheet
- Bot akan lanjut berjalan meski ada error
- Auto retry pada API failures

## Project Structure

```
├── main.py              # Entry point utama
├── config.py            # Konfigurasi dan environment variables
├── logger.py            # Advanced logging system  
├── signal_parser.py     # Parse pesan signal dari Telegram
├── price_tracker.py     # Track perubahan harga token
├── sheets_handler.py    # Google Sheets operations
├── requirements.txt     # Dependencies
├── .env                 # Environment variables
├── service-account.json # Google service account key
└── logs/               # Log files
    └── bot.log         # Main log file
```

## Monitoring Bot Status

### Heartbeat Logs
```
💓 Heartbeat #12 - Monitoring 3 channels, tracking 5 signals
📊 Hourly Status Report:
   • Active signals: 5
   • Monitored channels: 3  
   • Bot uptime: 60 minutes
```

### Signal Processing
```
📥 New signal: PEPE from Crypto Signals Pro
🔄 Updated 5min: PEPE - 1.25x
🚨 Alert triggered: 2x PEPE
🚀 New peak for DOGE: 3.45x ($2,500,000)
⏹️ Stopped tracking: SHIB
```

### Error Examples
```
❌ Error handling message from Unknown: API timeout
🔌 DexScreener API error: HTTP 429
⚠️ Failed to parse signal from Crypto Channel
```

## Troubleshooting

### Common Issues

1. **Bot tidak menerima pesan**
   - Pastikan CHANNEL_IDS benar (gunakan ID negatif untuk channels)
   - Check bot sudah join channel yang dipantau

2. **Google Sheets error**
   - Pastikan service account punya akses ke sheet
   - Check GOOGLE_SHEET_ID benar
   - Verify service-account.json valid

3. **DexScreener API error**
   - Rate limit: tunggu beberapa menit
   - Check koneksi internet
   - Verify CA (Contract Address) valid

4. **Parsing error**
   - Format pesan channel mungkin berubah
   - Check regex pattern di signal_parser.py
   - Enable debug logs untuk detail

### Debug Mode

Enable debug logging di `.env`:
```env
ENABLE_DEBUG_LOGS=true
LOG_LEVEL=DEBUG
```

Ini akan menampilkan log detail untuk debugging.

## Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Create pull request

## License

MIT License