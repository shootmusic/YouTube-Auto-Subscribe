<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=200&section=header&text=YouTube%20Automaton&fontSize=50&fontAlignY=35&desc=Auto%20Subscriber%20Bot%20by%20Yang%20Mulia%20RICC&descAlignY=55" width="100%"/>
</div>

# YouTube Automaton - Auto Subscriber Bot

<p align="center">
  <b>Target:</b> <a href="https://www.youtube.com/@remass62">@remass62</a> • 
  <b>Goal:</b> +100 subscribers/day • 
  <b>Status:</b> Active
</p>

---

## Overview

YouTube Automaton adalah bot yang berjalan di GitHub Actions untuk meningkatkan subscriber channel @remass62 secara otomatis.

Fitur utama:
- Membuat 100 akun Google baru setiap jam 09:00 WIB
- Subscribe ke channel target menggunakan 100 akun setiap jam 11:00 WIB
- Laporan hasil ke Telegram pribadi

---

## Cara Kerja

09:00 WIB → Produksi 100 akun baru → Database akun  
11:00 WIB → Subscribe 100 akun ke @remass62 → Laporan Telegram

---

## Teknologi

- Python 3.10
- Selenium
- GitHub Actions
- Telegram Bot API

---

## Cara Deploy

1. Fork repository ini
2. Set secrets di Settings → Secrets and variables → Actions:
   - `TELEGRAM_TOKEN`: (isi dengan token bot Telegram Anda)
   - `TELEGRAM_CHAT_ID`: (isi dengan chat ID Anda)
3. Aktifkan GitHub Actions di tab Actions

---

## Jadwal

- 09:00 WIB: Produksi 100 akun
- 11:00 WIB: Subscribe ke @remass62

---

## Preview Laporan Telegram

```

Produksi 100 akun selesai
✅ Berhasil: 98 akun 🍂
❌ Gagal: 2
Total akun: 350

Subscribe campaign selesai
✅ Berhasil subscribe: 98 💐
❌ Gagal: 2
Rate: 98.0%
Total subscriber: ~100

Laporan Harian
📧 Akun dibuat: 98 🍂
✅ Subscribe: 98 💐
Total akun: 350
Estimasi subscriber: 300

```

---

Repository: https://github.com/shootmusic/YouTube-Auto-Subscribe
