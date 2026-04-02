# account_factory_stealth.py - DEBUG MODE FULL
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

class Config:
    ACCOUNTS_DB = 'accounts.json'
    TARGET_AKUN_PER_HARI = 5  # DEBUG: Coba 5 dulu

try:
    import config
except ImportError:
    config = Config()

class StealthAccountFactory:
    def __init__(self):
        self.success = 0
        self.failed = 0
        
    def generate_fingerprint(self):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36'
        ]
        return {'user_agent': random.choice(user_agents)}

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
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver, fp

    def generate_account(self):
        first_names = ['Alex', 'Jordan', 'Casey', 'Morgan', 'Riley', 'Avery', 'Quinn', 'Skyler', 'Thomas', 'Steven']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Jackson', 'Miller']
        
        first = random.choice(first_names)
        last = random.choice(last_names)
        username = f"{first.lower()}{last.lower()}{random.randint(100,999)}"
        
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choice(chars) for _ in range(12))
        
        from datetime import date, timedelta
        max_age = date.today() - timedelta(days=365*20)
        min_age = date.today() - timedelta(days=365*35)
        random_date = min_age + timedelta(days=random.randint(0, (max_age-min_age).days))
        
        return {
            'first': first, 'last': last, 'username': username,
            'email': f"{username}@gmail.com", 'password': password,
            'birthday': {'year': random_date.year, 'month': random_date.month, 'day': random_date.day},
            'gender': random.choice(['Male', 'Female'])
        }

    def debug_page(self, driver, step_name):
        """Save debug info untuk analisis"""
        timestamp = int(time.time())
        print(f"\n🔍 DEBUG [{step_name}]")
        print(f"🌐 URL: {driver.current_url}")
        
        # Screenshot
        try:
            driver.save_screenshot(f'debug_{step_name}_{timestamp}.png')
            print(f"📸 Screenshot: debug_{step_name}_{timestamp}.png")
        except:
            print("❌ Screenshot failed")
        
        # HTML
        try:
            with open(f'debug_{step_name}_{timestamp}.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print(f"📄 HTML: debug_{step_name}_{timestamp}.html")
        except:
            print("❌ HTML save failed")
        
        # List semua input
        try:
            inputs = driver.find_elements(By.TAG_NAME, "input")
            print(f"📝 Inputs found: {len(inputs)}")
            for i, inp in enumerate(inputs[:5]):
                t = inp.get_attribute('type') or 'no-type'
                n = inp.get_attribute('name') or 'no-name'
                a = inp.get_attribute('aria-label') or 'no-aria'
                print(f"  [{i}] type={t}, name={n}, aria={a[:30]}")
        except:
            pass
        
        # List semua button
        try:
            buttons = driver.find_elements(By.XPATH, "//button | //span[text()='Next'] | //span[text()='Skip']")
            print(f"🔘 Buttons found: {len(buttons)}")
            for i, btn in enumerate(buttons[:5]):
                try:
                    txt = btn.text[:30] if btn.text else 'no-text'
                    print(f"  [{i}] {txt}")
                except:
                    pass
        except:
            pass
        
        # Check text penting
        page_text = driver.page_source.lower()
        checks = ['password', 'create', 'confirm', 'captcha', 'sorry', 'verify', 'phone', 'unusual']
        found = [c for c in checks if c in page_text]
        if found:
            print(f"⚠️ Keywords found: {found}")

    def smart_fill(self, driver, xpath, value):
        try:
            elem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
            elem.click()
            elem.clear()
            for char in value:
                elem.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            return True
        except:
            return False

    def create_account(self):
        driver = None
        try:
            info = self.generate_account()
            print(f"\n{'='*60}")
            print(f"🔥 Creating: {info['email']}")
            print(f"{'='*60}")
            
            driver, _ = self.create_driver()
            driver.get("https://accounts.google.com/signup")
            time.sleep(5)
            
            # STEP 1: NAME
            print("\n📍 STEP 1: Name")
            self.smart_fill(driver, "//input[@name='firstName']", info['first'])
            time.sleep(0.5)
            self.smart_fill(driver, "//input[@name='lastName']", info['last'])
            time.sleep(0.5)
            
            driver.find_element(By.XPATH, "//span[text()='Next']").click()
            print("✅ Next after name")
            time.sleep(4)
            
            # STEP 2: BIRTHDAY
            print("\n📍 STEP 2: Birthday")
            try:
                month = Select(driver.find_element(By.XPATH, "//select[@aria-label='Month']"))
                month.select_by_value(str(info['birthday']['month']))
            except:
                pass
            self.smart_fill(driver, "//input[@aria-label='Day']", str(info['birthday']['day']))
            self.smart_fill(driver, "//input[@aria-label='Year']", str(info['birthday']['year']))
            try:
                gender = Select(driver.find_element(By.XPATH, "//select[@aria-label='Gender']"))
                gender.select_by_value('1' if info['gender'] == 'Male' else '2')
            except:
                pass
            
            driver.find_element(By.XPATH, "//span[text()='Next']").click()
            print("✅ Next after birthday")
            time.sleep(4)
            
            # STEP 3: USERNAME PAGE
            print("\n📍 STEP 3: Username")
            time.sleep(3)
            
            # DEBUG
            self.debug_page(driver, "username_page")
            
            # CEK CAPTCHA/CHALLENGE
            current_url = driver.current_url
            if "captcha" in current_url.lower() or "sorry" in current_url.lower():
                print("🚫 CAPTCHA/CHALLENGE - ABORT")
                return False
            
            # PILIH RADIO ATAU ISI USERNAME
            try:
                radios = driver.find_elements(By.XPATH, "//input[@type='radio']")
                if radios:
                    random.choice(radios).click()
                    print("✅ Selected username option")
                    time.sleep(1)
            except:
                pass
            
            try:
                username_input = driver.find_element(By.XPATH, "//input[@type='text' and (@name='Username' or contains(@aria-label, 'username') or contains(@aria-label, 'Gmail'))]")
                username_input.clear()
                username_input.send_keys(info['username'])
                print(f"✅ Entered username: {info['username']}")
                time.sleep(1)
            except:
                print("ℹ️ No username input (auto-generated)")
            
            # KLIK NEXT
            try:
                driver.find_element(By.XPATH, "//span[text()='Next']").click()
                print("✅ Next after username")
                time.sleep(5)  # TUNGGU LEBIH LAMA
            except:
                print("❌ Next failed")
                return False
            
            # ========== STEP 4: PASSWORD PAGE ==========
            print("\n📍 STEP 4: Password")
            
            # DEBUG SEBELUM CARI PASSWORD
            self.debug_page(driver, "password_page_before")
            
            # CEK CHALLENGE/CAPTCHA
            current_url = driver.current_url
            if any(x in current_url.lower() for x in ['captcha', 'sorry', 'challenge', 'verify']):
                print("🚫 CHALLENGE PAGE - CANNOT PROCEED")
                return False
            
            # TUNGGU PASSWORD FIELD (60 DETIK MAX)
            print("⏳ Waiting for password fields...")
            password_fields = []
            
            selectors = [
                "//input[@type='password']",
                "//input[@name='Passwd']",
                "//input[@name='password']",
                "//input[contains(@aria-label, 'Create password')]",
                "//input[contains(@aria-label, 'Confirm password')]",
                "//input[contains(@placeholder, 'password')]",
                "//input[@autocomplete='new-password']",
                "//input[contains(@aria-label, 'password')]"
            ]
            
            for attempt in range(12):  # 12 x 5 detik = 60 detik
                for selector in selectors:
                    try:
                        fields = driver.find_elements(By.XPATH, selector)
                        for f in fields:
                            if f not in password_fields:
                                password_fields.append(f)
                    except:
                        pass
                
                if len(password_fields) >= 2:
                    print(f"✅ Found {len(password_fields)} password field(s)")
                    break
                elif len(password_fields) == 1:
                    print(f"⚠️ Found 1 field, waiting for more...")
                
                print(f"  Attempt {attempt+1}/12 - fields: {len(password_fields)}")
                time.sleep(5)
            
            # DEBUG SETELAH CARI
            self.debug_page(driver, "password_page_after")
            
            # ISI PASSWORD
            if len(password_fields) >= 2:
                print("🔑 Filling password and confirm...")
                for char in info['password']:
                    password_fields[0].send_keys(char)
                    time.sleep(0.05)
                print("✅ Password entered")
                time.sleep(0.5)
                
                for char in info['password']:
                    password_fields[1].send_keys(char)
                    time.sleep(0.05)
                print("✅ Confirm password entered")
                
            elif len(password_fields) == 1:
                print("🔑 Single password field, filling...")
                password_fields[0].send_keys(info['password'])
                print("✅ Password entered")
                time.sleep(1)
                
                # KLIK NEXT, TUNGGU CONFIRM
                try:
                    driver.find_element(By.XPATH, "//span[text()='Next']").click()
                    print("⏩ Next clicked, waiting for confirm...")
                    time.sleep(3)
                    
                    confirm_selectors = [
                        "//input[@type='password']",
                        "//input[contains(@aria-label, 'Confirm')]",
                        "//input[@name='PasswdAgain']"
                    ]
                    
                    for sel in confirm_selectors:
                        try:
                            confirm = driver.find_element(By.XPATH, sel)
                            confirm.send_keys(info['password'])
                            print("✅ Confirm password entered")
                            break
                        except:
                            continue
                except:
                    print("ℹ️ No confirm field")
            else:
                print("❌ No password fields found after 60 seconds")
                return False
            
            # KLIK NEXT AFTER PASSWORD
            try:
                driver.find_element(By.XPATH, "//span[text()='Next']").click()
                print("✅ Next after password")
                time.sleep(4)
            except:
                pass
            
            # STEP 5: SKIP PHONE
            print("\n📍 STEP 5: Skip phone")
            try:
                driver.find_element(By.XPATH, "//span[text()='Skip']").click()
                print("✅ Skipped phone")
                time.sleep(2)
            except:
                print("ℹ️ No skip button")
            
            # STEP 6: I AGREE
            print("\n📍 STEP 6: I agree")
            try:
                driver.find_element(By.XPATH, "//span[text()='I agree']").click()
                print("✅ Agreed")
                time.sleep(3)
            except:
                print("ℹ️ No agree button")
            
            # CHECK SUCCESS
            print("\n📍 CHECKING SUCCESS...")
            time.sleep(5)
            current_url = driver.current_url.lower()
            print(f"🌐 Final URL: {current_url[:100]}")
            
            if any(x in current_url for x in ['myaccount.google.com', 'accounts.google.com/signin', 'myaccount']):
                self.save_account(info)
                self.success += 1
                print(f"✅✅✅ SUCCESS: {info['email']}")
                return True
            else:
                self.debug_page(driver, "final_not_success")
                print(f"❌ Failed")
                self.failed += 1
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:200]}")
            if driver:
                self.debug_page(driver, "error")
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
        accounts.append({**info, 'created_at': datetime.now().isoformat()})
        with open(config.ACCOUNTS_DB, 'w') as f:
            json.dump(accounts, f, indent=2)
        with open('accounts.csv', 'a') as f:
            f.write(f"{info['email']},{info['password']}\n")

    def run(self, count=5):
        print(f"\n{'='*60}")
        print(f"🔥 DEBUG MODE: Creating {count} accounts")
        print(f"{'='*60}")
        
        for i in range(count):
            print(f"\n{'='*60}")
            print(f"📌 Progress: {i+1}/{count} | ✅ {self.success} | ❌ {self.failed}")
            print(f"{'='*60}")
            
            self.create_account()
            
            if i < count - 1:
                delay = random.uniform(60, 120)  # DELAY LEBIH LAMA BUAT DEBUG
                print(f"\n⏰ Sleeping {delay:.0f}s...")
                time.sleep(delay)
        
        print(f"\n{'='*60}")
        print(f"🏁 FINISHED! ✅ {self.success} | ❌ {self.failed}")
        print(f"{'='*60}")

if __name__ == "__main__":
    factory = StealthAccountFactory()
    factory.run(count=getattr(config, 'TARGET_AKUN_PER_HARI', 5))
