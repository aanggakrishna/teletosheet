# ⚡ Cara Cepat Tambah Channel

## 1. Dapatkan Channel ID
Forward pesan dari channel ke **@userinfobot** di Telegram

## 2. Edit .env
```bash
nano .env
```

Tambahkan di 2 tempat:
```env
CHANNEL_IDS=-1002031885122,-1009999999999
                            👆 tambah disini

CHANNEL_FORMATS=-1002031885122:ca_only,-1009999999999:ca_only
                                        👆 tambah disini
```

## 3. Restart Bot
```bash
source venv/bin/activate && python main.py
```

## Format Types
- `ca_only` → Hanya CA, fetch semua dari API ✅
- `narrative_ca` → Narasi + CA, fetch teknis dari API ✅
- `standard` → Parse dari text ❌
- `compact/simple/detailed/list` → Parse dari text ❌

**Recommended: Pakai `ca_only` untuk channel minimalis!**

✅ Selesai! Tidak perlu edit file Python!
