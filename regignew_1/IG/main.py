import os
import sys
import subprocess
import threading
import time
import random
import string
import re
from concurrent.futures import ThreadPoolExecutor
import queue

def install_module(module_name):
    try:
        __import__(module_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])

for m in ["ttkbootstrap", "selenium", "webdriver_manager", "requests", "selenium_stealth"]:
    install_module(m)

import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap import ttk

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import requests

DOMAINS = ["satato.com.vn"]
USERAGENT_FILE = "useragent.txt"
HO_FILE = "ho.txt"
TEN_FILE = "ten.txt"
ACCOUNTS_OUTPUT = "accounts.txt"

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
        f"{ho}{ten1}{ten2}{timestamp}",
        f"{ho}{ten1}{so}{timestamp[-2:]}",
        f"{ten1}{ten2}{timestamp}{so[-2:]}",
        f"{ho}_{ten1}_{ten2}_{so}",
        f"{ho}_{ten1}_{so}",
        f"{ten1}_{ten2}_{so}",
        f"{ho}_{ten1}_{ten2}_{timestamp}",
        f"{ho}_{ten1}_{so}_{timestamp[-2:]}",
        f"{ten1}_{ten2}_{timestamp}_{so[-2:]}",
        f"{ho}_{ten1}{ten2}{so}",
        f"{ho}{ten1}_{ten2}{so}",
        f"{ho}.{ten1}.{ten2}.{so}",
        f"{ho}.{ten1}.{so}",
        f"{ten1}.{ten2}.{so}",
        f"{ho}.{ten1}.{ten2}.{timestamp}",
        f"{ho}.{ten1}.{so}.{timestamp[-2:]}",
        f"{ten1}.{ten2}.{timestamp}.{so[-2:]}",
        f"{ho}.{ten1}{ten2}{so}",
        f"{ho}{ten1}.{ten2}{so}",
        f"{ho}_{ten1}.{ten2}_{so}",
        f"{ho}.{ten1}_{ten2}.{so}",
        f"{ho}_{ten1}.{so}",
        f"{ho}.{ten1}_{so}",
        f"{ten1}_{ten2}.{timestamp}",
        f"{ten1}.{ten2}_{timestamp}"
    ]
    return random.choice(patterns).lower()[:25]

def save_account(username, password, birthday, email, cookie):
    with open(ACCOUNTS_OUTPUT, "a", encoding="utf-8") as f:
        f.write(f"{username}|{password}|{birthday}|{email}|{cookie}\n")

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
        except:
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
    try:
        with open(USERAGENT_FILE, "r", encoding="utf-8") as f:
            ua = [line.strip() for line in f if line.strip()]
            if ua:
                chrome_options.add_argument(f"--user-agent={random.choice(ua)}")
    except:
        pass
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
    try:
        stealth(driver, languages=["vi-VN", "vi"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)
    except:
        pass
    try:
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    except:
        pass
    return driver

def get_full_cookie_string(driver):
    return "; ".join([f"{c['name']}={c['value']}" for c in driver.get_cookies()])

def get_random_image(path):
    if path and os.path.exists(path):
        imgs = [f for f in os.listdir(path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if imgs:
            return os.path.join(path, random.choice(imgs))
    return None

def upload_profile_picture(driver, avatar_folder):
    try:
        driver.get("https://www.instagram.com/accounts/edit/")
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)
        img = get_random_image(avatar_folder)
        if not img:
            return False
        inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
        if not inputs:
            return False
        inputs[0].send_keys(os.path.abspath(img))
        time.sleep(6)
        return True
    except:
        return False

def create_account_worker(account_number, thread_index, headless, avatar_folder, result_queue, stop_flag):
    try:
        pos = None
        driver = init_driver(headless=headless, window_position=pos)
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
        driver.find_element(By.NAME, "emailOrPhone").send_keys(email)
        time.sleep(1.5)
        driver.find_element(By.NAME, "password").send_keys(password)
        time.sleep(1.5)
        driver.find_element(By.NAME, "fullName").send_keys(fullname)
        time.sleep(1.5)
        username_field = driver.find_element(By.NAME, "username")
        username_field.clear()
        time.sleep(0.5)
        username_field.send_keys(insta_username)
        time.sleep(5)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        WebDriverWait(driver, 60).until(lambda d: d.find_elements(By.XPATH, "//select[@title='Tháng:']"))
        Select(driver.find_element(By.XPATH, "//select[@title='Tháng:']")).select_by_value(str(random.randint(1, 12)))
        Select(driver.find_element(By.XPATH, "//select[@title='Ngày:']")).select_by_value(str(random.randint(1, 28)))
        Select(driver.find_element(By.XPATH, "//select[@title='Năm:']")).select_by_value(str(random.randint(1950, 2005)))
        time.sleep(5)
        try:
            driver.find_element(By.XPATH, "//button[text()='Tiếp']").click()
        except:
            try:
                driver.find_element(By.XPATH, "//div[@role='button' and (text()='Tiếp' or text()='Next')]").click()
            except:
                pass
        WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.NAME, "email_confirmation_code")))
        code = get_email_code(email)
        if not code:
            driver.quit()
            result_queue.put((account_number, insta_username, password, "random", email, "", False, "No code"))
            return
        driver.find_element(By.NAME, "email_confirmation_code").send_keys(code)
        time.sleep(5)
        try:
            driver.find_element(By.XPATH, "//div[@role='button' and (text()='Tiếp' or text()='Next')]").click()
        except:
            pass
        WebDriverWait(driver, 120).until(lambda d: "emailsignup" not in d.current_url)
        time.sleep(5)
        driver.get("https://www.instagram.com/accounts/edit/")
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, "username")))
        real_username = driver.find_element(By.NAME, "username").get_attribute("value")
        cookie = get_full_cookie_string(driver)
        save_account(real_username, password, "random", email, cookie)
        upload_profile_picture(driver, avatar_folder)
        driver.quit()
        result_queue.put((account_number, real_username, password, "random", email, cookie, True, "OK"))
    except Exception as e:
        try:
            driver.quit()
        except:
            pass
        result_queue.put((account_number, "", "", "", "", "", False, str(e)))

class AccountCreatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Reg Acc IG")
        self.root.geometry("1150x620")
        self.style = tb.Style("cosmo")
        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill="both", expand=True)
        title_label = ttk.Label(main_frame, text="ACCOUNT CREATOR", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 15))
        control_frame = ttk.LabelFrame(main_frame, text="Cài đặt", padding=15)
        control_frame.pack(fill="x", pady=(0, 15))
        row1 = ttk.Frame(control_frame)
        row1.pack(fill="x", pady=5)
        ttk.Label(row1, text="Số lượng:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.var_count = tk.IntVar(value=10)
        ttk.Entry(row1, textvariable=self.var_count, width=10).grid(row=0, column=1, padx=(0, 15))
        ttk.Label(row1, text="Luồng:").grid(row=0, column=2, padx=(0, 5), sticky="w")
        self.var_threads = tk.IntVar(value=2)
        ttk.Entry(row1, textvariable=self.var_threads, width=10).grid(row=0, column=3, padx=(0, 15))
        ttk.Label(row1, text="Delay (giây):").grid(row=0, column=4, padx=(0, 5), sticky="w")
        self.var_delay = tk.IntVar(value=5)
        ttk.Entry(row1, textvariable=self.var_delay, width=10).grid(row=0, column=5, padx=(0, 15))
        self.var_headless = tk.BooleanVar(value=False)
        ttk.Checkbutton(row1, text="Ẩn Chrome", variable=self.var_headless).grid(row=0, column=6, padx=(0, 15))
        row2 = ttk.Frame(control_frame)
        row2.pack(fill="x", pady=5)
        ttk.Label(row2, text="Folder Ảnh:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.var_avatar = tk.StringVar(value="")
        ttk.Entry(row2, textvariable=self.var_avatar, width=50).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(row2, text="Chọn...", command=self.select_avatar_folder).grid(row=0, column=2)
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        self.btn_start = ttk.Button(button_frame, text="Bắt đầu", bootstyle="success", command=self.start, width=12)
        self.btn_start.pack(side="left", padx=(0, 10))
        self.btn_stop = ttk.Button(button_frame, text="Dừng", bootstyle="danger", command=self.stop, state="disabled", width=12)
        self.btn_stop.pack(side="left")
        table_frame = ttk.LabelFrame(main_frame, text="Kết quả", padding=10)
        table_frame.pack(fill="both", expand=True)
        columns = ("STT","Username","Password","Birthday","Email","Cookie","Status","Note")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=18)
        column_widths = {"STT": 50, "Username": 120, "Password": 120, "Birthday": 80, "Email": 150, "Cookie": 200, "Status": 80, "Note": 120}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100), anchor="center")
        self.tree.column("Cookie", anchor="w")
        self.tree.column("Note", anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.tag_configure("success", background="#d4edda")
        self.tree.tag_configure("fail", background="#f8d7da")
        self.menu = tk.Menu(root, tearoff=0)
        self.menu.add_command(label="Copy cell", command=self.copy_cell)
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.is_running = False
        self.stop_event = threading.Event()
        self.result_queue = queue.Queue()
        self.total_created = 0
        self.root.after(300, self.poll_results)

    def select_avatar_folder(self):
        d = filedialog.askdirectory()
        if d:
            self.var_avatar.set(d)

    def show_context_menu(self, event):
        iid = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if iid:
            self.tree.selection_set(iid)
            self._rc_selected = (iid, col)
            self.menu.tk_popup(event.x_root, event.y_root)

    def copy_cell(self):
        iid, col = getattr(self, "_rc_selected", (None,None))
        if not iid: 
            return
        col_index = int(col.replace("#","")) - 1
        vals = self.tree.item(iid, "values")
        if 0 <= col_index < len(vals):
            val = vals[col_index]
            self.root.clipboard_clear()
            self.root.clipboard_append(val)
            messagebox.showinfo("Copied", "Đã copy ô vào clipboard")

    def start(self):
        if self.is_running:
            return
        try:
            count = int(self.var_count.get())
            threads = int(self.var_threads.get())
            delay = int(self.var_delay.get())
        except:
            messagebox.showerror("Lỗi", "Hãy nhập giá trị hợp lệ")
            return
        if count <= 0 or threads <= 0:
            messagebox.showerror("Lỗi", "Số lượng và luồng phải lớn hơn 0")
            return
        self.tree.delete(*self.tree.get_children())
        self.is_running = True
        self.stop_event.clear()
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.total_created = 0
        t = threading.Thread(target=self.manager_thread, args=(count, threads, delay, self.var_headless.get(), self.var_avatar.get()))
        t.daemon = True
        t.start()

    def stop(self):
        if not self.is_running:
            return
        self.stop_event.set()
        self.btn_stop.configure(state="disabled")
        self.btn_start.configure(state="normal")
        self.is_running = False

    def manager_thread(self, count, threads, delay, headless, avatar_folder):
        try:
            for batch_start in range(0, count, threads):
                if self.stop_event.is_set():
                    break
                batch = range(batch_start + 1, min(batch_start + threads + 1, count + 1))
                with ThreadPoolExecutor(max_workers=threads) as executor:
                    futures = []
                    for i in batch:
                        if self.stop_event.is_set():
                            break
                        self.root.after(0, self.insert_placeholder_row, i)
                        fut = executor.submit(create_account_worker, i, (i % threads) + 1, headless, avatar_folder, self.result_queue, self.stop_event)
                        futures.append(fut)
                    for f in futures:
                        try:
                            f.result()
                        except Exception as e:
                            self.result_queue.put((-1, "", "", "", "", "", False, str(e)))
                for _ in range(delay):
                    if self.stop_event.is_set():
                        break
                    time.sleep(1)
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.btn_start.configure(state="normal"))
            self.root.after(0, lambda: self.btn_stop.configure(state="disabled"))

    def insert_placeholder_row(self, stt):
        item = self.tree.insert("", "end", values=(stt, "", "", "", "", "", "Running", ""))
        self.tree.see(item)

    def poll_results(self):
        while True:
            try:
                item = self.result_queue.get_nowait()
            except queue.Empty:
                break
            stt, username, password, birthday, email, cookie, success, note = item
            found = None
            for iid in self.tree.get_children():
                vals = self.tree.item(iid, "values")
                if str(vals[0]) == str(stt):
                    found = iid
                    break
            if found is None:
                iid = self.tree.insert("", "end", values=(stt, username, password, birthday, email, cookie, "OK" if success else "FAIL", note), tags=("success",) if success else ("fail",))
            else:
                self.tree.item(found, values=(stt, username, password, birthday, email, cookie, "OK" if success else "FAIL", note), tags=("success",) if success else ("fail",))
            if success:
                self.total_created += 1
        self.root.after(300, self.poll_results)

def main():
    root = tb.Window(themename="cosmo")
    app = AccountCreatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
