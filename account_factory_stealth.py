# account_factory_stealth.py - FIXED USERNAME FLOW
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
    TARGET_AKUN_PER_HARI = 100

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
        first_names = ['Alex', 'Jordan', 'Casey', 'Morgan', 'Riley', 'Avery', 'Quinn', 'Skyler', 'Thomas', 'Steven', 'Kenneth']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Jackson']
        
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
            print(f"\n🔥 Creating: {info['email']}")
            
            driver, _ = self.create_driver()
            driver.get("https://accounts.google.com/signup")
            time.sleep(5)
            
            # STEP 1: NAME
            self.smart_fill(driver, "//input[@name='firstName']", info['first'])
            time.sleep(0.5)
            self.smart_fill(driver, "//input[@name='lastName']", info['last'])
            time.sleep(0.5)
            
            driver.find_element(By.XPATH, "//span[text()='Next']").click()
            print("✅ Next after name")
            time.sleep(4)
            
            # STEP 2: BIRTHDAY
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
            
            # ========== STEP 3: USERNAME PAGE (FIXED) ==========
            print("🔍 Handling username page...")
            time.sleep(3)
            
            current_url = driver.current_url
            
            # CARI RADIO BUTTON ATAU INPUT USERNAME
            try:
                # PILIH RANDOM RADIO OPTION (Create own / Suggested)
                radios = driver.find_elements(By.XPATH, "//input[@type='radio']")
                if radios:
                    random.choice(radios).click()
                    print("✅ Selected username option")
                    time.sleep(1)
            except:
                pass
            
            # ISI USERNAME KALO ADA INPUT
            try:
                username_input = driver.find_element(By.XPATH, "//input[@type='text' and (@name='Username' or contains(@aria-label, 'username') or contains(@aria-label, 'Gmail'))]")
                username_input.clear()
                username_input.send_keys(info['username'])
                print(f"✅ Entered username: {info['username']}")
                time.sleep(1)
            except:
                print("ℹ️ No username input found (might be auto-generated)")
            
            # KLIK NEXT
            try:
                driver.find_element(By.XPATH, "//span[text()='Next']").click()
                print("✅ Next after username")
                
                # TUNGGU TRANSISI
                try:
                    WebDriverWait(driver, 15).until(EC.url_changes(current_url))
                    print("✅ Page transitioned")
                except:
                    pass
                time.sleep(3)
            except Exception as e:
                print(f"❌ Next failed: {e}")
                return False
            
            # STEP 4: PASSWORD
            print("🔍 Waiting for password...")
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
                )
            except:
                print("❌ Password field timeout")
                return False
            
            pwd_fields = driver.find_elements(By.XPATH, "//input[@type='password']")
            if len(pwd_fields) >= 2:
                for char in info['password']:
                    pwd_fields[0].send_keys(char)
                    time.sleep(0.05)
                for char in info['password']:
                    pwd_fields[1].send_keys(char)
                    time.sleep(0.05)
                print("✅ Password entered")
            else:
                print(f"❌ Password fields: {len(pwd_fields)}")
                return False
            
            driver.find_element(By.XPATH, "//span[text()='Next']").click()
            print("✅ Next after password")
            time.sleep(4)
            
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

    def run(self, count=100):
        print(f"\n🔥 Creating {count} accounts")
        for i in range(count):
            print(f"\n📌 {i+1}/{count} | ✅ {self.success} | ❌ {self.failed}")
            self.create_account()
            if i < count - 1:
                time.sleep(random.uniform(30, 60))
        print(f"\n🏁 Done! ✅ {self.success} | ❌ {self.failed}")

if __name__ == "__main__":
    factory = StealthAccountFactory()
    factory.run(count=getattr(config, 'TARGET_AKUN_PER_HARI', 100))
