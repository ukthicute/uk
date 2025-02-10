import os
import subprocess
import sys
import urllib.request
import tarfile

# Định nghĩa URL tải MSYS2
MSYS2_URL = 'https://repo.msys2.org/distrib/x86_64/msys2-base-x86_64-20210725.tar.xz'
MSYS2_DIR = 'msys2'

# Hàm tải MSYS2
def download_msys2():
    if not os.path.exists(MSYS2_DIR):
        print("Đang tải MSYS2...")
        urllib.request.urlretrieve(MSYS2_URL, 'msys2-base.tar.xz')
    else:
        print("MSYS2 đã được tải sẵn.")

# Hàm giải nén MSYS2
def extract_msys2():
    if not os.path.exists(MSYS2_DIR):
        print("Đang giải nén MSYS2...")
        with tarfile.open('msys2-base.tar.xz', 'r:xz') as tar:
            tar.extractall()
    else:
        print("MSYS2 đã được giải nén.")

# Hàm cài đặt MinGW-w64 qua MSYS2
def install_mingw():
    if os.name == 'nt':
        print("Cài đặt MinGW-w64...")
        # Tạo môi trường shell MSYS2 để cài đặt GCC
        msys2_shell = os.path.join(MSYS2_DIR, 'usr', 'bin', 'bash.exe')
        if not os.path.exists(msys2_shell):
            print("Không tìm thấy shell MSYS2.")
            return

        # Cài MinGW-w64 thông qua pacman
        subprocess.run([msys2_shell, '--noprofile', '--norc', 'pacman', '-S', '--noconfirm', 'mingw-w64-x86_64-gcc'])
    else:
        print("Chạy trên Windows!")

# Hàm biên dịch file C
def compile_c_code():
    # Giả sử bạn có file `tqh.c` để biên dịch
    if os.path.exists("tqh.c"):
        print("Đang biên dịch tqh.c...")
        subprocess.run(["gcc", "tqh.c", "-o", "tqh.exe"])
    else:
        print("Không tìm thấy file tqh.c để biên dịch.")

if __name__ == '__main__':
    download_msys2()
    extract_msys2()
    install_mingw()
    compile_c_code()
    print("Cài đặt và biên dịch hoàn tất!".encode('utf-8').decode('cp1252'))
