import os, re


def start_python_module(module_name):
    # 查看所有運行的python程序
    python_full = os.popen("wmic process where name='rtsp-simple-server.exe' list full").readlines()
    # 正則查找python程序是否在已運行的python程序中
    com = re.compile(module_name)
    ret = com.search(''.join(python_full))
    # 發現程序未運行，執行啟動命令
    if not ret:
        os.popen("rtsp-simple-server.exe")
        print("python 程序啟動完成")
    # 發現程序已經在運行中，不執行啟動命令
    else:
        print("python 程序已啟動")


if __name__ == '__main__':
    # python程序名
    module_name = 'rtsp-simple-server.exe'
    start_python_module(module_name)
