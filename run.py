import os
import datetime


while True:
    print()
    print("执行时间%s" % datetime.datetime.now().strftime("%Y%m%d %H:%M:%S"))
    os.system("python exchange.py")
