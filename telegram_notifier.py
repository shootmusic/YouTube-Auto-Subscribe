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
            print(f"Gagal kirim Telegram: {e}")
            return None
    
    def notify_start(self, task_name):
        msg = f"MR.X BOT - {task_name}\n"
        msg += f"Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        msg += f"Target: {config.CHANNEL_NAME}"
        self.send_message(msg)
    
    def notify_account_creation(self, stats):
        msg = f"Produksi 100 akun selesai\n"
        msg += f"✅ Berhasil: {stats['success']} akun 🍂\n"
        msg += f"❌ Gagal: {stats['failed']}\n"
        msg += f"Total akun: {stats['total']}"
        self.send_message(msg)
    
    def notify_subscribe_result(self, stats):
        msg = f"Subscribe campaign selesai\n"
        msg += f"✅ Berhasil subscribe: {stats['success']} 💐\n"
        msg += f"❌ Gagal: {stats['failed']}\n"
        msg += f"Rate: {stats['rate']:.1f}%\n"
        msg += f"Total subscriber: ~{stats['total_subs']}"
        self.send_message(msg)
    
    def notify_daily_report(self, report):
        msg = f"Laporan Harian\n"
        msg += f"📧 Akun dibuat: {report['accounts_created']} 🍂\n"
        msg += f"✅ Subscribe: {report['subscribes_success']} 💐\n"
        msg += f"Total akun: {report['total_accounts']}\n"
        msg += f"Estimasi subscriber: {report['estimated_subs']}"
        self.send_message(msg)
    
    def notify_error(self, error_msg):
        msg = f"ERROR DETECTED\n"
        msg += f"Waktu: {datetime.now().strftime('%H:%M:%S')}\n"
        msg += f"{error_msg[:200]}"
        self.send_message(msg)
