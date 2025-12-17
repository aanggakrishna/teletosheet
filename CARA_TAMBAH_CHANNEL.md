# 📖 Cara Menambah Channel Baru

## ✅ Metode Mudah: Via .env File (RECOMMENDED)

**Tidak perlu edit kode Python!** Cukup edit file `.env` saja.

### Langkah-langkah:

#### 1️⃣ Dapatkan Channel ID
```bash
# Forward 1 pesan dari channel ke @userinfobot di Telegram
# Bot akan memberikan info channel termasuk ID-nya
# Contoh ID: -1002031885122
```

#### 2️⃣ Edit File .env
```bash
nano .env  # atau text editor favorit Anda
```

#### 3️⃣ Tambahkan Channel ID
```env
# Tambahkan di CHANNEL_IDS (pisahkan dengan koma, tanpa spasi)
CHANNEL_IDS=-1002031885122,-1002026135487,-1001234567890,-1009999999999

# Tambahkan mapping format di CHANNEL_FORMATS
CHANNEL_FORMATS=-1002031885122:ca_only,-1002026135487:narrative_ca,-1001234567890:standard,-1009999999999:ca_only
```

#### 4️⃣ Restart Bot
```bash
# Stop bot (Ctrl+C)
# Lalu jalankan lagi:
source venv/bin/activate && python main.py
```

### ✨ Selesai! Bot sudah monitor channel baru

---

## 📝 Format Types yang Tersedia

| Format Type | Kapan Dipakai | Auto-Fetch API |
|-------------|---------------|----------------|
| `ca_only` | Channel hanya kirim CA (contract address) | ✅ Ya - Fetch semua data |
| `narrative_ca` | Channel kirim narasi + CA | ✅ Ya - Fetch data teknis |
| `standard` | Format labeled (Chain:, Price:, MC:, dll) | ❌ Parse dari text |
| `compact` | Format dengan simbol (💎 TOKEN \| SOL) | ❌ Parse dari text |
| `simple` | Format minimal (🚀 TOKEN, Solana, $100K) | ❌ Parse dari text |
| `detailed` | Format lengkap (holders, FDV, locked liq) | ❌ Parse dari text |
| `list` | Format bullet points (• Chain: ...) | ❌ Parse dari text |

### 🤖 Auto-Fetch Formats

**`ca_only`** - Untuk channel yang hanya mengirim Contract Address
```
Contoh pesan:
73toJFpdDpRQiXihBJYL5XK7TxqAiMh9Vg2yuZ1Xpump

Atau:
beli ini ya 73toJFpdDpRQiXihBJYL5XK7TxqAiMh9Vg2yuZ1Xpump
```
Bot akan otomatis fetch: token name, chain, price, MC, liquidity, volume dari DexScreener API

**`narrative_ca`** - Untuk channel yang kirim narasi/analisis + CA
```
Contoh pesan:
New gem found! This token has great potential.
Strong community and upcoming partnerships.

CA: 73toJFpdDpRQiXihBJYL5XK7TxqAiMh9Vg2yuZ1Xpump
```
Bot akan fetch data teknis dari API, tapi coba extract token name dari text

---

## 🔧 Default Format

Jika channel tidak ada di mapping, bot akan gunakan format default:

```env
DEFAULT_CHANNEL_FORMAT=standard
```

Bisa diganti ke format lain (ca_only, simple, dll) sesuai kebutuhan

---

## 📋 Contoh Lengkap .env

```env
# Channel IDs to monitor
CHANNEL_IDS=-1002031885122,-1002026135487,-1001234567890,-1009876543210

# Format mapping
CHANNEL_FORMATS=-1002031885122:ca_only,-1002026135487:narrative_ca,-1001234567890:standard,-1009876543210:ca_only

# Default format for unmapped channels
DEFAULT_CHANNEL_FORMAT=standard
```

**Penjelasan:**
- Channel `-1002031885122` → `ca_only` (hanya CA, auto-fetch semua)
- Channel `-1002026135487` → `narrative_ca` (narasi + CA, auto-fetch teknis)
- Channel `-1001234567890` → `standard` (format labeled, parse dari text)
- Channel `-1009876543210` → `ca_only` (hanya CA, auto-fetch semua)
- Channel lain yang belum dimapping → `standard` (default)

---

## ❓ FAQ

### Q: Berapa channel maksimal yang bisa dimonitor?
A: Tidak ada batasan, tapi recommended max 20-30 channel untuk performa optimal

### Q: Bagaimana kalau format channel berubah?
A: Cukup update format di `.env` lalu restart bot. Tidak perlu edit kode!

### Q: Bisa campuran format standard dan ca_only?
A: Bisa! Setiap channel punya format sendiri. Bot akan handle otomatis.

### Q: Kalau channel kirim CA tanpa label "CA:", bisa?
A: Bisa! Format `ca_only` akan detect CA dimana saja dalam pesan (32-44 karakter alphanumeric)

### Q: Auto-fetch bisa error?
A: Jarang, tapi bisa kalau:
  - Token baru banget, belum ada di DexScreener (tunggu 1-2 menit)
  - CA salah/typo
  - API DexScreener down
  Bot akan log error dan skip signal tersebut.

### Q: Cara cek format apa yang dipakai channel saya?
A: Lihat log saat bot menerima pesan:
```
✅ Signal parsed successfully
   Channel ID: -1002031885122
   Format: ca_only
   Auto-fetch: True
```

---

## 🚀 Tips

1. **Gunakan `ca_only` untuk channel minimalis** - Bot akan fetch semua data otomatis
2. **Gunakan `narrative_ca` untuk channel analisis** - Bot extract insight + fetch data teknis
3. **Set default ke `ca_only`** jika kebanyakan channel Anda kirim CA saja
4. **Restart bot setelah update .env** - Perubahan baru apply setelah restart
5. **Monitor log** untuk pastikan format terdeteksi dengan benar

---

**✅ Selesai! Sekarang Anda bisa tambah/hapus channel kapan saja tanpa perlu coding!**
