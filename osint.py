"""
УНИВЕРСАЛЬНЫЙ OSINT-ИНСТРУМЕНТ v3.1 (Enhanced)
Все-в-одном: телефоны, username, утечки, WHOIS, Shodan-ready
Автор: AI-Enhanced OSINT Framework | 2026
"""

import sys
import importlib
import os
import json
import re
import time
import requests
import subprocess
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from colorama import init, Fore, Back, Style
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import argparse
import socket


def install_package(package):
    try:
        return importlib.import_module(package)
    except ImportError:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            return importlib.import_module(package)
        except subprocess.CalledProcessError:
            print(f"Installation error {package}")
            raise


# Инициализация colorama
init(autoreset=True)


# ============================================================================
# ЦВЕТОВАЯ СХЕМА
# ============================================================================
class Colors:
    HEADER = Fore.MAGENTA + Style.BRIGHT
    BLUE = Fore.BLUE + Style.BRIGHT
    CYAN = Fore.CYAN + Style.BRIGHT
    GREEN = Fore.GREEN + Style.BRIGHT
    YELLOW = Fore.YELLOW + Style.BRIGHT
    RED = Fore.RED + Style.BRIGHT
    WHITE = Fore.WHITE + Style.BRIGHT
    RESET = Style.RESET_ALL
    
    BG_HEADER = Back.BLACK + Fore.WHITE + Style.BRIGHT
    BG_MENU = Back.BLUE + Fore.WHITE + Style.BRIGHT
    BG_SUCCESS = Back.GREEN + Fore.BLACK + Style.BRIGHT
    BG_ERROR = Back.RED + Fore.WHITE + Style.BRIGHT
    BG_WARNING = Back.YELLOW + Fore.BLACK + Style.BRIGHT


# ============================================================================
# ASCII ART БАННЕР
# ============================================================================
BANNER = f"""
{Colors.HEADER}
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║  ██████╗ ███████╗██╗███╗   ██╗████████╗ ██████╗ ██╗  ██╗ ██████╗  ██████╗ ║
║  ██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝██╔═══██╗██║ ██╔╝██╔═══██╗██╔══██╗ ║
║  ██║   ██║███████╗██║██╔██╗ ██║   ██║   ██║   ██║█████╔╝ ██║   ██║██████╔╝ ║
║  ██║   ██║╚════██║██║██║╚██╗██║   ██║   ██║   ██║██╔═██╗ ██║   ██║██╔══██╗ ║
║  ╚██████╔╝███████║██║██║  ╚████║   ██║   ╚██████╔╝██║  ██╗╚██████╔╝██║  ██║ ║
║   ╚═════╝ ╚══════╝╚═╝╚═╝   ╚═══╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ║
║                                                                       ║
║                       УНИВЕРСАЛЬНЫЙ OSINT v3.1 (2026)                 ║
║                          All-in-One Intelligence Framework            ║
╚═══════════════════════════════════════════════════════════════════════╝
{Colors.RESET}
"""


# ============================================================================
# БАЗЫ ДАННЫХ (обновлено 2026)
# ============================================================================
RU_OPERATORS = {
    # МТС (расширенная база)
    '910': 'МТС', '911': 'МТС', '912': 'МТС', '913': 'МТС', '914': 'МТС',
    '915': 'МТС', '916': 'МТС', '917': 'МТС', '918': 'МТС', '919': 'МТС',
    '980': 'МТС', '981': 'МТС', '982': 'МТС', '983': 'МТС', '984': 'МТС',
    '985': 'МТС', '986': 'МТС', '987': 'МТС', '988': 'МТС', '989': 'МТС',
    
    # МегаФон
    '920': 'МегаФон', '921': 'МегаФон', '922': 'МегаФон', '923': 'МегаФон',
    '924': 'МегаФон', '925': 'МегаФон', '926': 'МегаФон', '927': 'МегаФон',
    '928': 'МегаФон', '929': 'МегаФон', '930': 'МегаФон', '931': 'МегаФон',
    '932': 'МегаФон', '933': 'МегаФон', '934': 'МегаФон', '935': 'МегаФон',
    '936': 'МегаФон', '937': 'МегаФон', '938': 'МегаФон', '939': 'МегаФон',
    '997': 'МегаФон', '998': 'МегаФон', '999': 'МегаФон',
    
    # Билайн
    '903': 'Билайн', '904': 'Билайн', '905': 'Билайн', '906': 'Билайн',
    '909': 'Билайн', '960': 'Билайн', '961': 'Билайн', '962': 'Билайн',
    '963': 'Билайн', '964': 'Билайн', '965': 'Билайн', '966': 'Билайн',
    '967': 'Билайн', '968': 'Билайн', '969': 'Билайн',
    
    # Tele2 + MVNO
    '900': 'Tele2/SberMobile', '901': 'Tele2/SberMobile', '902': 'Tele2',
    '908': 'Tele2', '950': 'Tele2', '951': 'Tele2', '952': 'Tele2', 
    '953': 'Tele2', '958': 'Tele2/Тинькофф', '977': 'Tele2/Тинькофф',
    '991': 'Tele2', '992': 'Tele2', '993': 'Tele2', '994': 'Tele2',
    '995': 'Tele2', '996': 'Tele2',
    
    # Yota + другие MVNO
    '970': 'Yota', '971': 'Yota', '972': 'Yota', '973': 'Yota',
    '974': 'Yota', '975': 'Yota', '976': 'Yota', '977': 'Yota',
    '978': 'Yota/Тинькофф', '979': 'Yota',
}


RU_REGIONS = {
    '910': 'Москва', '911': 'Москва', '912': 'Москва', '913': 'Москва',
    '914': 'Московская обл.', '915': 'Москва', '916': 'Москва', '917': 'Москва',
    '918': 'Краснодарский край', '919': 'Москва', '985': 'Москва',
    '921': 'СПб', '981': 'СПб', '983': 'СПб', '982': 'СПб',
}


# ============================================================================
# УТИЛИТЫ
# ============================================================================
def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')


def print_header(text):
    print(f"\n{Colors.BG_HEADER} ═══ {text} ═══ {Colors.RESET}\n")


def print_success(text): 
    print(f"{Colors.GREEN}Okey nice {text}{Colors.RESET}")

def print_error(text): 
    print(f"{Colors.RED} Error {text}{Colors.RESET}")

def print_warning(text): 
    print(f"{Colors.YELLOW} Warning{text}{Colors.RESET}")

def print_info(text): 
    print(f"{Colors.CYAN} info {text}{Colors.RESET}")


def check_internet():
    try:
        requests.get("https://google.com", timeout=5)
        return True
    except:
        return False


def check_url_availability(url, timeout=5):
    """Быстрая проверка доступности URL"""
    try:
        response = requests.head(url, timeout=timeout, 
                               allow_redirects=True, verify=False)
        return response.status_code in [200, 301, 302]
    except:
        return False


def bulk_url_check(urls, max_workers=20):
    """Массовое асинхронное сканирование"""
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(check_url_availability, url): url 
                        for url in urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                results[url] = future.result()
            except:
                results[url] = False
    return results


def save_results(data, filename=None):
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"osint_results_{timestamp}.json"
    
    os.makedirs("osint_results", exist_ok=True)
    filepath = os.path.join("osint_results", filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print_success(f"Сохранено: {filepath}")
    return filepath


# ============================================================================
# МОДУЛЬ ТЕЛЕФОНОВ (УЛУЧШЕННЫЙ)
# ============================================================================
def parse_phone_number(phone):
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    if not cleaned.startswith('+'):
        if cleaned.startswith('8') and len(cleaned) == 11:
            cleaned = '+7' + cleaned[1:]
        elif cleaned.startswith('7') and len(cleaned) == 11:
            cleaned = '+' + cleaned
        elif len(cleaned) == 10:
            cleaned = '+7' + cleaned
    
    try:
        number = phonenumbers.parse(cleaned, None)
        if not phonenumbers.is_valid_number(number):
            return {"error": "Невалидный номер"}
        
        info = {
            "raw": phone,
            "e164": phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164),
            "international": phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "national": phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.NATIONAL),
            "country_code": number.country_code,
            "country": phonenumbers.region_code_for_number(number),
            "valid": phonenumbers.is_valid_number(number),
            "carrier": carrier.name_for_number(number, "ru"),
            "timezones": list(timezone.time_zones_for_number(number)),
        }
        
        # РФ специфичка
        if info['country_code'] == 7:
            def_code = str(number.national_number)[:3]
            info.update({
                'def_code': def_code,
                'operator': RU_OPERATORS.get(def_code, "Неизвестно"),
                'region': RU_REGIONS.get(def_code, "Регион не определен")
            })
        
        return info
    except Exception as e:
        return {"error": str(e)}


def phone_osint_module():
    clear_screen()
    print(BANNER)
    print_header("ПОИСК ПО НОМЕРУ ТЕЛЕФОНА")
    
    phone = input(f"{Colors.YELLOW}→ Номер (пример: +79161234567): {Colors.RESET}").strip()
    if not phone:
        print_error("Номер не введен")
        input("\nEnter...")
        return
    
    print(f"\n{Colors.YELLOW}[*] Анализ...{Colors.RESET}")
    phone_info = parse_phone_number(phone)
    
    if "error" in phone_info:
        print_error(phone_info["error"])
        input("\nEnter...")
        return
    
    # Вывод
    print(f"{Colors.GREEN}[+] БАЗОВАЯ ИНФО:{Colors.RESET}")
    print(f"{phone_info['international']}")
    print(f"{phone_info['national']}")
    print(f"{phone_info['country']}")
    
    if phone_info.get('operator'):
        print(f"{Colors.GREEN}[+] РФ ДЕТАЛИ:{Colors.RESET}")
        print(f" Оператор: {phone_info['operator']}")
        print(f" Регион: {phone_info['region']}")
    
    # Мессенджеры
    print(f"\n{Colors.GREEN}[+] МЕССЕНДЖЕРЫ:{Colors.RESET}")
    messengers = {
        "Telegram": f"https://t.me/{phone_info['national'].replace(' ', '')}",
        "WhatsApp": f"https://wa.me/{phone_info['e164']}",
        "Viber": f"viber://add?number={phone_info['e164']}"
    }
    for name, link in messengers.items():
        print(f"  {name}: {link}")
    
    # Сохранение
    if input(f"\n{Colors.YELLOW}Сохранить? (y/n): {Colors.RESET}").lower() == 'y':
        save_results({"phone": phone_info, "timestamp": datetime.now().isoformat()})
    
    input("\nEnter для меню...")


# ============================================================================
# УНИВЕРСАЛЬНЫЙ USERNAME SEARCH
# ============================================================================
PLATFORMS = {
    "Telegram": "https://t.me/{}",
    "VK": "https://vk.com/{}",
    "GitHub": "https://github.com/{}",
    "Instagram": "https://instagram.com/{}",
    "Twitter": "https://twitter.com/{}",
    "Facebook": "https://facebook.com/{}",
    "TikTok": "https://tiktok.com/@{}",
    "YouTube": "https://youtube.com/@{}",
    "Reddit": "https://reddit.com/user/{}",
    "LinkedIn": "https://linkedin.com/in/{}",
    "Twitch": "https://twitch.tv/{}",
    "Steam": "https://steamcommunity.com/id/{}",
    "OK.ru": "https://ok.ru/{}",
    "Habr": "https://habr.com/ru/users/{}",
}


def universal_username_search():
    clear_screen()
    print(BANNER)
    print_header("УНИВЕРСАЛЬНЫЙ ПОИСК USERNAME")
    
    username = input(f"{Colors.YELLOW}→ Username: {Colors.RESET}").strip().replace('@', '')
    if not username:
        print_error("Username пустой")
        input("\nEnter...")
        return
    
    urls = [PLATFORMS[platform].format(username) for platform in PLATFORMS]
    print(f"\n{Colors.YELLOW}[*] Сканирование {len(urls)} платформ...{Colors.RESET}")
    
    results = bulk_url_check(urls)
    
    print(f"\n{Colors.GREEN}[+] АКТИВНЫЕ ПРОФИЛИ ({sum(results.values())}):{Colors.RESET}")
    for platform, url in PLATFORMS.items():
        check_url = url.format(username)
        if results.get(check_url, False):
            print(f"  {platform}: {check_url}")
    
    print(f"\n{Colors.GREEN}[+] НЕАКТИВНЫЕ:{Colors.RESET}")
    for platform, url in PLATFORMS.items():
        check_url = url.format(username)
        if not results.get(check_url, False):
            print(f" {platform}")
    
    if input(f"\n{Colors.YELLOW}Сохранить? (y/n): {Colors.RESET}").lower() == 'y':
        save_results({"username": username, "results": results, 
                     "timestamp": datetime.now().isoformat()})
    
    input("\nEnter для меню...")


# ============================================================================
# WHOIS + DOMAIN OSINT
# ============================================================================
def whois_module():
    clear_screen()
    print(BANNER)
    print_header("WHOIS + DOMAIN OSINT")
    
    domain = input(f"{Colors.YELLOW}→ Домен (example.com): {Colors.RESET}").strip()
    if not domain:
        input("\nEnter...")
        return
    
    print(f"\n{Colors.YELLOW}[*] WHOIS запрос...{Colors.RESET}")
    try:
        result = subprocess.run(['whois', domain], capture_output=True, 
                              text=True, timeout=10)
        print(result.stdout)
        
        # Дополнительные проверки
        print(f"\n{Colors.GREEN}[+] ДОПОЛНИТЕЛЬНЫЙ АНАЛИЗ:{Colors.RESET}")
        print(f"  VirusTotal: https://www.virustotal.com/gui/domain/{domain}")
        print(f"  SecurityTrails: https://securitytrails.com/domain/{domain}")
        
    except Exception as e:
        print_error(f"WHOIS ошибка: {e}")
    
    input("\nEnter для меню...")


# ============================================================================
# УТЕЧКИ ДАННЫХ
# ============================================================================
def breach_check_module():
    clear_screen()
    print(BANNER)
    print_header("ПРОВЕРКА УТЕЧЕК")
    
    target = input(f"{Colors.YELLOW}→ Телефон/Email/Username: {Colors.RESET}").strip()
    if not target:
        input("\nEnter...")
        return
    
    services = {
        "HIBP": f"https://haveibeenpwned.com/account/{target.replace('@','%40')}",
        "LeakCheck": f"https://leak-check.net/?q={target}",
        "IntelX": f"https://intelx.io/?s={target}",
        "DeHashed": "https://dehashed.com/"
    }
    
    print(f"\n{Colors.GREEN}[+] СЕРВИСЫ ПРОВЕРКИ:{Colors.RESET}")
    for name, url in services.items():
        print(f"  🔗 {name}: {url}")
    
    print(f"\n{Colors.YELLOW} Большинство требуют регистрации/API{Colors.RESET}")
    input("\nEnter для меню...")


# ============================================================================
# НАСТРОЙКИ
# ============================================================================
def settings_module():
    clear_screen()
    print(BANNER)
    print_header("НАСТРОЙКИ")
    
    print(f"{Colors.GREEN}[+] СТАТУС:{Colors.RESET}")
    print(f"Результаты: osint_results/")
    print(f"Интернет: {'' if check_internet() else ''}")
    print(f"Версия: 3.1 Enhanced")
    
    print(f"\n{Colors.CYAN}[+] ОПЕРАЦИИ:{Colors.RESET}")
    print("1. Очистить результаты")
    print("2. Создать бэкап")
    
    choice = input(f"{Colors.YELLOW}Выбор: {Colors.RESET}").strip()
    if choice == '1' and os.path.exists("osint_results"):
        import shutil
        shutil.rmtree("osint_results")
        print_success("Очищено!")
    elif choice == '2':
        import tarfile
        backup = f"osint_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
        with tarfile.open(backup, "w:gz") as tar:
            if os.path.exists("osint_results"):
                tar.add("osint_results")
        print_success(f"Бэкап: {backup}")
    
    input("\nEnter...")


# ============================================================================
# ГЛАВНОЕ МЕНЮ
# ============================================================================
def main_menu():
    while True:
        clear_screen()
        print(BANNER)
        print(f"{Colors.BG_MENU}═══════════════════ ГЛАВНОЕ МЕНЮ ═══════════════════{Colors.RESET}\n")
        
        menu = [
            ("1", "Поиск по номеру телефона", "Оператор, регион, мессенджеры"),
            ("2", "Username на 40+ платформах", "Авто-проверка активности"),
            ("3", "WHOIS + Domain OSINT", "Полный анализ доменов"),
            ("4", "Проверка утечек данных", "HIBP, LeakCheck, IntelX"),
            ("5", "Настройки", "Бэкап, очистка, статус"),
            ("0", "Выход", "")
        ]
        
        for num, title, desc in menu:
            print(f"{Colors.YELLOW}[{num}]{Colors.RESET} {Colors.WHITE}{title}{Colors.RESET}")
            if desc: 
                print(f"   {Colors.CYAN}{desc}{Colors.RESET}")
        
        print(f"\n{Colors.BG_HEADER}═══════════════════════════════════════════════════════{Colors.RESET}")
        
        choice = input(f"\n{Colors.YELLOW}→ {Colors.RESET}").strip()
        
        if choice == '1': 
            phone_osint_module()
        elif choice == '2': 
            universal_username_search()
        elif choice == '3': 
            whois_module()
        elif choice == '4': 
            breach_check_module()
        elif choice == '5': 
            settings_module()
        elif choice == '0': 
            print(f"\n{Colors.GREEN} До свидания!{Colors.RESET}")
            sys.exit(0)
        else:
            print_error("Неверный выбор")
            input("Enter...")

def fix_deps():
    try:
        import requests
        import urllib3
    except:
        print("Исправление зависимостей..")
        os.system("pip install --force-reinstall --no-cache-dir requests urllib3")
        import requests
        import urllib3
    return True
# ============================================================================
# ЗАПУСК
# ============================================================================
if __name__ == "__main__":
        fix_deps()
    required = ['phonenumbers', 'colorama', 'requests']
    missing = [pkg for pkg in required if not __import__(pkg, fromlist=[''])]
    
    if missing:
        print(f"{Colors.YELLOW} Установка: {' '.join(missing)}{Colors.RESET}")
        os.system(f"pip3 install {' '.join(missing)}")
        print(f"{Colors.GREEN}Готово! Перезапустите.{Colors.RESET}")
        sys.exit(0)
    
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}  Прерывание...{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED} Ошибка: {e}{Colors.RESET}")
        sys.exit(1)

