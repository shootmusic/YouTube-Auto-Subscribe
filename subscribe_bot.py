# subscribe_bot.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import json
import os
from datetime import datetime
import config
from telegram_notifier import TelegramNotifier

class YouTubeSubscribeBot:
    def __init__(self):
        self.notifier = TelegramNotifier()
        self.target = config.TARGET_CHANNEL
        self.success = 0
        self.failed = 0
        self.start_time = None
        
    def load_accounts(self):
        if os.path.exists(config.ACCOUNTS_DB):
            with open(config.ACCOUNTS_DB, 'r') as f:
                return json.load(f)
        return []
    
    def create_driver(self):
        # Path untuk Termux
        chromedriver_path = '/data/data/com.termux/files/usr/bin/chromedriver'
        chrome_binary = '/data/data/com.termux/files/usr/lib/chromium/chrome'
        
        service = Service(chromedriver_path)
        options = Options()
        options.binary_location = chrome_binary
        
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(service=service, options=options)
        
        # Stealth script
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def subscribe_with_account(self, account):
        email = account['email']
        print(f"\n👤 Proses: {email}")
        
        driver = self.create_driver()
        
        try:
            # Login
            driver.get("https://accounts.google.com/Login")
            time.sleep(3)
            
            email_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='email']"))
            )
            email_input.send_keys(email)
            driver.find_element(By.XPATH, "//span[text()='Next']").click()
            time.sleep(3)
            
            pass_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
            )
            pass_input.send_keys(account['password'])
            driver.find_element(By.XPATH, "//span[text()='Next']").click()
            time.sleep(5)
            
            # Buka YouTube
            driver.get("https://youtube.com")
            time.sleep(3)
            
            # Buka channel target
            driver.get(self.target)
            time.sleep(5)
            
            driver.execute_script("window.scrollBy(0, 300)")
            time.sleep(2)
            
            # Subscribe
            subscribe_btn = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, 
                    "//button[contains(@aria-label, 'Subscribe')]"))
            )
            
            btn_text = subscribe_btn.text.lower()
            
            if 'subscribe' in btn_text and 'subscribed' not in btn_text:
                driver.execute_script("arguments[0].click();", subscribe_btn)
                print(f"✅ SUBSCRIBE BERHASIL: {email}")
                self.success += 1
            else:
                print(f"ℹ️ Udah subscribe: {email}")
                self.success += 1
            
            time.sleep(random.uniform(2, 5))
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.failed += 1
            return False
        finally:
            driver.quit()
    
    def run(self, max_accounts=100):
        self.start_time = time.time()
        self.success = 0
        self.failed = 0
        
        accounts = self.load_accounts()
        accounts_to_use = accounts[-max_accounts:] if accounts else []
        
        print(f"\n🎯 MULAI SUBSCRIBE KE: {config.CHANNEL_NAME}")
        print(f"📊 Total akun: {len(accounts_to_use)}")
        
        self.notifier.notify_start(f"Subscribe ke {config.CHANNEL_NAME}")
        
        for idx, account in enumerate(accounts_to_use):
            print(f"\n📌 Akun {idx+1}/{len(accounts_to_use)}")
            self.subscribe_with_account(account)
            
            if idx < len(accounts_to_use) - 1:
                delay = random.uniform(10, 20)
                print(f"⏰ Delay {delay:.0f} detik...")
                time.sleep(delay)
        
        duration = (time.time() - self.start_time) / 60
        rate = (self.success / (self.success + self.failed)) * 100 if (self.success + self.failed) > 0 else 0
        total_subs = 2 + self.success
        
        stats = {
            'success': self.success,
            'failed': self.failed,
            'rate': rate,
            'duration': duration,
            'total_subs': total_subs
        }
        
        self.notifier.notify_subscribe_result(stats)
        return stats

if __name__ == "__main__":
    bot = YouTubeSubscribeBot()
    bot.run(max_accounts=config.TARGET_SUBSCRIBE_PER_HARI)
