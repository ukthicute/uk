import requests
import time
import os
from datetime import timedelta

def save_cookies_to_file(cookies):
    """Lưu cookies vào file ck.txt"""
    with open('ck.txt', 'w') as f:
        for key, value in cookies.items():
            f.write(f"{key}={value};\n")

def load_cookies_from_file():
    """Tải cookies từ file ck.txt nếu có"""
    if os.path.exists('ck.txt'):
        with open('ck.txt', 'r') as f:
            cookies = {}
            for line in f.readlines():
                if '=' in line:
                    key, value = line.strip().split("=", 1)
                    cookies[key] = value
            return cookies
    return None

def convert_seconds_to_time_format(seconds):
    """Chuyển giây thành định dạng: ngày, giờ, phút, giây"""
    delta = timedelta(seconds=seconds)
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return days, hours, minutes, seconds

def keep_alive():
    """Giữ URL sống bằng cách gửi yêu cầu liên tục"""
    # Nhập URL của website cần giữ online
    url = input("Nhập URL cần gửi yêu cầu: ")

    # Kiểm tra xem có cookie đã lưu trong file không
    saved_cookies = load_cookies_from_file()
    if saved_cookies:
        use_saved_cookies = input("Có muốn sử dụng cookie đã lưu? (y/n): ").strip().lower()
        if use_saved_cookies == 'y':
            cookies = saved_cookies
            print("Đang sử dụng cookie đã lưu.")
        else:
            cookies_input = input("Nhập cookie mới (các cặp key=value cách nhau bởi dấu chấm phẩy ';'): ")
            # Chuyển đổi chuỗi cookie thành dictionary
            cookies = {}
            for cookie in cookies_input.split(";"):
                if "=" in cookie:
                    key, value = cookie.strip().split("=", 1)
                    cookies[key] = value
            save_cookies_to_file(cookies)
            print("Cookie đã được lưu vào file.")
    else:
        cookies_input = input("Nhập cookie mới (các cặp key=value cách nhau bởi dấu chấm phẩy ';'): ")
        # Chuyển đổi chuỗi cookie thành dictionary
        cookies = {}
        for cookie in cookies_input.split(";"):
            if "=" in cookie:
                key, value = cookie.strip().split("=", 1)
                cookies[key] = value
        save_cookies_to_file(cookies)
        print("Cookie đã được lưu vào file.")

    # Nhập thời gian giữa các lần gửi yêu cầu (tính bằng giây)
    try:
        wait_time_seconds = int(input("Nhập thời gian giữa các lần request (giây): "))
    except ValueError:
        print("Vui lòng nhập một giá trị hợp lệ cho thời gian!")
        return

    # Chuyển đổi thời gian giây thành các đơn vị thời gian
    days, hours, minutes, seconds = convert_seconds_to_time_format(wait_time_seconds)
    print(f"Thời gian giữa các lần request: {days} ngày, {hours} giờ, {minutes} phút, {seconds} giây.")

    print(f"Đang giữ sống URL: {url} với cookie đã nhập. Mỗi {wait_time_seconds} giây sẽ gửi một yêu cầu.")

    # Gửi yêu cầu liên tục
    while True:
        try:
            response = requests.get(url, cookies=cookies, allow_redirects=True)
            # Lấy mã trạng thái và phản hồi
            status_code = response.status_code
            response_text = response.text[:200]  # Lấy 200 ký tự đầu tiên của phản hồi (có thể thay đổi số này)
            final_url = response.url  # Lấy URL đích sau chuyển hướng
            
            if status_code == 200:
                print(f"Yêu cầu thành công! Trạng thái: {status_code}")
                print(f"Phản hồi: {response_text}")
                print(f"URL đích sau chuyển hướng: {final_url}")
            else:
                print(f"Lỗi! Trạng thái: {status_code}")
                print(f"Phản hồi: {response_text}")
                print(f"URL đích sau chuyển hướng: {final_url}")
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi gửi yêu cầu: {e}")
            print("Không thể gửi yêu cầu. Kết thúc chương trình.")
            break
        
        # Chờ trước khi gửi yêu cầu tiếp theo
        time.sleep(wait_time_seconds)

if __name__ == "__main__":
    keep_alive()
