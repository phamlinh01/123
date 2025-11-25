import os
import sys
import time

def install_and_import(package, import_name=None):
    import importlib
    try:
        return importlib.import_module(import_name or package)
    except ImportError:
        print(f"Thiếu module {package}, đang cài đặt...")
        os.system(f"{sys.executable} -m pip install {package}")
        return importlib.import_module(import_name or package)

requests = install_and_import("requests")
pystyle = install_and_import("pystyle")

from pystyle import Write, Colors, Colorate

API_LIKE = "https://huutri.id.vn/api/freefire/like?uid={}"
API_INFO = "https://huutri.id.vn/api/freefire/info?uid={}"

def log_success(msg):
    Write.Print(f"{msg}\n", Colors.green, interval=0.01)

def log_error(msg):
    Write.Print(f"{msg}\n", Colors.red, interval=0.01)

def log_info(msg):
    Write.Print(f"{msg}\n", Colors.cyan, interval=0.01)

def tang_like(uid):
    try:
        url = API_LIKE.format(uid)
        response = requests.get(url)
        data = response.json()

        if "likes" in data:
            before = data["likes"]["before"]
            after = data["likes"]["after"]
            added = data["likes"]["added_by_api"]

            log_info(f"\nUID: {uid}")
            log_success(f"Tên Nhân Vật: {data.get('nickname', 'Không rõ')}")
            log_info(f"Like Trước Khi Tăng: {before}")
            log_info(f"Like Sau Khi Tăng: {after}")
            log_success(f"Đã Tăng: {added}")
        else:
            log_error("Lỗi server!")
    except Exception as e:
        log_error(f"Lỗi: {e}")

def lay_thong_tin(uid):
    try:
        url = API_INFO.format(uid)
        response = requests.get(url)
        data = response.json()

        basic = data["basicInfo"]
        credit = data.get("creditScoreInfo", {})
        pet = data.get("petInfo", {})
        social = data.get("socialInfo", {})

        log_success("\n===== THÔNG TIN TÀI KHOẢN FREE FIRE =====")
        log_info(f"UID: {data.get('uid')}")
        log_info(f"Tên Nhân Vật: {basic.get('nickname')}")
        log_info(f"Cấp Độ: {basic.get('level')}")
        log_info(f"Kinh Nghiệm: {basic.get('exp')}")
        log_info(f"Huy Hiệu: {basic.get('badgeCnt')} cái")
        log_info(f"Like: {basic.get('liked')}")
        log_info(f"Rank: {basic.get('rank')} | Điểm Rank: {basic.get('rankingPoints')}")
        log_info(f"Rank CS: {basic.get('csRank')} | Điểm CS: {basic.get('csRankingPoints')}")
        log_info(f"Phiên Bản: {basic.get('releaseVersion')}")
        log_info(f"Vùng: {basic.get('region')}")

        if credit:
            log_success("===== CREDIT SCORE =====")
            log_info(f"Điểm Uy Tín: {credit.get('creditScore')}")
            log_info(f"Tình Trạng: {credit.get('rewardState')}")

        if pet:
            log_success("===== PET =====")
            log_info(f"Pet ID: {pet.get('id')}")
            log_info(f"Cấp Độ Pet: {pet.get('level')}")
            log_info(f"EXP Pet: {pet.get('exp')}")

        if social:
            log_success("===== SOCIAL =====")
            log_info(f"Ngôn Ngữ: {social.get('language')}")
            log_info(f"Chữ Ký: {social.get('signature')}")

        log_success("===== HOÀN TẤT =====")

    except Exception as e:
        log_error(f"Lỗi: {e}")

def menu():
    while True:
        banner = """
███████╗██████╗░███████╗███████╗███████╗██╗██████╗░███████╗
██╔════╝██╔══██╗██╔════╝██╔════╝██╔════╝██║██╔══██╗██╔════╝
█████╗░░██████╔╝█████╗░░█████╗░░█████╗░░██║██████╔╝█████╗░░
██╔══╝░░██╔══██╗██╔══╝░░██╔══╝░░██╔══╝░░██║██╔══██╗██╔══╝░░
██║░░░░░██║░░██║███████╗███████╗██║░░░░░██║██║░░██║███████╗
╚═╝░░░░░╚═╝░░╚═╝╚══════╝╚══════╝╚═╝░░░░░╚═╝╚═╝░░╚═╝╚══════╝
"""
        print(Colorate.Vertical(Colors.purple_to_blue, banner))

        Write.Print("1. Tăng Like Free Fire\n", Colors.green, interval=0.01)
        Write.Print("2. Lấy Thông Tin Tài Khoản Free Fire\n", Colors.cyan, interval=0.01)
        Write.Print("0. Thoát\n", Colors.red, interval=0.01)

        choice = input("\nChọn Chức Năng: ")

        if choice == "1":
            n = int(input("Bạn Muốn Nhập Mấy UID?: "))
            uids = [input(f"Nhập UID Thứ {i+1}: ") for i in range(n)]
            auto = input("Bạn Có Muốn Treo Tự Tăng Like Không (24h/lần) - (y/n): ").lower()

            if auto == "y":
                while True:
                    for uid in uids:
                        tang_like(uid)
                    log_info("Đang treo auto tăng like... (chờ 24h)")
                    time.sleep(24 * 3600)
            else:
                for uid in uids:
                    tang_like(uid)

        elif choice == "2":
            uid = input("Nhập UID: ")
            lay_thong_tin(uid)

        elif choice == "0":
            log_info("Thoát chương trình.")
            break
        else:
            log_error("Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    menu()
