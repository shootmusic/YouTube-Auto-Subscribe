# account_factory.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import random
import json
import os
import string
from datetime import datetime
import config
from telegram_notifier import TelegramNotifier

class GoogleAccountFactory:
    def __init__(self):
        self.notifier = TelegramNotifier()
        self.names = self.load_names()
        self.success = 0
        self.failed = 0
        self.start_time = None
        
    def load_names(self):
        first_names = ['John', 'James', 'Robert', 'Michael', 'William', 'David', 
                       'Richard', 'Joseph', 'Thomas', 'Charles', 'Christopher', 
                       'Daniel', 'Matthew', 'Anthony', 'Donald', 'Mark', 'Paul',
                       'Steven', 'Andrew', 'Kenneth', 'Joshua', 'George', 'Kevin',
                       'Brian', 'Edward', 'Ronald', 'Timothy', 'Jason', 'Jeffrey',
                       'Ryan', 'Jacob', 'Gary', 'Nicholas', 'Eric', 'Jonathan',
                       'Stephen', 'Larry', 'Justin', 'Scott', 'Brandon', 'Benjamin',
                       'Samuel', 'Gregory', 'Alexander', 'Patrick', 'Frank', 'Raymond']
        
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 
                      'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez',
                      'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore',
                      'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White', 'Harris',
                      'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker',
                      'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen',
                      'Hill', 'Flores', 'Green', 'Adams', 'Nelson', 'Baker', 'Hall',
                      'Rivera', 'Campbell', 'Mitchell', 'Carter', 'Roberts']
        
        return first_names, last_names
    
    def generate_account(self):
        first_names, last_names = self.names
        first = random.choice(first_names)
        last = random.choice(last_names)
        
        nums = ''.join([str(random.randint(0,9)) for _ in range(4)])
        username = f"{first.lower()}.{last.lower()}{nums}"
        email = f"{username}@gmail.com"
        
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choice(chars) for _ in range(14))
        
        year = random.randint(1985, 2005)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        
        return {
            'first': first,
            'last': last,
            'email': email,
            'password': password,
            'birthday': f"{year}-{month:02d}-{day:02d}",
            'gender': random.choice(['Male', 'Female']),
            'created_at': datetime.now().isoformat()
        }
    
    def create_driver(self):
        service = Service('/data/data/com.termux/files/usr/bin/chromedriver')
        options = Options()
        options.binary_location = '/data/data/com.termux/files/usr/lib/chromium/chrome'
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def create_single_account(self):
        driver = None
        try:
            info = self.generate_account()
            print(f"📧 Membuat: {info['email']}")
            
            driver = self.create_driver()
            driver.get("https://accounts.google.com/signup")
            time.sleep(random.uniform(3, 5))
            
            # First name - pake XPATH based on aria-label
            first_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@aria-label='First name']"))
            )
            first_input.send_keys(info['first'])
            time.sleep(0.5)
            
            # Last name
            last_input = driver.find_element(By.XPATH, "//input[@aria-label='Last name']")
            last_input.send_keys(info['last'])
            time.sleep(0.5)
            
            # Username - pake XPATH based on aria-label
            username_input = driver.find_element(By.XPATH, "//input[@aria-label='Username']")
            username_input.send_keys(info['email'].split('@')[0])
            time.sleep(0.5)
            
            # Password
            pass_input = driver.find_element(By.XPATH, "//input[@aria-label='Password']")
            pass_input.send_keys(info['password'])
            time.sleep(0.5)
            
            # Confirm password
            confirm_input = driver.find_element(By.XPATH, "//input[@aria-label='Confirm']")
            confirm_input.send_keys(info['password'])
            time.sleep(0.5)
            
            # Next
            driver.find_element(By.XPATH, "//span[text()='Next']").click()
            time.sleep(random.uniform(4, 6))
            
            # Personal info - Month
            month_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//select[@aria-label='Month']"))
            )
            month_input.send_keys(info['birthday'].split('-')[1])
            time.sleep(0.3)
            
            # Day
            day_input = driver.find_element(By.XPATH, "//input[@aria-label='Day']")
            day_input.send_keys(info['birthday'].split('-')[2])
            time.sleep(0.3)
            
            # Year
            year_input = driver.find_element(By.XPATH, "//input[@aria-label='Year']")
            year_input.send_keys(info['birthday'].split('-')[0])
            time.sleep(0.3)
            
            # Gender
            gender_input = driver.find_element(By.XPATH, "//select[@aria-label='Gender']")
            gender_input.send_keys(info['gender'])
            time.sleep(0.3)
            
            # Next
            driver.find_element(By.XPATH, "//span[text()='Next']").click()
            time.sleep(random.uniform(4, 6))
            
            # Skip phone
            try:
                skip_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Skip']"))
                )
                driver.execute_script("arguments[0].click();", skip_btn)
                time.sleep(2)
            except:
                pass
            
            # Terms
            try:
                agree_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='I agree']"))
                )
                agree_btn.click()
                time.sleep(3)
            except:
                pass
            
            # Check success
            if "Welcome" in driver.title or "Success" in driver.page_source:
                self.save_account(info)
                self.success += 1
                print(f"✅ BERHASIL: {info['email']}")
                return True
            else:
                self.failed += 1
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
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
        
        accounts.append(info)
        
        with open(config.ACCOUNTS_DB, 'w') as f:
            json.dump(accounts, f, indent=2)
    
    def run(self, target_count=100):
        self.start_time = time.time()
        self.success = 0
        self.failed = 0
        
        print(f"\n🔥 MEMULAI PRODUKSI {target_count} AKUN")
        
        for i in range(target_count):
            print(f"\n📌 Progress: {i+1}/{target_count}")
            self.create_single_account()
            delay = random.uniform(30, 60)
            print(f"⏰ Delay {delay:.0f} detik...")
            time.sleep(delay)
        
        duration = (time.time() - self.start_time) / 60
        
        total_accounts = 0
        if os.path.exists(config.ACCOUNTS_DB):
            with open(config.ACCOUNTS_DB, 'r') as f:
                total_accounts = len(json.load(f))
        
        stats = {
            'success': self.success,
            'failed': self.failed,
            'total': total_accounts,
            'duration': duration
        }
        
        self.notifier.notify_account_creation(stats)
        return stats

if __name__ == "__main__":
    factory = GoogleAccountFactory()
    factory.run(target_count=config.TARGET_AKUN_PER_HARI)
