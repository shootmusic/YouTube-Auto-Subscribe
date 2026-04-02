# account_factory_stealth.py - BIRTHDAY FIX
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
    TARGET_AKUN_PER_HARI = 5

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
        options.add_argument('--window-size=1920,1080)
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
        timestamp = int(time.time())
        print(f"\n🔍 DEBUG [{step_name}]")
        print(f"🌐 URL: {driver.current_url}")
        
        try:
            driver.save_screenshot(f'debug_{step_name}_{timestamp}.png')
            print(f"📸 Screenshot saved")
        except:
            pass
        
        try:
            with open(f'debug_{step_name}_{timestamp}.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print(f"📄 HTML saved")
        except:
            pass
        
        try:
            inputs = driver.find_elements(By.TAG_NAME, "input")
            print(f"📝 Inputs: {len(inputs)}")
            for i, inp in enumerate(inputs[:5]):
                t = inp.get_attribute('type') or 'no-type'
                n = inp.get_attribute('name') or 'no-name'
                a = inp.get_attribute('aria-label') or 'no-aria'
                print(f"  [{i}] {t}, {n}, {a[:25]}")
        except:
            pass

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
            
            # ========== STEP 2: BIRTHDAY (FIXED) ==========
            print("\n📍 STEP 2: Birthday")
            
            self.debug_page(driver, "birthday_start")
            
            # ISI MONTH
            try:
                month_select = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//select[@aria-label='Month']"))
                )
                Select(month_select).select_by_value(str(info['birthday']['month']))
                print(f"✅ Month: {info['birthday']['month']}")
                time.sleep(1)
            except Exception as e:
                print(f"❌ Month error: {e}")
                return False
            
            # ISI DAY (2 DIGIT)
            day_str = str(info['birthday']['day']).zfill(2)
            if not self.smart_fill(driver, "//input[@aria-label='Day']", day_str):
                print("❌ Day input failed")
                return False
            print(f"✅ Day: {day_str}")
            time.sleep(0.5)
            
            # ISI YEAR
            year_str = str(info['birthday']['year'])
            if not self.smart_fill(driver, "//input[@aria-label='Year']", year_str):
                print("❌ Year input failed")
                return False
            print(f"✅ Year: {year_str}")
            time.sleep(0.5)
            
            # ISI GENDER (WAJIB!)
            try:
                gender_select = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//select[@aria-label='Gender']"))
                )
                gender_value = '1' if info['gender'] == 'Male' else '2'
                Select(gender_select).select_by_value(gender_value)
                print(f"✅ Gender: {info['gender']}")
                time.sleep(1)
            except Exception as e:
                print(f"❌ Gender error: {e}")
                return False
            
            self.debug_page(driver, "birthday_filled")
            
            # KLIK NEXT + CEK URL BERUBAH
            print("🔘 Clicking Next...")
            current_url = driver.current_url
            
            try:
                next_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']/ancestor::button"))
                )
                next_btn.click()
                print("✅ Next clicked")
            except:
                print("❌ Next button not found")
                return False
            
            # TUNGGU URL BERUBAH (KRITIS!)
            time.sleep(2)
            new_url = driver.current_url
            print(f"🌐 URL: {new_url}")
            
            if "birthdaygender" in new_url:
                print("❌ STUCK ON BIRTHDAY PAGE - Aborting")
                self.debug_page(driver, "birthday_stuck")
                return False
            
            print("✅ Advanced from birthday page")
            time.sleep(3)
            
            # STEP 3: USERNAME
            print("\n📍 STEP 3: Username")
            self.debug_page(driver, "username_page")
            
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
                username_input = driver.find_element(By.XPATH, "//input[@type='text' and (contains(@aria-label, 'username') or contains(@aria-label, 'Gmail'))]")
                username_input.clear()
                username_input.send_keys(info['username'])
                print(f"✅ Username: {info['username']}")
                time.sleep(1)
            except:
                print("ℹ️ Auto-generated username")
            
            # KLIK NEXT
            try:
                driver.find_element(By.XPATH, "//span[text()='Next']").click()
                print("✅ Next after username")
                time.sleep(5)
            except:
                print("❌ Next failed")
                return False
            
            # STEP 4: PASSWORD
            print("\n📍 STEP 4: Password")
            self.debug_page(driver, "password_page")
            
            # CARI PASSWORD FIELDS
            pwd_fields = driver.find_elements(By.XPATH, "//input[@type='password']")
            print(f"🔑 Password fields: {len(pwd_fields)}")
            
            if len(pwd_fields) >= 2:
                for char in info['password']:
                    pwd_fields[0].send_keys(char)
                    time.sleep(0.05)
                for char in info['password']:
                    pwd_fields[1].send_keys(char)
                    time.sleep(0.05)
                print("✅ Password & confirm entered")
            elif len(pwd_fields) == 1:
                pwd_fields[0].send_keys(info['password'])
                print("✅ Password entered")
                driver.find_element(By.XPATH, "//span[text()='Next']").click()
                time.sleep(3)
                try:
                    confirm = driver.find_element(By.XPATH, "//input[@type='password' and (contains(@aria-label, 'Confirm') or @name='PasswdAgain')]")
                    confirm.send_keys(info['password'])
                    print("✅ Confirm entered")
                except:
                    pass
            else:
                print("❌ No password fields")
                return False
            
            # KLIK NEXT
            try:
                driver.find_element(By.XPATH, "//span[text()='Next']").click()
                print("✅ Next after password")
                time.sleep(4)
            except:
                pass
            
            # STEP 5: SKIP PHONE
            try:
                driver.find_element(By.XPATH, "//span[text()='Skip']").click()
                print("✅ Skipped phone")
                time.sleep(2)
            except:
                pass
            
            # STEP 6: I AGREE
            try:
                driver.find_element(By.XPATH, "//span[text()='I agree']").click()
                print("✅ Agreed")
                time.sleep(3)
            except:
                pass
            
            # CHECK SUCCESS
            time.sleep(5)
            current_url = driver.current_url.lower()
            if any(x in current_url for x in ['myaccount.google.com', 'accounts.google.com/signin']):
                self.save_account(info)
                self.success += 1
                print(f"✅✅✅ SUCCESS: {info['email']}")
                return True
            else:
                self.debug_page(driver, "final_failed")
                print(f"❌ Failed: {current_url[:80]}")
                self.failed += 1
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")
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
        print(f"\n🔥 Creating {count} accounts")
        for i in range(count):
            print(f"\n📌 {i+1}/{count} | ✅ {self.success} | ❌ {self.failed}")
            self.create_account()
            if i < count - 1:
                time.sleep(random.uniform(60, 120))
        print(f"\n🏁 Done! ✅ {self.success} | ❌ {self.failed}")

if __name__ == "__main__":
    factory = StealthAccountFactory()
    factory.run(count=getattr(config, 'TARGET_AKUN_PER_HARI', 5))
