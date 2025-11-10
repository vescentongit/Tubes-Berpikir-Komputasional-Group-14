
import Pages as Pages
# import tesPage as Pages

def change_page(current_page):
    # main page
    if current_page == 1:
        while True:
            print(Pages.main_page())
            user_input = input("Want to change page? (y/n): ").lower()
            if user_input == "y":
                return "menu"
            
    # timer
    elif current_page == 2:
        Pages.timer()
        user_back = input('Want to go back? (y/n) : ').lower()
        if user_back == 'y':
            return 'menu'
        else:
            return 2
    
    # alarm
    elif current_page == 3:
        Pages.alarm()
        user_back = input('Want to go back? (y/n) : ').lower()
        if user_back == 'y':
            return 'menu'
        else:
            return 3
        # return 'menu'
    
    # weather
    elif current_page == 4:
        Pages.weather()
        user_back = input('Want to go back? (y/n) : ').lower()
        if user_back == 'y':
            return 'menu'
        else:
            return 4
        # return 'menu'
    
    # calculator
    elif current_page == 5:
        Pages.calculator()
        user_back = input('Want to go back? (y/n) : ').lower()
        if user_back == 'y':
            return 'menu'
        else:
            return 5
        # return 'menu'
    
    # settings
    elif current_page == 6:
        result = Pages.settings()
        if result == 'menu':
            return 'menu'
        else:
            user_input = input('Go back to menu? (y/n) : ')
            if user_input == 'y':
                return 'menu'
            else:
                return 6
    
    elif current_page == "menu":
        print(Pages.menu())
        try:
            user_page_input = input("Page number (q/quit to quit): ").lower()
            # main
            if user_page_input in ['0', 'quit','q']:
                return 'quit'
            elif user_page_input == '1':
                return 1
            # timer
            elif user_page_input == '2':
                return 2
            # alarm
            elif user_page_input == '3':
                return 3
            # weather
            elif user_page_input == '4':
                return 4
            # calculator
            elif user_page_input == '5':
                return 5
            # settings
            elif user_page_input == '6':
                return 6
            else:
                print("Invalid page number. Try again.")
                return "menu"
        except ValueError:
            print("Please enter a valid number.")
            return "menu"

    


def main():
    """Main program loop."""
    page = 1
    while True:
        page = change_page(page)
        if page == 'quit':
            print('\n...Shutting down...')
            break
        


if __name__ == "__main__":
    main()