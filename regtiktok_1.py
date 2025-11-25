import time
import random
import requests
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
import threading

# Domain and password lists

Domain = [
    'nguyenhoang', 'tranthanhhai', 'leminhkhanh', 'phamthanhdat', 'hoangtrungnghia', 
    'dangphucanh', 'vothithu', 'phanquanghuy', 'huynhngocmai', 'dothanhlong', 
    'buivananh', 'hothithao', 'ngominhhai', 'duongduckhanh', 'lythanhvinh', 
    'nguyenthithuy', 'tranvandung', 'lehoangnam', 'phamthithao', 'hoangminhchau', 
    'dangquangvinh', 'vovanthang', 'phanthingoc', 'huynhvanlong', 'dothithu', 
    'buiquanghuy', 'hovanmai', 'ngothanhdat', 'duongthithuy', 'lyvandung', 
    'nguyenhoanganh', 'tranminhhai', 'lethanhkhanh', 'phamvandat', 'hoangthithu', 
    'dangminhchau', 'vothanhvinh', 'phanquanghuy', 'huynhthithao', 'dovanlong', 
    'buithithuy', 'hovananh', 'ngothanhdat', 'duongminhhai', 'lythanhkhanh', 
    'nguyenvandung', 'tranhoangnam', 'lethithao', 'phamminhchau', 'hoangquangvinh', 
    'dangvanthang', 'vothithu', 'phanvandung', 'huynhhoanganh', 'dothanhdat', 
    'buiminhhai', 'hothanhkhanh', 'ngovananh', 'duongthithuy', 'lyhoangnam', 
    'nguyenthithao', 'tranminhchau', 'lequangvinh', 'phamvanthang', 'hoangthithu', 
    'dangvandung', 'vohoanganh', 'phanthanhdat', 'huynhminhhai', 'dothanhkhanh', 
    'buivananh', 'hothithuy', 'ngominhchau', 'duongquangvinh', 'lyvanthang', 
    'nguyenthithu', 'tranvandung', 'lehoanganh', 'phamthanhdat', 'hoangminhhai', 
    'dangthanhkhanh', 'vovananh', 'phanthithuy', 'huynhhoangnam', 'dothithao', 
    'buiminhchau', 'hoquangvinh', 'ngovanthang', 'duongthithu', 'lyvandung', 
    'nguyenhoanganh', 'tranminhhai', 'lethanhkhanh', 'phamvandat', 'hoangthithu', 
    'dangminhchau', 'vothanhvinh', 'phanquanghuy', 'huynhthithao', 'dovanlong', 
    'buithithuy', 'hovananh', 'ngothanhdat', 'duongminhhai', 'lythanhkhanh', 
    'nguyenvandung', 'tranhoangnam', 'lethithao', 'phamminhchau', 'hoangquangvinh', 
    'dangvanthang', 'vothithu', 'phanvandung', 'huynhhoanganh', 'dothanhdat', 
    'buiminhhai', 'hothanhkhanh', 'ngovananh', 'duongthithuy', 'lyhoangnam', 
    'nguyenthithao', 'tranminhchau', 'lequangvinh', 'phamvanthang', 'hoangthithu', 
    'dangvandung', 'vohoanganh', 'phanthanhdat', 'huynhminhhai', 'dothanhkhanh', 
    'buivananh', 'hothithuy', 'ngominhchau', 'duongquangvinh', 'lyvanthang', 
    'nguyenthithu', 'tranvandung', 'lehoanganh', 'phamthanhdat', 'hoangminhhai', 
    'dangthanhkhanh', 'vovananh', 'phanthithuy', 'huynhhoangnam', 'dothithao', 
    'buiminhchau', 'hoquangvinh', 'ngovanthang', 'duongthithu', 'lyvandung', 
    'nguyenminhlong', 'tranthanhvy', 'leductri', 'phamngocyen', 'hoangthanhbinh', 
    'dangthithao', 'vominhhung', 'phanvanphong', 'huynhthanhson', 'dothithuy', 
    'buiquangnam', 'hovanhoa', 'ngothanhlinh', 'duongminhtam', 'lythanhphuc', 
    'nguyenvanquan', 'tranthithu', 'lehoangduy', 'phamminhkhanh', 'hoangthanhthu', 
    'dangvanvinh', 'vothanhngoc', 'phanquangdung', 'huynhthithuy', 'dovananh', 
    'buithanhhai', 'hothanhdat', 'ngominhchau', 'duongthanhvinh', 'lyvanthang', 
    'nguyenthithu', 'tranvandung', 'lehoanganh', 'phamthanhdat', 'hoangminhhai', 
    'dangthanhkhanh', 'vovananh', 'phanthithuy', 'huynhhoangnam', 'dothithao', 
    'buiminhchau', 'hoquangvinh', 'ngovanthang', 'duongthithu', 'lyvandung', 
    'nguyenhoanganh', 'tranminhhai', 'lethanhkhanh', 'phamvandat', 'hoangthithu'
]

passw = [
'explanation1', 'hypothesize1', 'combination1', 'personality1', 'calculation1', 'destination1', 'exploration1', 'architecture1', 'university1', 'consequence1', 'possibility1', 'organization1', 'considerable1', 'protectional1', 'environment1', 'transmission1', 'measurement1', 'presentation1', 'exaggeration1', 'concentration1', 'examination1', 'illustration1', 'optimization1', 'contribution1', 'determination1', 'announcement1', 'capabilities1', 'publication1', 'observation1', 'registration1', 'expectations1', 'introduction1', 'transparency1', 'arrangement1', 'exploitation1', 'installation1', 'preparation1', 'coordination1', 'manipulation1', 'participation1', 'qualifications1', 'recognition1', 'subscription1', 'contradiction1', 'modification1', 'transmission1', 'manufacturing1', 'configuration1', 'specialities1', 'appreciation1', 'authentication1', 'collaboration1', 'communication1', 'demonstration1', 'documentation1', 'experimentation1', 'identification1', 'implementation1', 'intervention1', 'justification1', 'mathematician1', 'multiplication1', 'notification1', 'perspiration1', 'preoccupation1', 'rehabilitation1', 'representation1', 'restructuring1', 'satisfaction1', 'simplification1', 'specification1', 'stabilization1', 'standardization1', 'subordination1', 'substantiation1', 'transportation1', 'transvaluation1', 'verification1', 'visualization1', 'accommodation1', 'accountability1', 'appropriation1', 'centralization1', 'characterization1', 'confrontation1', 'congratulation1', 'decentralization1', 'determination1', 'differentiation1', 'digitalization1', 'diversification1', 'elaboration1', 'generalization1', 'harmonization1', 'instrumentation1', 'international1', 'misrepresentation1'
'explanation2', 'hypothesize2', 'combination2', 'personality2', 'calculation2', 'destination2', 'exploration2', 'architecture2', 'university2', 'consequence2', 'possibility2', 'organization2', 'considerable2', 'protectional2', 'environment2', 'transmission2', 'measurement2', 'presentation2', 'exaggeration2', 'concentration2', 'examination2', 'illustration2', 'optimization2', 'contribution2', 'determination2', 'announcement2', 'capabilities2', 'publication2', 'observation2', 'registration2', 'expectations2', 'introduction2', 'transparency2', 'arrangement2', 'exploitation2', 'installation2', 'preparation2', 'coordination2', 'manipulation2', 'participation2', 'qualifications2', 'recognition2', 'subscription2', 'contradiction2', 'modification2', 'transmission2', 'manufacturing2', 'configuration2', 'specialities2', 'appreciation2', 'authentication2', 'collaboration2', 'communication2', 'demonstration2', 'documentation2', 'experimentation2', 'identification2', 'implementation2', 'intervention2', 'justification2', 'mathematician2', 'multiplication2', 'notification2', 'perspiration2', 'preoccupation2', 'rehabilitation2', 'representation2', 'restructuring2', 'satisfaction2', 'simplification2', 'specification2', 'stabilization2', 'standardization2', 'subordination2', 'substantiation2', 'transportation2', 'transvaluation2', 'verification2', 'visualization2', 'accommodation2', 'accountability2', 'appropriation2', 'centralization2', 'characterization2', 'confrontation2', 'congratulation2', 'decentralization2', 'determination2', 'differentiation2', 'digitalization2', 'diversification2', 'elaboration2', 'generalization2', 'harmonization2', 'instrumentation2', 'international2', 'misrepresentation2'
'explanation3', 'hypothesize3', 'combination3', 'personality3', 'calculation3', 'destination3', 'exploration3', 'architecture3', 'university3', 'consequence3', 'possibility3', 'organization3', 'considerable3', 'protectional3', 'environment3', 'transmission3', 'measurement3', 'presentation3', 'exaggeration3', 'concentration3', 'examination3', 'illustration3', 'optimization3', 'contribution3', 'determination3', 'announcement3', 'capabilities3', 'publication3', 'observation3', 'registration3', 'expectations3', 'introduction3'
]


def domains():
    headers = {
        'Referer': 'https://mail.tm/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    }
    try:
        domains = requests.get('https://api.mail.tm/domains', headers=headers).json()
        if 'hydra:member' in domains:
            return domains['hydra:member'][0]['domain']
        else:
            print('Lỗi khi lấy domain')
            return None
    except Exception as e:
        print(f"Lỗi kết nối đến mail.tm: {e}")
        return None

def stard():
    Domains = domains()
    if Domains is None:
        return 0
    print(f'Đã gét Domain : {Domains}')
    time.sleep(3)
    try:
        random_Domain = random.choice(Domain)
        random_word = random.choice(passw)
        random_number = random.randint(156, 168953)    
        DOMAINUSER = f'{random_Domain}{random_number}'
        PASSUSER = f'{random_word}{random_number}'
        headers = {'Referer': 'https://mail.tm/'}
        json_data = {'address': f'{DOMAINUSER}@{Domains}', 'password': f'{PASSUSER}'}
        response = requests.post('https://api.mail.tm/accounts', headers=headers, json=json_data)
        response_data = response.json()
        if 'address' and 'id' in response_data:
            DOMAINUSER = str(DOMAINUSER + '@' + Domains)
            return DOMAINUSER, PASSUSER
        else:
            print("ID not found in response.")
            return 0
    except Exception as e:
        print(f"Lỗi trong stard: {e}")
        return 0

def mxn(emailtm, emailtmpass):
    base_url = "https://api.mail.tm"
    token_url = f"{base_url}/token"
    headers = {"Content-Type": "application/json"}
    payload = {"address": emailtm, "password": emailtmpass}
    try:
        response = requests.post(token_url, headers=headers, data=json.dumps(payload), timeout=10)
        if response.status_code in [200, 201]:
            token_data = response.json()
            token = token_data.get("token")
            print(f"Token nhận được: {token}")
        else:
            print(f"Lỗi khi lấy token: {response.status_code} - {response.text}")
            return 0

        messages_url = f"{base_url}/messages?page=1"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        response = requests.get(messages_url, headers=headers, timeout=10)
        if response.status_code == 200:
            messages_data = response.json()
            messages = messages_data.get("hydra:member", [])
            if messages:
                latest_message = messages[0]
                message_id = latest_message["id"]
                message_url = f"{base_url}/messages/{message_id}"
                message_response = requests.get(message_url, headers=headers, timeout=10)
                if message_response.status_code == 200:
                    message_details = message_response.json()
                    message_text = message_details.get("text", "")
                    match = re.search(r'\b\d{6}\b', message_text)
                    if match:
                        verification_code = match.group(0)
                        print(f"Mã xác minh nhận được: {verification_code}")
                        return verification_code
                    else:
                        print("Không tìm thấy mã xác minh trong nội dung tin nhắn.")
                        return 0
                else:
                    print(f"Lỗi khi lấy chi tiết tin nhắn: {message_response.status_code} - {message_response.text}")
                    return 0
            else:
                print("Không có tin nhắn nào. Đang chờ...")
                return 0
        else:
            print(f"Lỗi khi lấy danh sách tin nhắn: {response.status_code} - {response.text}")
            return 0
    except Exception as e:
        print(f"Lỗi trong mxn: {e}")
        return 0

def get_ip_with_requests(proxies, use_proxy, thread_id):
    """Lấy IP bằng requests với nhiều dịch vụ dự phòng."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
    }
    proxy_dict = None
    if use_proxy and proxies:
        proxy = proxies[thread_id % len(proxies)]
        host, port, user, password = proxy.split(":")
        proxy_url = f"http://{user}:{password}@{host}:{port}"
        proxy_dict = {
            "http": proxy_url,
            "https": proxy_url,
        }
        print(f"Luồng {thread_id}: Sử dụng proxy {proxy_url} để lấy IP")

    services = ["https://api.ipify.org", "https://ifconfig.me/ip", "https://ipinfo.io/ip"]
    for service in services:
        for attempt in range(3):
            try:
                response = requests.get(service, headers=headers, proxies=proxy_dict, timeout=10)
                if response.status_code == 200:
                    ip_address = response.text.strip()
                    print(f"Luồng {thread_id}: IP lấy được từ {service} - {ip_address}")
                    return ip_address
                else:
                    print(f"Luồng {thread_id}: Lỗi lấy IP từ {service} (lần {attempt + 1}): {response.status_code}")
            except Exception as e:
                print(f"Luồng {thread_id}: Lỗi lấy IP từ {service} (lần {attempt + 1}): {e}")
            time.sleep(2)  # Chờ trước khi thử lại
    print(f"Luồng {thread_id}: Không thể lấy IP từ bất kỳ dịch vụ nào")
    return "Không lấy được IP"

def update_display(proxies, use_proxy, shared_data, total_threads, total_accounts, accounts_created, lock, wait_time, barrier):
    # Lưu trữ IP tạm thời
    ip_cache = {}  # Dictionary để lưu IP cho từng luồng
    waiting = False  # Trạng thái chờ đồng bộ
    wait_start = 0  # Thời điểm bắt đầu chờ

    while accounts_created[0] < total_accounts or any(data.get('status') == 'Running' for data in shared_data.values()):
        with lock:
            print("\033c", end="")  # Xóa console
            print(f"| Tổng số luồng chạy: {total_threads:2d} | Số acc cần reg: {total_accounts:3d} | Tổng số tài khoản đã tạo: {accounts_created[0]}/{total_accounts} |")
            print("-" * 130)
            print(f"| Số thứ tự luồng  |   IP của luồng    |  Thông báo mã xác nhận email |   Tình trạng     | THỜI GIAN DỪNG ĐỂ ĐỔI VPN (giây) |")
            print("-" * 130)
            
            # Kiểm tra trạng thái chờ
            if not use_proxy:
                waiting = all(data.get('status') in ['Thành công', 'DIE'] for data in shared_data.values())
                if waiting and barrier.n_waiting > 0:  # Đang trong giai đoạn chờ đồng bộ
                    if wait_start == 0:
                        wait_start = time.time()
                    elapsed = time.time() - wait_start
                    remaining = max(0, wait_time - int(elapsed))
                else:
                    wait_start = 0
                    remaining = wait_time
            else:
                remaining = 0

            for i in range(total_threads):
                data = shared_data.get(i, {})
                # Lấy IP trực tiếp nếu chưa có trong cache
                if i not in ip_cache:
                    ip_cache[i] = get_ip_with_requests(proxies, use_proxy, i)
                ip = ip_cache[i]
                email_status = data.get('email_status', 'Chờ xử lý')
                status = data.get('status', 'Running')

                # Hiển thị thời gian đếm ngược nếu đang chờ
                remaining_time = "N/A"
                if not use_proxy:
                    if waiting and barrier.n_waiting > 0:
                        remaining_time = str(remaining) if remaining > 0 else "0"
                    else:
                        remaining_time = str(wait_time)

                print(f"| Luồng {i + 1:<15} | {ip:<15} | {email_status:<30} | {status:<15} | {remaining_time:<30} |")
            print("-" * 130)
        time.sleep(1)  # Cập nhật mỗi giây

def task(thread_id, proxies, use_proxy, wait_time, total_accounts, accounts_created, shared_data, lock, barrier):
    print(f"Luồng {thread_id}: Bắt đầu")
    while accounts_created[0] < total_accounts:
        shared_data[thread_id] = {'email_status': 'Chờ xử lý', 'status': 'Running'}
        driver = None
        try:
            # Cấu hình Chrome options
            options = ChromeOptions()
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            options.add_argument("--window-size=300,1000")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-logging")
            options.add_argument('--log-level=3')
            options.add_argument('--silent')
            options.add_argument('--enable-unsafe-swiftshader')

            # Xử lý proxy cho Selenium
            if use_proxy and proxies:
                proxy = proxies[thread_id % len(proxies)]
                host, port, user, password = proxy.split(":")
                proxy_url = f"http://{user}:{password}@{host}:{port}"
                options.add_argument(f'--proxy-server={proxy_url}')
                print(f"Luồng {thread_id}: Sử dụng proxy {proxy_url} cho Selenium")

            # Khởi động Chrome với options đã cấu hình
            driver = webdriver.Chrome(options=options)
            print(f"Luồng {thread_id}: Đã khởi động Chrome")

            # Tạo tài khoản email
            taoenail = stard()
            if taoenail == 0:
                raise Exception("Không thể tạo email tạm thời")
            emailtm, emailtmpass = taoenail
            

            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.get("https://www.tiktok.com/signup")
            time.sleep(3)
            driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/div[1]/div/div[2]/div[2]').click()

            # Chọn ngày sinh ngẫu nhiên
            time.sleep(3)
            driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/form/div[2]/div[1]/div[1]').click()
            random_month_index = random.randint(0, 11)
            month_option_id = f"Month-options-item-{random_month_index}"
            driver.find_element(By.ID, month_option_id).click()

            driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/form/div[2]/div[2]/div[1]').click()
            random_day_index = random.randint(0, 30)
            day_option_id = f"Day-options-item-{random_day_index}"
            driver.find_element(By.ID, day_option_id).click()

            driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/form/div[2]/div[3]/div[1]').click()
            random_year_index = random.randint(20, 57)  # 2004 = 20, 1967 = 57
            year_option_id = f"Year-options-item-{random_year_index}"
            year_element = driver.find_element(By.ID, year_option_id)
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", year_element)
            year_element.click()
            time.sleep(2)

            # Chọn đăng ký bằng email
            driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/form/div[4]/a').click()
            time.sleep(2)
            driver.find_element(By.NAME, 'email').send_keys(f'{emailtm}')
            driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/form/div[6]/div/input').send_keys(f'{passtiktok}')
            time.sleep(2)

            # Gửi mã xác nhận
            send_code_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-e2e='send-code-button']"))
            )
            send_code_btn.click()
            send_code_btn.click()

            # Lấy mã xác nhận với thử lại
            time.sleep(20)  # Chờ ban đầu cho email
            code = mxn(emailtm, emailtmpass)
            attempt = 0
            max_attempts = 5
            while not code and attempt < max_attempts:
                print(f"Luồng {thread_id}: Thử lại lấy mã lần {attempt + 1}...")
                time.sleep(5)
                code = mxn(emailtm, emailtmpass)
                attempt += 1
            if code:
                shared_data[thread_id]['email_status'] = 'Đã nhận mã'
                print(f"Luồng {thread_id}: Đã cập nhật trạng thái email thành 'Đã nhận mã'")
            else:
                raise Exception(f"Luồng {thread_id}: Không nhận được mã xác minh sau {max_attempts} lần thử")

            # Nhập mã xác nhận và gửi
            driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/form/div[7]/div[1]/div/input').send_keys(f'{code}')
            time.sleep(2)
            send_code_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "html/body/div[1]/div/div[2]/div[1]/form/button"))
            )
            send_code_btn.click()

            # Bước cuối
            driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/form/div[3]').click()
            with open('TK.txt', "a") as email:
                email.write(f"{emailtm}|{emailtmpass} | password: {passtiktok} \n")
            shared_data[thread_id]['status'] = 'Thành công'
            time.sleep(5)

            # Tăng bộ đếm tài khoản đã tạo
            with lock:
                accounts_created[0] += 1

            driver.quit()

        except Exception as e:
            shared_data[thread_id]['status'] = 'DIE'
            print(f"Luồng {thread_id}: Lỗi - {e}")
            if driver is not None:
                driver.quit()

        # Đồng bộ các luồng bằng Barrier
        if not use_proxy:
            barrier.wait()  # Chờ tất cả các luồng hoàn thành
            if thread_id == 0:  # Chỉ luồng đầu tiên thực hiện chờ
                print(f"Tất cả luồng đang dừng {wait_time} giây để đổi VPN...")
                time.sleep(wait_time)
            barrier.wait()  # Đảm bảo tất cả luồng cùng tiếp tục sau khi chờ

def main():
    global passtiktok
    print("Bắt đầu main")
    total_accounts = int(input('NHẬP TỔNG SỐ ACC MUỐN REG: '))
    MAX_THREADS = int(input('SỐ LUỒNG MUỐN CHẠY: '))
    passtiktok = input('NHẬP PASS TIKTOK:')
    print(f"Starting {MAX_THREADS} threads to create {total_accounts} accounts... at {time.strftime('%H:%M:%S %Z on %Y-%m-%d')}")

    use_proxy = input("CHẠY PROXY KO (1 = No, 2 = Yes tạo tệp tên [proxy.txt] định dạng host:port:user:password").strip()
    use_proxy = True if use_proxy == "2" else False

    wait_time = 0
    if not use_proxy:
        wait_time = int(input("THỜI GIAN DỪNG ĐỂ ĐỔI VPN (giây): ").strip())

    proxies = []
    if use_proxy:
        try:
            with open("proxy.txt", "r") as f:
                proxies = [line.strip() for line in f if line.strip()]
            if not proxies:
                print("Không tìm thấy proxy trong proxy.txt. Sẽ chạy mà không dùng proxy.")
                use_proxy = False
        except FileNotFoundError:
            print("File proxy.txt không tồn tại. Sẽ chạy mà không dùng proxy.")
            use_proxy = False

    # Sử dụng threading để quản lý dữ liệu
    shared_data = {}
    accounts_created = [0]  # Sử dụng list để lưu biến đếm
    lock = threading.Lock()
    barrier = threading.Barrier(MAX_THREADS)  # Barrier để đồng bộ các luồng

    display_thread = threading.Thread(target=update_display, args=(proxies, use_proxy, shared_data, MAX_THREADS, total_accounts, accounts_created, lock, wait_time, barrier), daemon=True)
    display_thread.start()

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(task, i, proxies, use_proxy, wait_time, total_accounts, accounts_created, shared_data, lock, barrier) for i in range(MAX_THREADS)]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"Lỗi trong future: {e}")

    print(f"Hoàn thành tạo {accounts_created[0]} tài khoản! at {time.strftime('%H:%M:%S %Z on %Y-%m-%d')}")

if __name__ == "__main__":
    main()