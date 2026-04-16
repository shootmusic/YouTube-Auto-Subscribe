# account_factory_stealth.py - 1 AKUN PER HARI
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
    TARGET_AKUN_PER_HARI = 1

try:
    import config
except ImportError:
    config = Config()

class StealthAccountFactory:
    def __init__(self):
        self.success = 0
        self.failed = 0

    def generate_account(self):
        first_names = ['Alex', 'Jordan', 'Casey', 'Morgan', 'Riley', 'Avery', 'Quinn', 'Skyler', 'Thomas', 'Steven']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Jackson', 'Miller']
        
        first = random.choice(first_names)
        last = random.choice(last_names)
        username = f"{first.lower()}{last.lower()}{random.randint(100,999)}"
        
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choice(chars) for _ in range(12))
        
        from datetime import date, timedelta
        # PASTIKAN UMUR 20-35 TAHUN (VALID)
        min_age = date.today() - timedelta(days=365*20)
        max_age = date.today() - timedelta(days=365*35)
        random_date = max_age + timedelta(days=random.randint(0, (min_age-max_age).days))
        
        return {
            'first': first, 'last': last, 'username': username,
            'email': f"{username}@gmail.com", 'password': password,
            'birthday': {'year': random_date.year, 'month': random_date.month, 'day': random_date.day},
            'gender': random.choice(['Male', 'Female'])
        }

    def create_driver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver

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

    def click_next(self, driver):
        """Klik Next dengan berbagai metode"""
        try:
            # Scroll ke tombol Next
            next_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", next_btn)
            print("✅ Next clicked (JavaScript)")
            return True
        except Exception as e:
            print(f"❌ Next click error: {e}")
            return False

    def create_account(self):
        driver = None
        try:
            info = self.generate_account()
            print(f"\n{'='*60}")
            print(f"🔥 Creating: {info['email']}")
            print(f"🎂 Birthday: {info['birthday']['day']}/{info['birthday']['month']}/{info['birthday']['year']}")
            print(f"⚥ Gender: {info['gender']}")
            print(f"{'='*60}")
            
            driver = self.create_driver()
            driver.get("https://accounts.google.com/signup")
            time.sleep(5)
            
            # ========== STEP 1: NAME ==========
            print("\n📍 STEP 1: Name")
            if not self.smart_fill(driver, "//input[@name='firstName']", info['first']):
                print("❌ First name failed")
                return False
            time.sleep(0.5)
            
            if not self.smart_fill(driver, "//input[@name='lastName']", info['last']):
                print("❌ Last name failed")
                return False
            time.sleep(0.5)
            
            if not self.click_next(driver):
                return False
            time.sleep(4)
            
            # ========== STEP 2: BIRTHDAY & GENDER ==========
            print("\n📍 STEP 2: Birthday & Gender")
            
            # CEK ERROR MESSAGE SEBELUM INPUT
            try:
                errors = driver.find_elements(By.XPATH, "//div[contains(@class, 'error') or contains(@role, 'alert')]")
                for err in errors:
                    if err.text:
                        print(f"⚠️ ERROR: {err.text}")
            except:
                pass
            
            # Month
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
            
            # Day
            day_str = str(info['birthday']['day']).zfill(2)
            if not self.smart_fill(driver, "//input[@aria-label='Day']", day_str):
                print("❌ Day failed")
                return False
            print(f"✅ Day: {day_str}")
            time.sleep(0.5)
            
            # Year
            year_str = str(info['birthday']['year'])
            if not self.smart_fill(driver, "//input[@aria-label='Year']", year_str):
                print("❌ Year failed")
                return False
            print(f"✅ Year: {year_str}")
            time.sleep(0.5)
            
            # Gender
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
            
            # CEK ERROR MESSAGE SETELAH INPUT
            try:
                errors = driver.find_elements(By.XPATH, "//div[contains(@class, 'error') or contains(@role, 'alert')]")
                for err in errors:
                    if err.text:
                        print(f"⚠️ ERROR AFTER INPUT: {err.text}")
            except:
                pass
            
            # KLIK NEXT DENGAN CEK URL
            print("🔘 Clicking Next on birthday page...")
            current_url = driver.current_url
            
            if not self.click_next(driver):
                print("❌ Next button on birthday page failed")
                return False
            
            # TUNGGU DAN CEK URL BERUBAH
            time.sleep(5)
            new_url = driver.current_url
            
            if current_url == new_url:
                print("❌ URL NOT CHANGED - Still on birthday page")
                # Coba force refresh
                driver.refresh()
                time.sleep(3)
                new_url = driver.current_url
                if current_url == new_url:
                    return False
            
            print(f"✅ URL changed to: {new_url[:80]}")
            time.sleep(3)
            
            # ========== STEP 3: USERNAME PAGE ==========
            print("\n📍 STEP 3: Username page")
            
            # CEK APAKAH ADA CAPTCHA/CHALLENGE
            if "captcha" in driver.current_url.lower() or "challenge" in driver.current_url.lower():
                print("🚫 CAPTCHA/CHALLENGE DETECTED")
                return False
            
            # ISI USERNAME
            username_selectors = [
                "//input[@name='Username']",
                "//input[@id='username']",
                "//input[@type='text'][contains(@aria-label, 'username')]",
                "//input[@type='text'][contains(@aria-label, 'Gmail')]"
            ]
            
            username_filled = False
            for sel in username_selectors:
                try:
                    username_input = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, sel))
                    )
                    username_input.clear()
                    username_input.send_keys(info['username'])
                    print(f"✅ Username entered: {info['username']}")
                    username_filled = True
                    break
                except:
                    continue
            
            if not username_filled:
                print("ℹ️ No username input (Google will auto-generate)")
            
            if not self.click_next(driver):
                print("❌ Next after username failed")
                return False
            time.sleep(5)
            
            # ========== STEP 4: PASSWORD ==========
            print("\n📍 STEP 4: Password page")
            
            # TUNGGU PASSWORD FIELD (MAX 30 DETIK)
            password_fields = []
            for attempt in range(30):
                pwd_fields = driver.find_elements(By.XPATH, "//input[@type='password']")
                if pwd_fields:
                    password_fields = pwd_fields
                    print(f"✅ Password field found ({len(password_fields)} fields)")
                    break
                time.sleep(1)
            
            if len(password_fields) >= 2:
                for char in info['password']:
                    password_fields[0].send_keys(char)
                    time.sleep(0.05)
                print("✅ Password entered")
                time.sleep(0.5)
                
                for char in info['password']:
                    password_fields[1].send_keys(char)
                    time.sleep(0.05)
                print("✅ Confirm entered")
                
            elif len(password_fields) == 1:
                password_fields[0].send_keys(info['password'])
                print("✅ Password entered")
                
                confirm = driver.find_elements(By.XPATH, "//input[@type='password'][contains(@aria-label, 'Confirm')]")
                if confirm:
                    confirm[0].send_keys(info['password'])
                    print("✅ Confirm entered")
            else:
                print("❌ No password fields found")
                return False
            
            if not self.click_next(driver):
                print("⚠️ No Next after password")
            time.sleep(4)
            
            # ========== STEP 5: SKIP PHONE ==========
            try:
                skip_btn = driver.find_element(By.XPATH, "//span[text()='Skip']")
                driver.execute_script("arguments[0].click();", skip_btn)
                print("✅ Skipped phone verification")
                time.sleep(2)
            except:
                pass
            
            # ========== STEP 6: I AGREE ==========
            try:
                agree_btn = driver.find_element(By.XPATH, "//span[text()='I agree']")
                driver.execute_script("arguments[0].click();", agree_btn)
                print("✅ Accepted terms")
                time.sleep(3)
            except:
                pass
            
            # ========== CHECK SUCCESS ==========
            time.sleep(5)
            current_url = driver.current_url.lower()
            
            if any(x in current_url for x in ['myaccount.google.com', 'accounts.google.com/signin', 'welcome']):
                try:
                    email_elem = driver.find_element(By.XPATH, "//div[contains(text(), '@gmail.com')]")
                    info['email'] = email_elem.text.strip()
                    print(f"📧 Google generated email: {info['email']}")
                except:
                    pass
                
                self.save_account(info)
                self.success = 1
                print(f"\n✅✅✅ SUCCESS: {info['email']}")
                return True
            else:
                print(f"\n❌ Failed - URL: {current_url[:100]}")
                return False
                
        except Exception as e:
            print(f"\n❌ Error: {str(e)[:200]}")
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
        print(f"💾 Account saved")

    def run(self, count=1):
        print(f"\n{'='*60}")
        print(f"🔥 MEMBUAT {count} AKUN PER HARI")
        print(f"{'='*60}")
        
        for i in range(count):
            print(f"\n📌 Akun ke-{i+1}/{count}")
            success = self.create_account()
            if success:
                self.success += 1
            else:
                self.failed += 1
        
        print(f"\n{'='*60}")
        print(f"🏁 SELESAI! ✅ Berhasil: {self.success} | ❌ Gagal: {self.failed}")
        print(f"{'='*60}")

if __name__ == "__main__":
    factory = StealthAccountFactory()
    factory.run(count=config.TARGET_AKUN_PER_HARI)
