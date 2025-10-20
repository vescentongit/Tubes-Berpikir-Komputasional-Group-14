import time
current = time.localtime()
day = time.strftime("%d", current)
month = time.strftime("%m", current)
hour = time.strftime("%H", current)
minute = time.strftime("%M", current)
meanTime = time.strftime('%Z', current)


print(day, month, hour, minute, meanTime)