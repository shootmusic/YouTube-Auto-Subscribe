# account_factory_stealth.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import json
import os
import string
from datetime import datetime
from fake_useragent import UserAgent

# Config
class Config:
    ACCOUNTS_DB = 'accounts.json'
    TARGET_AKUN_PER_HARI = 100

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
        # UserAgent dengan fallback aman untuk GitHub Actions
        try:
            self.ua = UserAgent()
            self.ua.random  # Test fetch
        except:
            self.ua = None
            print("⚠️ Using fallback user agent")
        
        self.success = 0
        self.failed = 0
        try:
            self.notifier = TelegramNotifier()
        except:
            self.notifier = None
        
    def generate_fingerprint(self):
        platforms = [
            ('Win32', 'Windows NT 10.0; Win64; x64'),
            ('Win32', 'Windows NT 11.0; Win64; x64'), 
            ('MacIntel', 'Macintosh; Intel Mac OS X 10_15_7'),
            ('Linux x86_64', 'X11; Linux x86_64')
        ]
        
        platform_js, platform_ua = random.choice(platforms)
        
        resolutions = [
            (1920, 1080), (1366, 768), (1440, 900), (1536, 864),
            (2560, 1440), (1280, 720), (1680, 1050)
        ]
        width, height = random.choice(resolutions)
        
        timezones = [
            'America/New_York', 'America/Los_Angeles', 'America/Chicago',
            'Europe/London', 'Europe/Paris', 'Europe/Berlin',
            'Asia/Tokyo', 'Asia/Singapore', 'Asia/Jakarta'
        ]
        
        languages = [
            'en-US,en;q=0.9', 'en-GB,en;q=0.9', 'en-CA,en;q=0.9',
            'id-ID,id;q=0.9,en;q=0.8'
        ]
        
        # Fallback user agents jika fake-useragent gagal
        fallback_uas = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
        ]
        
        if self.ua:
            try:
                user_agent = self.ua.random
            except:
                user_agent = random.choice(fallback_uas)
        else:
            user_agent = random.choice(fallback_uas)
        
        fingerprint = {
            'platform': platform_js,
            'platform_ua': platform_ua,
            'resolution': (width, height),
            'timezone': random.choice(timezones),
            'language': random.choice(languages),
            'cores': random.choice([4, 6, 8]),
            'memory': random.choice([8, 16]),
            'user_agent': user_agent
        }
        
        return fingerprint

    def create_driver(self):
        fp = self.generate_fingerprint()
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(f'--user-agent={fp["user_agent"]}')
        
        # GitHub Actions sudah install Chrome, webdriver-manager akan auto download driver yang cocok
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        """)
        
        return driver, fp

    def generate_account(self):
        # Nama panggilan (nama pertama)
        first_names = ['Alex', 'Jordan', 'Casey', 'Morgan', 'Riley', 'Avery', 'Quinn', 'Skyler', 'Dakota', 'Reese',
                      'John', 'James', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas',
                      'George', 'Charles', 'Kenneth', 'Steven', 'Edward', 'Brian', 'Ronald', 'Anthony', 'Kevin']
        
        # Nama panjang (opsional, jadi gak wajib)
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Wilson',
                     'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee']
        
        first = random.choice(first_names)
        last = random.choice(last_names)
        
        # Username patterns untuk Gmail
        patterns = [
            f"{first.lower()}.{last.lower()}{random.randint(10,999)}",
            f"{first[0].lower()}{last.lower()}{random.randint(100,9999)}",
            f"{first.lower()}{last[0].lower()}{random.randint(100,9999)}",
            f"{first.lower()}{random.randint(1000,9999)}"
        ]
        
        username = random.choice(patterns)
        
        # Password yang kuat
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choice(chars) for _ in range(random.randint(12, 16)))
        
        # Random birthday (18-45 years old)
        from datetime import date, timedelta
        max_age = date.today() - timedelta(days=365*18)
        min_age = date.today() - timedelta(days=365*45)
        random_date = min_age + timedelta(days=random.randint(0, (max_age-min_age).days))
        
        # Gender sesuai nama (kalo nama keliatan cowo/cewe)
        gender = 'Male'
        if first in ['Alex', 'Jordan', 'Casey', 'Morgan', 'Riley', 'Avery', 'Quinn', 'Skyler', 'Dakota', 'Reese']:
            gender = random.choice(['Male', 'Female'])
        elif first in ['John', 'James', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'George', 'Charles', 'Kenneth', 'Steven', 'Edward', 'Brian', 'Ronald', 'Anthony', 'Kevin']:
            gender = 'Male'
        else:
            gender = 'Female'
        
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
            'gender': gender
        }

    def smart_fill(self, driver, selectors, value):
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
                
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                time.sleep(random.uniform(0.3, 0.8))
                
                elem.click()
                time.sleep(0.1)
                elem.clear()
                time.sleep(0.1)
                
                for char in value:
                    elem.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
                    
                return True
                
            except Exception:
                continue
                
        return False

    def create_account(self):
        driver = None
        
        try:
            info = self.generate_account()
            print(f"\n🔥 Creating: {info['email']}")
            
            driver, _ = self.create_driver()
            driver.get("https://accounts.google.com/signup")
            time.sleep(5)
            
            # ========== STEP 1: PILIH UNTUK SIAPA (skip, pilih default "For myself") ==========
            try:
                for_myself = driver.find_elements(By.XPATH, "//div[contains(text(), 'For myself')]")
                if for_myself:
                    for_myself[0].click()
                    print("✅ Selected 'For myself'")
                    time.sleep(1)
                    
                    next_btn = driver.find_element(By.XPATH, "//span[text()='Next']")
                    next_btn.click()
                    print("✅ Clicked Next after selection")
                    time.sleep(3)
            except:
                print("ℹ️ No 'For myself' page detected")
            
            # ========== STEP 2: NAMA DEPAN & NAMA PANJANG (OPSIONAL) ==========
            # First name
            first_name_selectors = [
                ('xpath', "//input[@aria-label='First name']"),
                ('xpath', "//input[@name='firstName']"),
                ('xpath', "//input[@id='firstName']"),
            ]
            self.smart_fill(driver, first_name_selectors, info['first'])
            time.sleep(1)
            
            # Last name (optional, bisa dikosongin)
            last_name_selectors = [
                ('xpath', "//input[@aria-label='Last name']"),
                ('xpath', "//input[@name='lastName']"),
                ('xpath', "//input[@id='lastName']"),
            ]
            self.smart_fill(driver, last_name_selectors, info['last'])
            time.sleep(1)
            
            # Click Next
            try:
                next_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))
                )
                next_btn.click()
                print("✅ Clicked Next after name")
                time.sleep(4)
            except:
                print("❌ Next button not found")
                return False
            
            # ========== STEP 3: BIRTHDAY & GENDER ==========
            # Month
            try:
                month_select = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//select[@aria-label='Month']"))
                )
                Select(month_select).select_by_value(str(info['birthday']['month']))
                print(f"✅ Month selected: {info['birthday']['month']}")
                time.sleep(0.3)
            except:
                pass
            
            # Day
            day_selectors = [('xpath', "//input[@aria-label='Day']")]
            self.smart_fill(driver, day_selectors, str(info['birthday']['day']))
            time.sleep(0.3)
            
            # Year
            year_selectors = [('xpath', "//input[@aria-label='Year']")]
            self.smart_fill(driver, year_selectors, str(info['birthday']['year']))
            time.sleep(0.3)
            
            # Gender
            try:
                gender_select = driver.find_element(By.XPATH, "//select[@aria-label='Gender']")
                Select(gender_select).select_by_value('1' if info['gender'] == 'Male' else '2')
                print(f"✅ Gender selected: {info['gender']}")
                time.sleep(0.3)
            except:
                pass
            
            # Click Next
            try:
                next_btn = driver.find_element(By.XPATH, "//span[text()='Next']")
                next_btn.click()
                print("✅ Clicked Next after birthday/gender")
                time.sleep(4)
            except:
                print("❌ Next button not found after birthday")
                return False
            
            # ========== STEP 4: CREATE EMAIL ADDRESS (USERNAME) ==========
            print("🔍 Looking for email address page...")
            time.sleep(3)
            
            # Deteksi halaman "Create an email address"
            email_page_indicators = [
                "//div[contains(text(), 'Create an email address')]",
                "//div[contains(text(), 'Gmail address')]",
                "//div[contains(text(), 'Create your own Gmail address')]"
            ]
            
            is_email_page = False
            for indicator in email_page_indicators:
                if driver.find_elements(By.XPATH, indicator):
                    is_email_page = True
                    break
            
            if is_email_page:
                print("🔍 Detected: Create email address page")
                
                # Cek apakah ada pilihan rekomendasi dari Google
                recommended_emails = driver.find_elements(By.XPATH, "//div[contains(text(), '@gmail.com')]")
                
                if recommended_emails:
                    # Pake rekomendasi pertama dari Google
                    info['email'] = recommended_emails[0].text.strip()
                    info['username'] = info['email'].split('@')[0]
                    print(f"📧 Using recommended email: {info['email']}")
                    
                    # Klik pilihan pertama
                    try:
                        recommended_emails[0].click()
                        print("✅ Clicked recommended email")
                        time.sleep(1)
                    except:
                        pass
                else:
                    # Coba cari input manual
                    username_input = driver.find_elements(By.XPATH, "//input[@name='Username']|//input[@id='username']")
                    if username_input:
                        print("📝 Manual username input detected")
                        username_input[0].send_keys(info['username'])
                        print(f"✅ Username entered: {info['username']}")
                        time.sleep(1)
                    
                    # Cari tombol "Create your own"
                    try:
                        own_btn = driver.find_element(By.XPATH, "//span[contains(text(), 'Create your own')]")
                        own_btn.click()
                        print("✅ Clicked 'Create your own'")
                        time.sleep(2)
                        
                        username_input = driver.find_element(By.XPATH, "//input[@name='Username']")
                        username_input.send_keys(info['username'])
                        print(f"✅ Username entered: {info['username']}")
                        time.sleep(1)
                    except:
                        pass
                
                # Click Next
                try:
                    next_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))
                    )
                    next_btn.click()
                    print("✅ Clicked Next after email address")
                    time.sleep(4)
                except:
                    print("❌ Next button not found on email page")
                    return False
            else:
                print("⚠️ No email page detected, proceeding to password...")
            
            # ========== STEP 5: CREATE PASSWORD & CONFIRM ==========
            time.sleep(2)
            print("🔍 Looking for password field...")
            
            # Password field selectors
            password_selectors = [
                ('xpath', "//input[@type='password']"),
                ('xpath', "//input[@name='Passwd']"),
                ('xpath', "//input[@aria-label='Create a strong password']"),
                ('xpath', "//input[@aria-label='Create a password']"),
                ('xpath', "//input[@aria-label='Password']"),
                ('xpath', "//input[@placeholder='password']"),
                ('xpath', "//input[@placeholder='Enter password']"),
                ('css', "input[type='password']"),
            ]
            
            if not self.smart_fill(driver, password_selectors, info['password']):
                print("❌ Password field not found")
                return False
            print("✅ Password entered")
            time.sleep(0.5)
            
            # Confirm password field selectors
            confirm_selectors = [
                ('xpath', "(//input[@type='password'])[2]"),
                ('xpath', "//input[@name='ConfirmPasswd']"),
                ('xpath', "//input[@aria-label='Confirm']"),
                ('xpath', "//input[@aria-label='Confirm password']"),
                ('xpath', "//input[@placeholder='confirm']"),
                ('xpath', "//input[@placeholder='Confirm password']"),
            ]
            
            if not self.smart_fill(driver, confirm_selectors, info['password']):
                print("❌ Confirm password field not found")
                return False
            print("✅ Confirm password entered")
            time.sleep(1)
            
            # Click Next after password
            try:
                next_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))
                )
                next_btn.click()
                print("✅ Clicked Next after password")
                time.sleep(4)
            except:
                print("ℹ️ No Next button after password")
            
            # ========== STEP 6: SKIP PHONE VERIFICATION ==========
            try:
                skip_btn = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Skip']"))
                )
                skip_btn.click()
                print("✅ Skipped phone verification")
                time.sleep(2)
            except:
                pass
            
            # ========== STEP 7: I AGREE (TERMS) ==========
            try:
                agree_btn = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='I agree']"))
                )
                agree_btn.click()
                print("✅ Clicked I agree")
                time.sleep(3)
            except:
                pass
            
            # ========== STEP 8: CHECK SUCCESS ==========
            time.sleep(5)
            current_url = driver.current_url.lower()
            
            success_indicators = ['myaccount.google.com', 'accounts.google.com/signin', 'account']
            
            if any(indicator in current_url for indicator in success_indicators):
                self.save_account(info)
                self.success += 1
                print(f"✅✅✅ SUCCESS: {info['email']}")
                return True
            else:
                print(f"❌ Failed - URL: {current_url[:100]}...")
                driver.save_screenshot('error_final.png')
                self.failed += 1
                return False
            
        except Exception as e:
            print(f"❌ Error: {str(e)[:200]}")
            if driver:
                driver.save_screenshot('error_exception.png')
            self.failed += 1
            return False
        finally:
            if driver:
                driver.quit()

    def save_account(self, info):
        accounts = []
        if os.path.exists(config.ACCOUNTS_DB):
            with open(config.ACCOUNTS_DB, 'r') as f:
                accounts = json.load(f)
        
        accounts.append({
            'email': info['email'],
            'password': info['password'],
            'first': info['first'],
            'last': info['last'],
            'username': info['username'],
            'gender': info['gender'],
            'birthday': info['birthday'],
            'created_at': datetime.now().isoformat()
        })
        
        with open(config.ACCOUNTS_DB, 'w') as f:
            json.dump(accounts, f, indent=2)
        
        with open('accounts.csv', 'a') as f:
            f.write(f"{info['email']},{info['password']},{info['first']},{info['last']}\n")
        
        print(f"💾 Account saved to database")

    def run(self, count=100):
        print(f"\n🔥 STEALTH MODE: Creating {count} accounts")
        print("=" * 60)
        
        for i in range(count):
            print(f"\n📌 Progress: {i+1}/{count} | ✅ {self.success} | ❌ {self.failed}")
            self.create_account()
            
            if i < count - 1:
                delay = random.uniform(30, 60)
                print(f"⏰ Sleeping {delay:.0f}s...")
                time.sleep(delay)
        
        print(f"\n{'='*60}")
        print(f"🏁 FINISHED! ✅ Success: {self.success} | ❌ Failed: {self.failed}")

if __name__ == "__main__":
    factory = StealthAccountFactory()
    factory.run(count=getattr(config, 'TARGET_AKUN_PER_HARI', 100))
