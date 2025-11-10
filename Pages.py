import time
import winsound
import threading
import requests

current_time = time.localtime()
globalDefaultLocation = 'Bandung'
defaultUnit = 'metric'
defaultFreq = 1000
celcius = '°C'
fahrenheit = '°F'

# Main Page (1)
def main_page():
    date = time.strftime("%d/%m", current_time)      # e.g. 09/10
    hour = time.strftime("%H.%M", current_time)      # e.g. 08.05
    day = time.strftime("%a", current_time)          # e.g. Monday

    return f""" 
|{date:^7}|
|{hour:^7}|
|{day:^7}|"""

# Timer function
def timer_function(seconds):
    for i in range(seconds, 0, -1):
        time.sleep(1)
    print('\nTime up')
    winsound.Beep(defaultFreq,1000)
    time.sleep(0.5)
    winsound.Beep(defaultFreq,1000)
    time.sleep(0.5)
    winsound.Beep(defaultFreq,1000)

# Timer (2)
def timer():
    print('---Timer---')
    user_input = input('Do you want to set a timer? (y/n) : ').lower()
    if user_input == 'y':
        inputTimer = input('Input timer (HH:MM:SS) : ')
        try:
            timerNumber = [int(inputTimer[0:2]), int(inputTimer[3:5]), int(inputTimer[6:8])]
            timerAmount = timerNumber[0] * 3600 + timerNumber[1] * 60 + timerNumber[2] * 1
            
            timer_thread = threading.Thread(target=timer_function, args =(timerAmount,), daemon=True)
            timer_thread.start()
            print('\n---Timer is running in the background.---')
        except (ValueError, TypeError,) as i:
            print(f'! {i} !')
    else:
        pass

# alarm function
def alarm_function(setName, setTarget):
    try:
        def check(fromNow):
            if fromNow[0] < 0:
                fromNow[0] += 24
            if fromNow[1] < 0:
                fromNow[0] -= 1
                fromNow[1] += 60
        
        current_time = time.localtime()
        alarm = [int(setTarget[0:2]), int(setTarget[3:5])]
        now = [int(time.strftime('%H', current_time)), int(time.strftime('%M', current_time))]
        
        fromNow = [int(alarm[0] - now[0]), int(alarm[1] - now[1])]
        check(fromNow)
        print(f'---{setName} is set {fromNow[0]} hours and {fromNow[1]} minutes from now.---')
        
        while True:
            current_time = time.localtime()
            current = time.strftime('%H:%M:%S', current_time)
            if current == setTarget + ':00':
                print(f'\a\n{setName} is ringing!')
                winsound.Beep(defaultFreq,1000)
                time.sleep(0.5)
                winsound.Beep(defaultFreq,1000)
                time.sleep(0.5)
                winsound.Beep(defaultFreq,1000)
                break
            
            time.sleep(1)
    except ValueError as i:
        print(f'! {i} !') 

# Alarm (3)
def alarm():
    print('---Alarm---')
    user_input = input('Do you want to set an alarm? (y/n) : ').lower()
    if user_input == 'y':
        setName = input("What's the name of your alarm?: ")
        setTarget = input("Set your target alarm (HH:MM) : ")
        
        # start alarm in background
        alarm_thread = threading.Thread(target=alarm_function, args=(setName, setTarget), daemon=True)
        alarm_thread.start()
        
        print(f'---{setName} is running in the background.---')
    else:
        pass

# Weather (4)
def weather():
    print('---Weather---')
    APIKey = 'c10df769389502b7bdca80f56674191e'
    user_input = input('Want to check the weather? (y/n) : ').lower()
        
    if user_input == 'y':
        defaultOrNot = int(input('Default Location /  Custom (1/2)? : '))
        if defaultOrNot == 1:
            city = globalDefaultLocation
            url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={APIKey}&units={defaultUnit}'
        elif defaultOrNot == 2:
            city = input('Which city? : ')
            url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={APIKey}&units={defaultUnit}'

        response = requests.get(url)
        data = response.json()
        # print(data)
        if response.status_code == 200:
            temperature = data['main']['temp']
            weather = data['weather'][0]['description']
            b = weather.split()
            if len(b) >= 2:
                weather = b[0].capitalize() + ' ' + b[1].capitalize()
            else:
                weather = b[0].capitalize()
            humidity = data['main']['humidity']
            if defaultUnit == 'metric':
                print(
    f"""
------------------------------
City         : {city}
Temperature  : {temperature}°C
Weather      : {weather}
Humidity     : {humidity}%
------------------------------
    """)
            elif defaultUnit == 'imperial':
                print(
    f"""
------------------------------
City         : {city}
Temperature  : {temperature}°F
Weather      : {weather}
Humidity     : {humidity}%
------------------------------
    """)
    else:
        pass

def calculator_function(exp):
    try:
        result = eval(exp)
        return result
    except (SyntaxError, ZeroDivisionError, NameError, TypeError) as i:
        return f"! {i} !"

# Calculator (5)
def calculator():
    print("\n---Calculator---")
    userInput = input('Do you want to solve an expression? (y/n) : ')
    if userInput == 'y':
        while True:
            userInput = input("Enter expression / back: ")
            if userInput.lower() == 'back':
                return
            result = calculator_function(userInput)
            print(f"---The answer is {result}---")
            
    else:
        pass
    

# Settings (6)
def settings():
    global globalDefaultLocation
    global defaultFreq
    global defaultUnit
    print('---Settings---')
    print(f"""
| Default Location   (1) |
| Alarm/Timer Sound  (2) |
| Temperature Unit   (3) |
| Back to Menu       (4) |
""")
    userInput = int(input('(1/2/3/4) : '))
    if userInput == 1:
        print(f'Current default location : {globalDefaultLocation}')
        globalDefaultLocation = input('Input your desired location : ')
        print(f'---Default location changed to {globalDefaultLocation}---')
  
    elif userInput == 2:
        print(f'Current Alarm / Timer Sound Frequency : {defaultFreq} Hz')
        newFreq = int(input('Input your desired frequency (100-32000) Hz : '))
        if newFreq > 32000 or newFreq < 100:
            print('! Please enter a valid number. !')
            return
        else:
            defaultFreq = newFreq
            print(f'---Frequency changed to {defaultFreq}---')
    
    elif userInput == 3:
        print(f'Current default unit : {defaultUnit}')
        defaultUnit = input('Input your desired unit (Imperial/Metric) : ').lower()
        if defaultUnit == 'metric':
            defaultUnit = 'metric'
            print(f'---Unit changed to {defaultUnit}---')
        elif defaultUnit == 'imperial':
            defaultUnit = 'imperial'
            print(f'---Unit changed to {defaultUnit}---')
        else:
            print('! Please enter a valid unit !')
            return
    
    elif userInput == 4:
        return 'menu'
        

def menu():
    return f"""
-----------------------------
|{'main':^7}|{'timer':^10}|{'alarm':^8}|
-----------------------------
|weather|calculator|settings|
-----------------------------
"""


if __name__ == '__main__':
    settings()
    weather()