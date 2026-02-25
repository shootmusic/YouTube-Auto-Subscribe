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

    def create_driver(self):
        """Create Chrome instance dengan webdriver-manager (auto download)"""
        fp = self.generate_fingerprint()
        
        options = Options()
        
        # Opsi umum untuk GitHub Actions
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(f'--user-agent={fp["user_agent"]}')
        
        # Gunakan webdriver-manager untuk auto download driver
        service = Service(ChromeDriverManager().install())
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
        """Generate random account data dengan format yang lebih bervariasi"""
        first_names = [
            'Alex', 'Jordan', 'Casey', 'Morgan', 'Riley', 'Avery', 'Quinn', 'Skyler', 'Dakota', 'Reese',
            'John', 'James', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Charles',
            'Christopher', 'Daniel', 'Matthew', 'Anthony', 'Donald', 'Mark', 'Paul', 'Steven', 'Andrew', 'Kenneth',
            'Joshua', 'George', 'Kevin', 'Brian', 'Edward', 'Ronald', 'Timothy', 'Jason', 'Jeffrey', 'Ryan',
            'Jacob', 'Gary', 'Nicholas', 'Eric', 'Jonathan', 'Stephen', 'Larry', 'Justin', 'Scott', 'Brandon'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
            'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
            'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson',
            'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
            'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell', 'Carter', 'Roberts'
        ]
        
        first = random.choice(first_names)
        last = random.choice(last_names)
        
        # Random username patterns yang lebih bervariasi
        patterns = [
            f"{first.lower()}.{last.lower()}{random.randint(10,999)}",
            f"{first[0].lower()}{last.lower()}{random.randint(100,9999)}",
            f"{first.lower()}{last[0].lower()}{random.randint(100,9999)}",
            f"{first.lower()}{random.randint(1000,9999)}",
            f"{last.lower()}{random.randint(1000,9999)}",
            f"{first.lower()}_{last.lower()}{random.randint(10,99)}",
            f"{first[0].lower()}_{last.lower()}{random.randint(100,999)}",
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
        """Fill field dengan human-like behavior"""
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
                
                # Scroll ke elemen
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                time.sleep(random.uniform(0.3, 0.8))
                
                # Click dan clear
                elem.click()
                time.sleep(0.1)
                elem.clear()
                time.sleep(0.1)
                
                # Ketik seperti manusia
                for char in value:
                    elem.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
                    
                return True
                
            except Exception:
                continue
                
        return False

    def check_element_exists(self, driver, by, selector, timeout=3):
        """Cek apakah elemen ada di halaman"""
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return True
        except:
            return False

    def create_account(self):
        """Create single Google account dengan selector yang lebih lengkap"""
        driver = None
        
        try:
            info = self.generate_account()
            print(f"\n🔥 Creating: {info['email']}")
            
            driver, _ = self.create_driver()
            
            # Buka signup
            driver.get("https://accounts.google.com/signup")
            time.sleep(random.uniform(5, 8))
            
            # === STEP 1: First name ===
            first_name_selectors = [
                ('xpath', "//input[@aria-label='First name']"),
                ('xpath', "//input[@name='firstName']"),
                ('xpath', "//input[@id='firstName']"),
                ('xpath', "//input[@placeholder='First name']"),
                ('css', "input[autocomplete='given-name']"),
            ]
            
            if not self.smart_fill(driver, first_name_selectors, info['first']):
                print("❌ First name not found")
                return False
            time.sleep(random.uniform(0.5, 1.5))
            
            # === STEP 2: Last name ===
            last_name_selectors = [
                ('xpath', "//input[@aria-label='Last name']"),
                ('xpath', "//input[@name='lastName']"),
                ('xpath', "//input[@id='lastName']"),
                ('xpath', "//input[@placeholder='Last name']"),
                ('css', "input[autocomplete='family-name']"),
            ]
            
            if not self.smart_fill(driver, last_name_selectors, info['last']):
                print("❌ Last name not found")
                return False
            time.sleep(random.uniform(0.5, 1.5))
            
            # === STEP 3: Klik Next (pindah ke halaman username) ===
            try:
                next_btn_selectors = [
                    "//span[text()='Next']",
                    "//button[@type='button']//span[text()='Next']",
                    "//input[@type='submit' and @value='Next']",
                    "//button[contains(text(), 'Next')]"
                ]
                
                for selector in next_btn_selectors:
                    try:
                        next_btn = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        next_btn.click()
                        print("✅ Clicked Next button")
                        time.sleep(3)
                        break
                    except:
                        continue
            except:
                print("ℹ️ Maybe already on username page")
            
            # === STEP 4: Username (selector super lengkap) ===
            username_selectors = [
                ('xpath', "//input[@name='Username']"),
                ('xpath', "//input[@id='username']"),
                ('xpath', "//input[@type='email']"),
                ('xpath', "//input[@aria-label='Username']"),
                ('xpath', "//input[@aria-label='Email']"),
                ('xpath', "//input[@aria-label='Email address']"),
                ('xpath', "//input[@autocomplete='username']"),
                ('css', "input[autocomplete='username']"),
                ('xpath', "//input[@name='email']"),
                ('xpath', "//input[@id='Email']"),
                ('xpath', "//input[@id='emailAddress']"),
                ('css', "input[type='email']"),
            ]
            
            # Tunggu sebentar untuk memastikan halaman username muncul
            time.sleep(2)
            
            if not self.smart_fill(driver, username_selectors, info['username']):
                print("❌ Username not found - saving debug info")
                
                # Screenshot untuk debugging
                timestamp = int(time.time())
                screenshot_file = f"error_username_{timestamp}.png"
                html_file = f"page_source_{timestamp}.html"
                
                driver.save_screenshot(screenshot_file)
                print(f"📸 Screenshot saved: {screenshot_file}")
                
                with open(html_file, "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print(f"📄 HTML source saved: {html_file}")
                
                # Coba lihat judul halaman dan URL
                print(f"🔍 Page title: {driver.title}")
                print(f"🔍 Current URL: {driver.current_url}")
                
                return False
            
            print(f"✅ Username filled: {info['username']}")
            time.sleep(random.uniform(0.5, 1.5))
            
            # === STEP 5: Password ===
            password_selectors = [
                ('xpath', "//input[@type='password']"),
                ('xpath', "//input[@name='Passwd']"),
                ('xpath', "//input[@aria-label='Password']"),
                ('xpath', "//input[@aria-label='Create password']"),
                ('css', "input[type='password']"),
            ]
            
            if not self.smart_fill(driver, password_selectors, info['password']):
                print("❌ Password field not found")
                return False
            time.sleep(0.5)
            
            # === STEP 6: Confirm password ===
            confirm_selectors = [
                ('xpath', "(//input[@type='password'])[2]"),
                ('xpath', "//input[@name='PasswdAgain']"),
                ('xpath', "//input[@aria-label='Confirm']"),
                ('xpath', "//input[@aria-label='Confirm password']"),
            ]
            
            if not self.smart_fill(driver, confirm_selectors, info['password']):
                print("❌ Confirm password field not found")
                return False
            time.sleep(1)
            
            # === STEP 7: Next setelah password ===
            try:
                next_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))
                )
                next_btn.click()
                print("✅ Clicked Next after password")
                time.sleep(4)
            except:
                print("ℹ️ No Next button after password, maybe already on next page")
            
            # === STEP 8: Personal info (jika ada) ===
            # Month
            try:
                if self.check_element_exists(driver, By.XPATH, "//select[@aria-label='Month']"):
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
                if self.check_element_exists(driver, By.XPATH, "//select[@aria-label='Gender']"):
                    gender_select = driver.find_element(By.XPATH, "//select[@aria-label='Gender']")
                    Select(gender_select).select_by_value('1' if info['gender'] == 'Male' else '2')
                    print(f"✅ Gender selected: {info['gender']}")
                    time.sleep(0.3)
            except:
                pass
            
            # Next after personal info
            try:
                next_btn = driver.find_element(By.XPATH, "//span[text()='Next']")
                next_btn.click()
                print("✅ Clicked Next after personal info")
                time.sleep(4)
            except:
                pass
            
            # === STEP 9: Skip phone verification (jika ada) ===
            try:
                skip_btn = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Skip']"))
                )
                skip_btn.click()
                print("✅ Skipped phone verification")
                time.sleep(2)
            except:
                pass
            
            # === STEP 10: I agree (jika ada) ===
            try:
                agree_btn = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='I agree']"))
                )
                agree_btn.click()
                print("✅ Clicked I agree")
                time.sleep(3)
            except:
                pass
            
            # === CHECK SUCCESS ===
            time.sleep(5)
            current_url = driver.current_url.lower()
            page_source = driver.page_source.lower()
            
            success_indicators = [
                'myaccount.google.com',
                'accounts.google.com/signin',
                'welcome to google',
                'account successfully created',
                'confirm your recovery email'
            ]
            
            if any(indicator in current_url or indicator in page_source for indicator in success_indicators):
                self.save_account(info)
                self.success += 1
                print(f"✅✅✅ SUCCESS: {info['email']}")
                return True
            else:
                print(f"❌ Failed - URL: {current_url[:100]}...")
                driver.save_screenshot(f"error_final_{int(time.time())}.png")
                self.failed += 1
                return False
            
        except Exception as e:
            print(f"❌ Error: {str(e)[:200]}")
            if driver:
                driver.save_screenshot(f"error_exception_{int(time.time())}.png")
            self.failed += 1
            return False
        finally:
            if driver:
                driver.quit()

    def save_account(self, info):
        """Save account to JSON"""
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
            'created_at': datetime.now().isoformat()
        })
        
        with open(config.ACCOUNTS_DB, 'w') as f:
            json.dump(accounts, f, indent=2)
        
        # Simple CSV
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
                print(f"⏰ Sleeping {delay:.0f}s before next account...")
                time.sleep(delay)
        
        print(f"\n{'='*60}")
        print(f"🏁 FINISHED! ✅ Success: {self.success} | ❌ Failed: {self.failed}")
        
        # Final notif ke Telegram
        if self.notifier:
            try:
                accounts = []
                if os.path.exists(config.ACCOUNTS_DB):
                    with open(config.ACCOUNTS_DB, 'r') as f:
                        accounts = json.load(f)
                stats = {
                    'success': self.success, 
                    'failed': self.failed, 
                    'total': len(accounts),
                    'duration': 0
                }
                self.notifier.notify_account_creation(stats)
                print("✅ Telegram notification sent")
            except Exception as e:
                print(f"❌ Failed to send Telegram notification: {e}")

if __name__ == "__main__":
    factory = StealthAccountFactory()
    factory.run(count=getattr(config, 'TARGET_AKUN_PER_HARI', 100))
