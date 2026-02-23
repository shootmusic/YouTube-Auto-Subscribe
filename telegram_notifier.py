# telegram_notifier.py
import requests
import json
from datetime import datetime
import config

class TelegramNotifier:
    def __init__(self):
        self.token = config.TELEGRAM_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}"
    
    def send_message(self, text, parse_mode='HTML'):
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            response = requests.post(url, data=data, timeout=10)
            return response.json()
        except Exception as e:
            print(f"❌ Gagal kirim Telegram: {e}")
            return None
    
    def notify_start(self, task_name):
        msg = f"🚀 <b>MR.X BOT - {task_name}</b>\n"
        msg += f"⏰ Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        msg += f"🎯 Target: {config.CHANNEL_NAME}"
        self.send_message(msg)
    
    def notify_account_creation(self, stats):
        msg = f"📧 <b>PRODUKSI AKUN SELESAI</b>\n"
        msg += f"✅ Berhasil: {stats['success']} akun\n"
        msg += f"❌ Gagal: {stats['failed']}\n"
        msg += f"📊 Total akun tersedia: {stats['total']}\n"
        msg += f"⏱️ Durasi: {stats['duration']:.1f} menit"
        self.send_message(msg)
    
    def notify_subscribe_result(self, stats):
        msg = f"✅ <b>SUBSCRIBE CAMPAIGN SELESAI</b>\n"
        msg += f"📈 <b>Hasil untuk {config.CHANNEL_NAME}</b>\n"
        msg += f"━━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"👍 Berhasil subscribe: {stats['success']}\n"
        msg += f"👎 Gagal: {stats['failed']}\n"
        msg += f"📊 Rate: {stats['rate']:.1f}%\n"
        msg += f"⏱️ Durasi: {stats['duration']:.1f} menit\n"
        msg += f"━━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"🎯 <b>Total subscriber sekarang: ~{stats['total_subs']}</b>"
        self.send_message(msg)
    
    def notify_daily_report(self, report):
        msg = f"📋 <b>LAPORAN HARIAN MR.X</b>\n"
        msg += f"📅 Tanggal: {report['date']}\n"
        msg += f"━━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"📧 Akun dibuat: {report['accounts_created']}\n"
        msg += f"✅ Subscribe berhasil: {report['subscribes_success']}\n"
        msg += f"📊 Subscriber bertambah: +{report['subscribes_success']}\n"
        msg += f"🎯 Channel: {config.CHANNEL_NAME}\n"
        msg += f"━━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"🔥 Total akun aktif: {report['total_accounts']}\n"
        msg += f"💪 Estimasi subscriber: ~{report['estimated_subs']}"
        self.send_message(msg)
    
    def notify_error(self, error_msg):
        msg = f"🚨 <b>ERROR DETECTED</b>\n"
        msg += f"⏰ {datetime.now().strftime('%H:%M:%S')}\n"
        msg += f"━━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"<code>{error_msg[:200]}</code>"
        self.send_message(msg)
