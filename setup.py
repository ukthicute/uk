import os
import subprocess
import sys

# Tải MSYS2 từ trang chính thức
def download_msys2():
    url = 'https://repo.msys2.org/distrib/x86_64/msys2-base-x86_64-20210725.tar.xz'
    file_path = 'msys2-base.tar.xz'

    # Tải xuống MSYS2
    os.system(f"curl -L -o {file_path} {url}")
    return file_path

# Giải nén MSYS2
def extract_msys2(file_path):
    os.system(f"tar -xvf {file_path}")

# Cài đặt MinGW-w64
def install_mingw():
    os.system("pacman -S mingw-w64-x86_64-gcc")

if __name__ == '__main__':
    # Tải MSYS2 và giải nén
    file_path = download_msys2()
    extract_msys2(file_path)

    # Cài MinGW-w64
    install_mingw()
    print("GCC đã được cài đặt thành công thông qua MSYS2.")
