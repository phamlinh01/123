import os
import sys
import subprocess
import time
import random
import string
import re

def install_module(module_name):
    try:
        __import__(module_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])

for m in ("selenium", "webdriver_manager", "requests", "selenium_stealth"):
    install_module(m)

try:
    from selenium_stealth import stealth
except Exception:
    stealth = None

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests

DOMAINS = ["satato.com.vn"]
USERAGENT_FILE = "useragent.txt"
HO_FILE = "ho.txt"
TEN_FILE = "ten.txt"
ACCOUNTS_OUTPUT = "accounts_cookies.txt"

def generate_fake_useragent():
    try:
        with open(USERAGENT_FILE, "r", encoding="utf-8") as f:
            uas = [l.strip() for l in f if l.strip()]
            if uas:
                return random.choice(uas)
    except Exception:
        pass
    major = random.randint(100, 120)
    build = random.randint(0, 9999)
    patch = random.randint(0, 999)
    win_ver = random.choice(["10.0", "6.1", "6.3"])
    ua = f"Mozilla/5.0 (Windows NT {win_ver}; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{major}.0.{build}.{patch} Safari/537.36"
    return ua

def random_email(length=8):
    letters = string.ascii_lowercase + string.digits
    prefix = ''.join(random.choice(letters) for _ in range(length))
    return prefix, f"{prefix}@{random.choice(DOMAINS)}"

def random_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
    return ''.join(random.choice(chars) for _ in range(length))

def random_fullname_from_files():
    try:
        with open(HO_FILE, "r", encoding="utf-8") as f:
            ho = [line.strip() for line in f if line.strip()]
    except:
        ho = ["Nguyen","Le","Tran"]
    try:
        with open(TEN_FILE, "r", encoding="utf-8") as f:
            ten = [line.strip() for line in f if line.strip()]
    except:
        ten = ["Anh","Minh","Hoa"]
    return f"{random.choice(ho)} {random.choice(ten)}"

def random_username():
    ho_list = ["nguyen", "le", "tran", "pham", "hoang", "vo", "dang", "bui", "do", "ngo", "duong", "ly", "truong", "cao", "ha"]
    ten_list = ["anh", "bao", "khoa", "minh", "ngoc", "thao", "phuong", "nhu", "huy", "tuan", "dat", "linh", "khanh", "trang", "vy"]
    ho = random.choice(ho_list)
    ten1, ten2 = random.sample(ten_list, 2)
    so_length = random.choice([3, 4, 5])
    so = str(random.randint(10**(so_length-1), 10**so_length - 1))
    timestamp = str(int(time.time() * 1000))[-4:]
    patterns = [
        f"{ho}{ten1}{ten2}{so}",
        f"{ho}{ten1}{so}",
        f"{ten1}{ten2}{so}",
        f"{ho}_{ten1}_{ten2}_{so}",
        f"{ho}_{ten1}_{so}",
        f"{ten1}_{ten2}_{so}",
    ]
    return random.choice(patterns).lower()[:25]

def save_account(username, password, email):
    with open(ACCOUNTS_OUTPUT, "a", encoding="utf-8") as f:
        f.write(f"{username}|{password}|{email}\n")

def get_email_code(email):
    url = f"https://hunght1890.com/{email}"
    for _ in range(30):
        try:
            res = requests.get(url, timeout=30)
            if res.status_code == 200:
                mails = res.json()
                if mails:
                    body = mails[0].get("body", "")
                    subject = mails[0].get("subject", "")
                    match = re.search(r"\b\d{6}\b", body) or re.search(r"\b\d{6}\b", subject)
                    if match:
                        return match.group(0)
            time.sleep(3)
        except Exception:
            time.sleep(3)
    return None

def init_driver(headless=False, window_position=None):
    chrome_options = Options()
    chrome_options.add_argument("--lang=vi")
    chrome_options.add_argument("--window-size=800,600")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    if window_position:
        chrome_options.add_argument(f"--window-position={window_position}")
    chrome_options.add_argument(f"--user-agent={generate_fake_useragent()}")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    if headless:
        chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    if stealth:
        try:
            stealth(driver, languages=["vi-VN", "vi"], vendor="Google Inc.", platform="Win32",
                    webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)
        except Exception:
            pass
    try:
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    except Exception:
        pass
    return driver

def create_account_once(account_number, headless):
    driver = None
    try:
        driver = init_driver(headless=headless)
        driver.get("https://www.instagram.com/accounts/emailsignup/")

        WebDriverWait(driver, 60).until(lambda d: all([
            d.find_elements(By.NAME, "emailOrPhone"),
            d.find_elements(By.NAME, "password"),
            d.find_elements(By.NAME, "fullName"),
            d.find_elements(By.NAME, "username")
        ]))

        _, email = random_email()
        password = random_password()
        fullname = random_fullname_from_files()
        insta_username = random_username()

        driver.find_element(By.NAME, "emailOrPhone").clear()
        time.sleep(1.5)
        driver.find_element(By.NAME, "emailOrPhone").send_keys(email)
        driver.find_element(By.NAME, "password").clear()
        time.sleep(1.5)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.NAME, "fullName").clear()
        time.sleep(1.5)
        driver.find_element(By.NAME, "fullName").send_keys(fullname)

        username_field = driver.find_element(By.NAME, "username")
        username_field.clear()
        time.sleep(1.5)
        username_field.send_keys(insta_username)
        time.sleep(3)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        print(f"[{account_number}] ⏳ Đang gửi form đăng ký...")

        WebDriverWait(driver, 60).until(lambda d: d.find_elements(By.XPATH, "//select[@title='Tháng:']"))
        print(f"[{account_number}] ✅ Form đăng ký thành công, đang chọn ngày sinh...")

        Select(driver.find_element(By.XPATH, "//select[@title='Tháng:']")).select_by_value(str(random.randint(1, 12)))
        Select(driver.find_element(By.XPATH, "//select[@title='Ngày:']")).select_by_value(str(random.randint(1, 28)))
        Select(driver.find_element(By.XPATH, "//select[@title='Năm:']")).select_by_value(str(random.randint(1950, 2005)))

        time.sleep(3)
        try:
            driver.find_element(By.XPATH, "//button[text()='Tiếp']").click()
        except:
            try:
                driver.find_element(By.XPATH, "//div[@role='button' and (text()='Tiếp' or text()='Next')]").click()
            except:
                pass

        print(f"[{account_number}] ⏳ Đang chờ mã xác nhận gửi đến {email}...")
        WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.NAME, "email_confirmation_code")))

        code = get_email_code(email)
        if not code:
            print(f"[{account_number}] ❌ Không nhận được mã, bỏ qua tài khoản này.")
            return

        driver.find_element(By.NAME, "email_confirmation_code").send_keys(code)
        time.sleep(3)
        try:
            driver.find_element(By.XPATH, "//div[@role='button' and (text()='Tiếp' or text()='Next')]").click()
            time.sleep(30)
            print(f"[{account_number}] ⏳ Đang đợi 30s để hoàn thành tạo acc...")
        except:
            pass

        print(f"[{account_number}] ✅ Hoàn tất đăng ký, lưu tài khoản...")
        save_account(insta_username, password, email)
        print(f"[{account_number}] 🎉 {insta_username} | {password} | {email}")

    except Exception as e:
        print(f"[{account_number}] ❌ Lỗi: {e}")

    finally:
        try:
            if driver:
                driver.quit()
        except:
            pass

def main():
    print("Tool Reg Acc IG")
    try:
        raw_count = input("Nhập số tài khoản cần tạo (mặc định 10): ").strip()
        count = int(raw_count) if raw_count else 10
    except:
        count = 10
    try:
        raw_delay = input("Nhập delay giữa các tài khoản (giây, mặc định 5): ").strip()
        delay = int(raw_delay) if raw_delay else 5
    except:
        delay = 5

    headless_input = input("Ẩn Chrome? (y/N): ").strip().lower()
    headless = headless_input == "y"

    print(f"Bắt đầu tạo {count} tài khoản. delay={delay}s, headless={headless}")

    created = 0
    for i in range(1, count + 1):
        print(f"\n--- Tài khoản {i}/{count} ---")
        create_account_once(i, headless)
        created += 1
        if i < count:
            print(f"Đợi {delay} giây...")
            time.sleep(delay)

    print(f"\nHoàn tất. Đã lưu {created}/{count} tài khoản vào '{ACCOUNTS_OUTPUT}'.")

if __name__ == "__main__":
    main()
