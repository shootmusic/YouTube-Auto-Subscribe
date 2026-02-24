# account_factory_stealth.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import json
import os
import string
import re
import subprocess
import platform
from datetime import datetime
from fake_useragent import UserAgent

# Config fallback
class Config:
    ACCOUNTS_DB = 'accounts.json'
    TARGET_AKUN_PER_HARI = 5

try:
    import config
except ImportError:
    config = Config()

try:
    from telegram_notifier import TelegramNotifier
except ImportError:
    class TelegramNotifier:
        def notify_account_creation(self, stats):
            print(f"[NOTIFY] Stats: {stats}")

class StealthAccountFactory:
    def __init__(self):
        self.ua = UserAgent(fallback='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        self.success = 0
        self.failed = 0
        try:
            self.notifier = TelegramNotifier()
        except:
            self.notifier = None
        
    def generate_fingerprint(self):
        """Generate unique browser fingerprint"""
        platforms = [
            ('Win32', 'Windows NT 10.0; Win64; x64'),
            ('Win32', 'Windows NT 11.0; Win64; x64'), 
            ('MacIntel', 'Macintosh; Intel Mac OS X 10_15_7'),
            ('Linux x86_64', 'X11; Linux x86_64')
        ]
        
        platform_js, platform_ua = random.choice(platforms)
        
        # Random screen resolutions
        resolutions = [
            (1920, 1080), (1366, 768), (1440, 900), (1536, 864),
            (2560, 1440), (1280, 720), (1680, 1050)
        ]
        width, height = random.choice(resolutions)
        
        # Random timezone
        timezones = [
            'America/New_York', 'America/Los_Angeles', 'America/Chicago',
            'Europe/London', 'Europe/Paris', 'Europe/Berlin',
            'Asia/Tokyo', 'Asia/Singapore', 'Asia/Jakarta'
        ]
        
        # Random languages
        languages = [
            'en-US,en;q=0.9', 'en-GB,en;q=0.9', 'en-CA,en;q=0.9',
            'id-ID,id;q=0.9,en;q=0.8'
        ]
        
        fingerprint = {
            'platform': platform_js,
            'platform_ua': platform_ua,
            'resolution': (width, height),
            'timezone': random.choice(timezones),
            'language': random.choice(languages),
            'cores': random.choice([4, 6, 8]),
            'memory': random.choice([8, 16]),
            'user_agent': self.ua.random
        }
        
        return fingerprint

    def create_stealth_driver(self):
        """Create Chrome instance dengan deteksi environment otomatis"""
        fp = self.generate_fingerprint()
        
        # === DETEKSI ENVIRONMENT ===
        is_termux = os.path.exists('/data/data/com.termux/files/usr')
        is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
        
        if is_termux:
            # Path untuk Termux (local debugging)
            chromedriver_path = '/data/data/com.termux/files/usr/bin/chromedriver'
            chrome_binary = '/data/data/com.termux/files/usr/lib/chromium/chrome'
            print("🔧 Environment: Termux")
        elif is_github_actions:
            # Path untuk GitHub Actions (Ubuntu)
            chromedriver_path = '/usr/local/bin/chromedriver'
            chrome_binary = '/usr/bin/chromium-browser'
            print("🔧 Environment: GitHub Actions")
        else:
            # Fallback: andai jalan di sistem lain
            chromedriver_path = 'chromedriver'
            chrome_binary = None
            print("🔧 Environment: Unknown (using PATH)")
        
        service = Service(chromedriver_path)
        options = Options()
        
        if chrome_binary:
            options.binary_location = chrome_binary
        
        # Headless mode - matikan untuk debug, nyalakan untuk production
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # Stealth args
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        options.add_argument(f'--user-agent={fp["user_agent"]}')
        
        # Create driver
        driver = webdriver.Chrome(service=service, options=options)
        
        # Stealth script
        driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
        
        return driver, fp

    def generate_account(self):
        """Generate random account data"""
        first_names = ['Alex', 'Jordan', 'Casey', 'Morgan', 'Riley', 'Avery', 'Quinn', 'Skyler', 'Dakota', 'Reese']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Wilson', 'Anderson']
        
        first = random.choice(first_names)
        last = random.choice(last_names)
        
        # Random username patterns
        patterns = [
            f"{first.lower()}.{last.lower()}{random.randint(10,999)}",
            f"{first[0].lower()}{last.lower()}{random.randint(100,9999)}",
            f"{first.lower()}{last[0].lower()}{random.randint(100,9999)}",
            f"{first.lower()}{random.randint(1000,9999)}"
        ]
        
        username = random.choice(patterns)
        
        # Password
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choice(chars) for _ in range(random.randint(12, 16)))
        
        # Random birthday
        from datetime import date, timedelta
        max_age = date.today() - timedelta(days=365*18)
        min_age = date.today() - timedelta(days=365*35)
        random_date = min_age + timedelta(days=random.randint(0, (max_age-min_age).days))
        
        return {
            'first': first,
            'last': last,
            'username': username,
            'email': f"{username}@gmail.com",
            'password': password,
            'birthday': {
                'year': random_date.year,
                'month': random_date.month,
                'day': random_date.day
            },
            'gender': random.choice(['Male', 'Female'])
        }

    def smart_fill(self, driver, selectors, value):
        """Fill field with human-like behavior"""
        for selector_type, selector in selectors:
            try:
                if selector_type == 'xpath':
                    elem = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                elif selector_type == 'css':
                    elem = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                
                # Scroll
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                time.sleep(random.uniform(0.3, 0.8))
                
                # Click & clear
                elem.click()
                time.sleep(0.1)
                elem.clear()
                time.sleep(0.1)
                
                # Type like human
                for char in value:
                    elem.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
                    
                return True
                
            except Exception as e:
                continue
                
        return False

    def create_account(self):
        """Create single Google account"""
        driver = None
        
        try:
            info = self.generate_account()
            print(f"\n🔥 Creating: {info['email']}")
            
            driver, _ = self.create_stealth_driver()
            
            # Buka signup
            driver.get("https://accounts.google.com/signup")
            time.sleep(random.uniform(5, 8))
            
            # === STEP 1: First name ===
            if not self.smart_fill(driver, [
                ('xpath', "//input[@aria-label='First name']"),
                ('xpath', "//input[@name='firstName']"),
                ('xpath', "//input[@id='firstName']"),
            ], info['first']):
                print("❌ First name not found")
                return False
            
            time.sleep(random.uniform(0.5, 1.5))
            
            # === STEP 2: Last name ===
            if not self.smart_fill(driver, [
                ('xpath', "//input[@aria-label='Last name']"),
                ('xpath', "//input[@name='lastName']"),
                ('xpath', "//input[@id='lastName']"),
            ], info['last']):
                print("❌ Last name not found")
                return False
            
            time.sleep(random.uniform(0.5, 1.5))
            
            # === STEP 3: Username/Email - SELECTOR BARU ===
            # Coba klik Next dulu (mungkin username di halaman berikutnya)
            try:
                next_btn = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))
                )
                next_btn.click()
                time.sleep(3)
            except:
                pass
            
            # Sekarang cari username
            if not self.smart_fill(driver, [
                ('xpath', "//input[@name='Username']"),
                ('xpath', "//input[@id='username']"),
                ('xpath', "//input[@type='email']"),
                ('xpath', "//input[@aria-label='Username']"),
            ], info['username']):
                print("❌ Username not found")
                # Screenshot buat debug
                driver.save_screenshot('username_error.png')
                print("📸 Screenshot: username_error.png")
                return False
            
            time.sleep(random.uniform(0.5, 1.5))
            
            # === STEP 4: Password ===
            if not self.smart_fill(driver, [
                ('xpath', "//input[@type='password']"),
                ('xpath', "//input[@name='Passwd']"),
                ('xpath', "//input[@aria-label='Password']"),
            ], info['password']):
                print("❌ Password field not found")
                return False
            
            time.sleep(random.uniform(0.3, 0.8))
            
            # === STEP 5: Confirm password ===
            if not self.smart_fill(driver, [
                ('xpath', "(//input[@type='password'])[2]"),
                ('xpath', "//input[@name='PasswdAgain']"),
                ('xpath', "//input[@aria-label='Confirm']"),
            ], info['password']):
                print("❌ Confirm password field not found")
                return False
            
            time.sleep(random.uniform(1, 2))
            
            # === STEP 6: Click Next ===
            try:
                next_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))
                )
                next_btn.click()
                time.sleep(random.uniform(4, 6))
            except:
                print("❌ Next button not found")
                return False
            
            # === STEP 7: Personal info ===
            # Month
            try:
                month_select = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//select[@aria-label='Month']"))
                )
                Select(month_select).select_by_value(str(info['birthday']['month']))
                time.sleep(random.uniform(0.3, 0.8))
            except:
                pass
            
            # Day
            self.smart_fill(driver, [
                ('xpath', "//input[@aria-label='Day']"),
            ], str(info['birthday']['day']))
            time.sleep(random.uniform(0.3, 0.8))
            
            # Year
            self.smart_fill(driver, [
                ('xpath', "//input[@aria-label='Year']"),
            ], str(info['birthday']['year']))
            time.sleep(random.uniform(0.3, 0.8))
            
            # Gender
            try:
                gender_select = driver.find_element(By.XPATH, "//select[@aria-label='Gender']")
                gender_map = {'Male': '1', 'Female': '2'}
                Select(gender_select).select_by_value(gender_map.get(info['gender'], '3'))
                time.sleep(random.uniform(0.3, 0.8))
            except:
                pass
            
            # Next
            try:
                next_btn = driver.find_element(By.XPATH, "//span[text()='Next']")
                next_btn.click()
                time.sleep(random.uniform(4, 6))
            except:
                pass
            
            # === CHECK SUCCESS ===
            time.sleep(5)
            
            success_signs = [
                'myaccount.google.com',
                'accounts.google.com/signin',
                'Welcome to Google',
                'Confirm your recovery email'
            ]
            
            current_url = driver.current_url.lower()
            
            if any(sign.lower() in current_url for sign in success_signs):
                self.save_account(info)
                self.success += 1
                print(f"✅ SUCCESS: {info['email']}")
                return True
            else:
                print(f"❌ Failed - URL: {current_url[:60]}...")
                driver.save_screenshot('error.png')
                print("📸 Screenshot saved: error.png")
                self.failed += 1
                return False
            
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")
            if driver:
                driver.save_screenshot(f'error_{int(time.time())}.png')
            self.failed += 1
            return False
            
        finally:
            if driver:
                driver.quit()

    def save_account(self, info):
        """Save account to JSON"""
        accounts = []
        if os.path.exists(config.ACCOUNTS_DB):
            try:
                with open(config.ACCOUNTS_DB, 'r') as f:
                    accounts = json.load(f)
            except:
                pass
        
        account_data = {
            'email': info['email'],
            'password': info['password'],
            'first': info['first'],
            'last': info['last'],
            'created_at': datetime.now().isoformat()
        }
        
        accounts.append(account_data)
        
        with open(config.ACCOUNTS_DB, 'w') as f:
            json.dump(accounts, f, indent=2)
        
        # Simple CSV
        with open('accounts.csv', 'a') as f:
            f.write(f"{info['email']},{info['password']},{info['first']},{info['last']}\n")
        
        # Kirim notifikasi kalo ada
        if self.notifier and self.success + self.failed > 0:
            try:
                stats = {'success': self.success, 'failed': self.failed, 'total': len(accounts)}
                self.notifier.notify_account_creation(stats)
            except:
                pass

    def run(self, count=5):
        print(f"\n🔥 STEALTH MODE: Creating {count} accounts")
        print("=" * 50)
        
        for i in range(count):
            print(f"\n📌 Progress: {i+1}/{count}")
            self.create_account()
            
            if i < count - 1:
                delay = random.uniform(30, 60)
                print(f"⏰ Sleeping {delay:.0f}s...")
                time.sleep(delay)
        
        print(f"\n{'='*50}")
        print(f"🏁 Done! Success: {self.success}, Failed: {self.failed}")
        
        # Final notif
        if self.notifier:
            try:
                accounts = []
                if os.path.exists(config.ACCOUNTS_DB):
                    with open(config.ACCOUNTS_DB, 'r') as f:
                        accounts = json.load(f)
                stats = {'success': self.success, 'failed': self.failed, 'total': len(accounts), 'duration': 0}
                self.notifier.notify_account_creation(stats)
            except:
                pass

if __name__ == "__main__":
    factory = StealthAccountFactory()
    factory.run(count=getattr(config, 'TARGET_AKUN_PER_HARI', 5))
