import pygame
import time
import threading
import requests
import winsound
import dotenv
import os
from datetime import datetime
dotenv.load_dotenv()

# Konfigurasi variabel konstan
WIDTH, HEIGHT = 800, 600
FPS = 60
API_KEY = os.getenv('WEATHER_API_KEY')
logo = pygame.image.load('TuBes_Berkom_2025/assets/watch.png')

# Colors
BG_COLOR = (15, 23, 42) # Blue
CARD_COLOR = (30, 41, 59)
ACCENT_COLOR = (59, 130, 246)
TEXT_COLOR = (248, 250, 252)
SECONDARY_TEXT = (148, 163, 184)
BUTTON_HOVER = (37, 99, 235)
SUCCESS_COLOR = (34, 197, 94)
ERROR_COLOR = (239, 68, 68)

# Inisiasi pygame
pygame.init()
pygame.display.set_icon(logo)

# Fonts
def get_font(size):
    return pygame.font.Font('TuBes_Berkom_2025/assets/Poppins-SemiBold.ttf', size)

FONT_TITLE = get_font(64)
FONT_LARGE = get_font(48)
FONT_MEDIUM = get_font(36)
FONT_SMALL = get_font(24)
FONT_TINY = get_font(18)

# Global variables
globalDefaultLocation = 'Bandung'
defaultUnit = 'Metric' 
active_timers = []
active_alarms = []


# UI handlers
class Button:
    def __init__(self, x, y, width, height, text, color=ACCENT_COLOR, action=None, page=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.action = action
        self.page = page
        self.hover = False
        
    def draw(self, screen):
        color = BUTTON_HOVER if self.hover else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (0,0,0,50), (self.rect.x+2, self.rect.y+4, self.rect.width, self.rect.height), border_radius=8)
        text_surface = FONT_TINY.render(self.text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class InputBox:
    def __init__(self, x, y, width, height, placeholder=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ''
        self.placeholder = placeholder
        self.active = False
        self.cursor_timer = 0
        
    def draw(self, screen):
        bg_color = (40, 51, 69) if self.active else CARD_COLOR
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=4)
        border_color = ACCENT_COLOR if self.active else SECONDARY_TEXT
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=4)
        
        display_text = self.text if self.text else self.placeholder
        text_color = TEXT_COLOR if self.text else SECONDARY_TEXT
        text_surface = FONT_TINY.render(display_text, True, text_color)
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))
        
        if self.active:
            self.cursor_timer = (self.cursor_timer + 1) % 60
            if self.cursor_timer < 30:
                tw = text_surface.get_width() if self.text else 0
                pygame.draw.line(screen, TEXT_COLOR, (self.rect.x + 10 + tw, self.rect.y + 8), 
                                (self.rect.x + 10 + tw, self.rect.y + 32), 2)
    
    def handle_text_input(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.key == pygame.K_RETURN:
            return True
        elif event.unicode.isprintable() and len(self.text) < 25:
            self.text += event.unicode
        return False

# Main App Handler
class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Simple Smartwatch")
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_page = 'menu'
        self.message = ''
        self.message_color = SUCCESS_COLOR
        self.message_timer = 0
        self.setup_ui()

    def setup_ui(self):
        """Initialize all persistent UI components once."""
        self.back_btn = Button(WIDTH - 120, 20, 100, 40, "Back")
        
        # Menu Page
        self.menu_btns = []
        menu_items = [("Timer", 'timer'), ("Alarm", 'alarm'), ("Weather", 'weather'), 
                        ("Calculator", 'calculator'), ("Settings", 'settings')]
        
        start_y = 250 
        for i, (txt, pg) in enumerate(menu_items):
            self.menu_btns.append(Button(WIDTH // 2 - 150, start_y + i * 60, 300, 45, txt, page=pg))

        # Timer Page
        self.timer_in = InputBox(WIDTH // 2 - 150, 150, 300, 40, "HH:MM:SS")
        self.timer_btn = Button(WIDTH // 2 - 75, 220, 150, 50, "Start Timer", action='start_timer')

        # Alarm Page
        self.alarm_name_in = InputBox(WIDTH // 2 - 150, 120, 300, 40, "Alarm Name")
        self.alarm_time_in = InputBox(WIDTH // 2 - 150, 180, 300, 40, "HH:MM")
        self.alarm_btn = Button(WIDTH // 2 - 75, 250, 150, 50, "Set Alarm", action='set_alarm')

        # Weather Page
        self.weather_in = InputBox(WIDTH // 2 - 150, 150, 300, 40, f"City (empty = {globalDefaultLocation})")
        self.weather_btn = Button(WIDTH // 2 - 75, 220, 150, 50, "Get Weather", action='weather')

        # Calculator Page
        self.calc_in = InputBox(WIDTH // 2 - 200, 150, 400, 40, "Expression (e.g. 5*5)")
        self.calc_btn = Button(WIDTH // 2 - 75, 220, 150, 50, "Calculate", action='calc')

        # Settings Page
        self.settings_loc_in = InputBox(50, 220, 300, 40, f"Enter new location...")
        self.settings_save_btn = Button(370, 220, 100, 40, "Save", action='save_loc')
        self.settings_unit_btn = Button(50, 290, 300, 50, "Toggle Unit", action='toggle_unit')

    # messaging handler
    def show_message(self, msg, duration=3, is_error=False):
        self.message = msg
        self.message_color = ERROR_COLOR if is_error else SUCCESS_COLOR
        self.message_timer = duration * FPS

    # logic action handler
    def handle_action(self, action):
        if action == 'start_timer':
            self.logic_timer(self.timer_in.text)
        elif action == 'set_alarm':
            self.logic_alarm(self.alarm_name_in.text, self.alarm_time_in.text)
        elif action == 'weather':
            self.logic_weather(self.weather_in.text)
        elif action == 'calc':
            self.logic_calc(self.calc_in.text)
        elif action == 'save_loc':
            # location handler
            new_loc = self.settings_loc_in.text
            if new_loc.strip():
                global globalDefaultLocation
                globalDefaultLocation = new_loc
                
                self.weather_in.placeholder = f"City (empty = {globalDefaultLocation})" 
    
                self.show_message(f"Location saved: {new_loc}")
                self.settings_loc_in.text = "" # Clear after saving
            else:
                winsound.Beep(500, 200)
                self.show_message("Please enter a city", is_error=True)
                
        elif action == 'toggle_unit':
            global defaultUnit
            defaultUnit = "Imperial" if defaultUnit == "Metric" else "Metric"
            self.show_message(f"Unit: {defaultUnit}")

    def logic_timer(self, dur_str):
        try:
            parts = list(map(int, dur_str.split(':')))
            if len(parts) == 3: 
                h, m, s = parts
            elif len(parts) == 2: 
                h, m, s = 0, parts[0], parts[1]
            elif len(parts) == 1: 
                h, m, s = 0, 0, parts[0]
            else: 
                raise ValueError
            
            total = h * 3600 + m * 60 + s
            if total == 0: 
                raise ValueError
            
            active_timers.append({'end_time': time.time() + total})
            
            def timer_thread():
                time.sleep(total)
                self.show_message("Timer Done!")
                # Buzzer handler
                try:
                    for i in range(3):
                        winsound.Beep(1000, 500)
                        time.sleep(0.1)
                except: 
                    pass
            
            threading.Thread(target=timer_thread, daemon=True).start()
            self.show_message(f"Timer set: {h}h {m}m {s}s")
            self.timer_in.text = ''
        except: 
            self.show_message("Format: HH:MM:SS", is_error=True)
            winsound.Beep(500, 200)

    def logic_alarm(self, name, t_str):
        if not name or not t_str: 
            winsound.Beep(500, 200)
            return self.show_message("Fill both fields", is_error=True)
        active_alarms.append({'name': name, 'time': t_str})
        
        def run_a():
            while True:
                # Check current time against alarm time
                if datetime.now().strftime("%H:%M") == t_str:
                    self.show_message(f"ALARM: {name}!")
                    # Buzzer
                    try:
                        # Beep 5 times 
                        for i in range(5):
                            winsound.Beep(1000, 200)
                            time.sleep(0.1)
                    except: 
                        pass
                    break
                time.sleep(10) # Check every 10 seconds
                
        threading.Thread(target=run_a, daemon=True).start()
        self.show_message(f"Alarm set for {t_str}")

    def logic_weather(self, city):
        # Input cleaning
        clean_city = city.strip()
        
        # Global vs custom
        if clean_city:
            target = clean_city
            mode = "Custom"
        else:
            target = globalDefaultLocation
            mode = "Default"
            
        self.show_message(f"Fetching {mode} ({target})...")

        def api_thread():
            try:
                url = "http://api.openweathermap.org/data/2.5/weather"
                params = {'q': target, 'appid': API_KEY, 'units': defaultUnit}
                resp = requests.get(url, params=params)
                
                if resp.status_code == 200:
                    data = resp.json()
                    temp = data['main']['temp']
                    desc = data['weather'][0]['description'].title()
                    humidity = data['main']['humidity']
                    
                    # Determine unit symbol
                    u = "C" if defaultUnit == 'Metric' else "F"
                    
                    # Show result
                    self.show_message(f"{target}: {temp}°{u}, {desc}, {humidity}%")
                else: 
                    self.show_message(f"Error: City '{target}' not found", is_error=True)
            except Exception as i: 
                self.show_message("Connection Error - Check Internet", is_error=True)
                winsound.Beep(500, 200)
                print(i)
                
        threading.Thread(target=api_thread, daemon=True).start()

    def logic_calc(self, expr):
        try: 
            if any(c not in "0123456789+-*/(). " for c in expr): 
                raise ValueError
            self.show_message(f"Result: {eval(expr)}")
        except: 
            winsound.Beep(500, 200)
            self.show_message("Invalid Math", is_error=True)

    # Rendering
    def draw_menu_title(self):
        title_surf = FONT_TITLE.render("Simple Smartwatch", True, TEXT_COLOR)
        self.screen.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, 100)))
        now = datetime.now()
        date_surf = FONT_SMALL.render(f"{now.strftime('%A, %B %d')} | {now.strftime('%H:%M')}", True, ACCENT_COLOR)
        self.screen.blit(date_surf, date_surf.get_rect(center=(WIDTH//2, 160)))

    def draw_settings_content(self):
        y = 120
        # Display current values
        settings_text = [
            f"Current Location: {globalDefaultLocation}",
            f"Temperature Unit: {defaultUnit}"
        ]
        for text in settings_text:
            surface = FONT_SMALL.render(text, True, TEXT_COLOR)
            self.screen.blit(surface, (50, y))
            y += 40

    # --- Core Loop ---

    def run(self):
        while self.running:
            self.screen.fill(BG_COLOR)
            m_pos = pygame.mouse.get_pos()
            
            cur_btns, cur_inps = [], []
            
            if self.current_page == 'menu':
                self.draw_menu_title()
                cur_btns = self.menu_btns
            else:
                cur_btns.append(self.back_btn)
                head = FONT_LARGE.render(self.current_page.capitalize(), True, TEXT_COLOR)
                self.screen.blit(head, (20, 20))
                
                if self.current_page == 'timer':
                    cur_inps, cur_btns = [self.timer_in], cur_btns + [self.timer_btn]
                elif self.current_page == 'alarm':
                    cur_inps, cur_btns = [self.alarm_name_in, self.alarm_time_in], cur_btns + [self.alarm_btn]
                elif self.current_page == 'weather':
                    cur_inps, cur_btns = [self.weather_in], cur_btns + [self.weather_btn]
                elif self.current_page == 'calculator':
                    cur_inps, cur_btns = [self.calc_in], cur_btns + [self.calc_btn]
                elif self.current_page == 'settings':
                    self.draw_settings_content()
                    # Add the Location Input + Save Button + Unit Toggle
                    cur_inps = [self.settings_loc_in]
                    cur_btns = cur_btns + [self.settings_save_btn, self.settings_unit_btn]

            # Pygame Event Handlers
            for event in pygame.event.get():
                
                # Quit handler
                if event.type == pygame.QUIT: 
                    self.running = False
                
                # Mouse handling
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i in cur_inps: 
                        i.active = i.rect.collidepoint(m_pos)
                    for b in cur_btns:
                        if b.is_clicked(m_pos):
                            if b.page: 
                                winsound.Beep(100, 100)
                                self.current_page = b.page
                            elif b.text == "Back": 
                                winsound.Beep(100, 100)
                                self.current_page = 'menu'
                            elif b.action: 
                                self.handle_action(b.action)
                            
                # Key pressed handler
                if event.type == pygame.KEYDOWN:
                    for i in cur_inps:
                        if i.active and i.handle_text_input(event):
                            for b in cur_btns:
                                if b.action: self.handle_action(b.action)

            
            for b in cur_btns: 
                b.check_hover(m_pos); b.draw(self.screen)
            for i in cur_inps: 
                i.draw(self.screen)
            
            if self.message_timer > 0:
                msg_surf = FONT_TINY.render(self.message, True, TEXT_COLOR)
                bg_rect = msg_surf.get_rect(center=(WIDTH//2, HEIGHT - 50))
                bg_rect.inflate_ip(40, 20)
                pygame.draw.rect(self.screen, self.message_color, bg_rect, border_radius=10)
                self.screen.blit(msg_surf, msg_surf.get_rect(center=bg_rect.center))
                self.message_timer -= 1

            pygame.display.update()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == "__main__":
    App().run()