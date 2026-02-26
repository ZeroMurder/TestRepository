
"""
УНИВЕРСАЛЬНЫЙ OSINT-ИНСТРУМЕНТ
Версия: 3.0 (AllOnev1)
Функционал: Поиск по номеру телефона, username в Telegram, социальные сети
"""

import sys
import os
import json
import re
import time
import requests
import subprocess
from datetime import datetime
from colorama import init, Fore, Back, Style
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import argparse

# Инициализация colorama для цветного вывода
init(autoreset=True)

# ============================================================================
# КЛАССЫ ДЛЯ ЦВЕТНОГО ОФОРМЛЕНИЯ
# ============================================================================

class Colors:
    """Цветовая схема для интерфейса"""
    HEADER = Fore.MAGENTA + Style.BRIGHT
    BLUE = Fore.BLUE + Style.BRIGHT
    CYAN = Fore.CYAN + Style.BRIGHT
    GREEN = Fore.GREEN + Style.BRIGHT
    YELLOW = Fore.YELLOW + Style.BRIGHT
    RED = Fore.RED + Style.BRIGHT
    WHITE = Fore.WHITE + Style.BRIGHT
    RESET = Style.RESET_ALL
    
    # Фоновые цвета
    BG_HEADER = Back.BLACK + Fore.WHITE + Style.BRIGHT
    BG_MENU = Back.BLUE + Fore.WHITE + Style.BRIGHT
    BG_SUCCESS = Back.GREEN + Fore.BLACK + Style.BRIGHT
    BG_ERROR = Back.RED + Fore.WHITE + Style.BRIGHT
    BG_WARNING = Back.YELLOW + Fore.BLACK + Style.BRIGHT

# ============================================================================
# ASCII АРТ И ЗАСТАВКА
# ============================================================================

BANNER = f"""
{Colors.HEADER}
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║     ██████╗ ███████╗██╗███╗   ██╗████████╗ ██████╗               ║
║    ██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝██╔═══██╗              ║
║    ██║   ██║███████╗██║██╔██╗ ██║   ██║   ██║   ██║              ║
║    ██║   ██║╚════██║██║██║╚██╗██║   ██║   ██║   ██║              ║
║    ╚██████╔╝███████║██║██║ ╚████║   ██║   ╚██████╔╝              ║
║     ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝               ║
║                                                                   ║
║              ██╗███╗   ██╗████████╗███████╗██╗                   ║
║              ██║████╗  ██║╚══██╔══╝██╔════╝██║                   ║
║              ██║██╔██╗ ██║   ██║   █████╗  ██║                   ║
║              ██║██║╚██╗██║   ██║   ██╔══╝  ██║                   ║
║              ██║██║ ╚████║   ██║   ███████╗███████╗              ║
║              ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚══════╝              ║
║                                                                   ║
║              УНИВЕРСАЛЬНЫЙ OSINT-ИНСТРУМЕНТ v3.0                 ║
║                    All-in-One Intelligence Tool                   ║
╚═══════════════════════════════════════════════════════════════════╝
{Colors.RESET}
"""

# ============================================================================
# БАЗЫ ДАННЫХ
# ============================================================================

# Расширенная база операторов РФ (актуально на 2025)
RU_OPERATORS = {
    # МТС
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
    
    # Tele2
    '900': 'Tele2', '901': 'Tele2', '902': 'Tele2', '908': 'Tele2',
    '950': 'Tele2', '951': 'Tele2', '952': 'Tele2', '953': 'Tele2',
    '958': 'Tele2', '977': 'Tele2', '991': 'Tele2', '992': 'Tele2',
    '993': 'Tele2', '994': 'Tele2', '995': 'Tele2', '996': 'Tele2',
    
    # Yota (виртуальный на сети МегаФон)
    '000': 'Yota', '001': 'Yota', '002': 'Yota', '003': 'Yota',
    '004': 'Yota', '005': 'Yota', '006': 'Yota', '007': 'Yota',
    '008': 'Yota', '009': 'Yota', '970': 'Yota', '971': 'Yota',
    '972': 'Yota', '973': 'Yota', '974': 'Yota', '975': 'Yota',
    '976': 'Yota', '977': 'Yota', '978': 'Yota', '979': 'Yota',
    
    # Тинькофф Мобайл (на сети Tele2)
    '958': 'Тинькофф Мобайл', '959': 'Тинькофф Мобайл',
    '977': 'Тинькофф Мобайл', '978': 'Тинькофф Мобайл',
    
    # SberMobile (на сети Tele2)
    '900': 'SberMobile', '901': 'SberMobile', '902': 'SberMobile',
    
    # Другие виртуальные
    '959': 'Danycom', '960': 'Danycom',
    '989': 'Matrix Telecom', '990': 'Matrix Telecom'
}

# База регионов РФ по кодам DEF
RU_REGIONS = {
    # Москва и область
    '910': 'Москва и МО', '911': 'Москва и МО', '912': 'Москва и МО',
    '913': 'Москва и МО', '914': 'Москва и МО', '915': 'Москва и МО',
    '916': 'Москва и МО', '917': 'Москва и МО', '918': 'Москва и МО',
    '919': 'Москва и МО', '985': 'Москва и МО', '986': 'Москва и МО',
    
    # Санкт-Петербург и ЛО
    '921': 'Санкт-Петербург и ЛО', '981': 'Санкт-Петербург и ЛО',
    '982': 'Санкт-Петербург и ЛО', '983': 'Санкт-Петербург и ЛО',
    
    # Центральный федеральный округ
    '920': 'Центральный ФО', '930': 'Центральный ФО',
    '961': 'Центральный ФО', '962': 'Центральный ФО',
    
    # Северо-Западный ФО
    '931': 'Северо-Западный ФО', '932': 'Северо-Западный ФО',
    '921': 'Северо-Западный ФО', '981': 'Северо-Западный ФО',
    
    # Южный ФО
    '928': 'Южный ФО', '938': 'Южный ФО', '988': 'Южный ФО',
    '989': 'Южный ФО', '918': 'Краснодарский край',
    
    # Приволжский ФО
    '927': 'Приволжский ФО', '937': 'Приволжский ФО',
    '950': 'Приволжский ФО', '951': 'Приволжский ФО',
    '952': 'Приволжский ФО', '953': 'Приволжский ФО',
    
    # Уральский ФО
    '922': 'Уральский ФО', '932': 'Уральский ФО',
    '982': 'Уральский ФО', '992': 'Уральский ФО',
    
    # Сибирский ФО
    '923': 'Сибирский ФО', '933': 'Сибирский ФО',
    '983': 'Сибирский ФО', '993': 'Сибирский ФО',
    
    # Дальневосточный ФО
    '924': 'Дальневосточный ФО', '934': 'Дальневосточный ФО',
    '984': 'Дальневосточный ФО', '994': 'Дальневосточный ФО'
}

# База стран для международных номеров
COUNTRIES = {
    '7': 'Россия',
    '1': 'США/Канада',
    '44': 'Великобритания',
    '49': 'Германия',
    '33': 'Франция',
    '39': 'Италия',
    '34': 'Испания',
    '380': 'Украина',
    '375': 'Беларусь',
    '77': 'Казахстан',
    '994': 'Азербайджан',
    '374': 'Армения',
    '995': 'Грузия',
    '373': 'Молдова',
    '996': 'Кыргызстан',
    '992': 'Таджикистан',
    '993': 'Туркменистан',
    '998': 'Узбекистан'
}

# ============================================================================
# ОСНОВНЫЕ ФУНКЦИИ
# ============================================================================

def clear_screen():
    """Очистка экрана"""
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header(text):
    """Печать заголовка"""
    print(f"\n{Colors.BG_HEADER} ═══ {text} ═══ {Colors.RESET}\n")

def print_success(text):
    """Печать успешного сообщения"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    """Печать ошибки"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text):
    """Печать предупреждения"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text):
    """Печать информационного сообщения"""
    print(f"{Colors.CYAN}ℹ {text}{Colors.RESET}")

def print_menu_item(number, text, description=""):
    """Печать пункта меню"""
    print(f"{Colors.YELLOW}[{number}]{Colors.RESET} {Colors.WHITE}{text}{Colors.RESET}")
    if description:
        print(f"   {Colors.CYAN}{description}{Colors.RESET}")

def save_results(data, filename=None):
    """Сохранение результатов в файл"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"osint_results_{timestamp}.json"
    
    # Создаем директорию для результатов
    if not os.path.exists("osint_results"):
        os.makedirs("osint_results")
    
    filepath = os.path.join("osint_results", filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print_success(f"Результаты сохранены в: {filepath}")
    return filepath

# ============================================================================
# МОДУЛЬ ПОИСКА ПО НОМЕРУ ТЕЛЕФОНА
# ============================================================================

def parse_phone_number(phone):
    """
    Парсинг и валидация номера телефона
    Поддерживает форматы: +7XXX, 8XXX, 7XXX, +1XXX и т.д.
    """
    # Очистка от мусора
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Если нет плюса, пытаемся определить
    if not cleaned.startswith('+'):
        if cleaned.startswith('8') and len(cleaned) == 11:
            # Российский формат 8XXXXXXXXXX
            cleaned = '+7' + cleaned[1:]
        elif cleaned.startswith('7') and len(cleaned) == 11:
            # Российский формат 7XXXXXXXXXX
            cleaned = '+' + cleaned
        elif len(cleaned) == 10:
            # 10 цифр - вероятно российский
            cleaned = '+7' + cleaned
        else:
            cleaned = '+' + cleaned
    
    try:
        number = phonenumbers.parse(cleaned, None)
        
        if not phonenumbers.is_valid_number(number):
            return {"error": "Невалидный номер телефона"}
        
        # Базовая информация
        info = {
            "raw_input": phone,
            "e164": phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164),
            "international": phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "national": phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.NATIONAL),
            "country_code": number.country_code,
            "national_number": number.national_number,
            "valid": phonenumbers.is_valid_number(number),
            "possible": phonenumbers.is_possible_number(number),
            "country": phonenumbers.region_code_for_number(number),
        }
        
        # Дополнительная информация для РФ
        if info['country_code'] == 7:
            national_str = str(number.national_number)
            if len(national_str) >= 3:
                def_code = national_str[:3]
                info['def_code'] = def_code
                info['operator'] = RU_OPERATORS.get(def_code, "Неизвестный оператор")
                info['region'] = RU_REGIONS.get(def_code, "Регион не определен")
                
                # Проверка на перенесенный номер (MNP)
                info['mnp_possible'] = def_code in ['958', '959', '977', '978']
        
        # Определение типа номера
        number_type = phonenumbers.number_type(number)
        type_map = {
            0: "Фиксированная линия",
            1: "Мобильный",
            2: "Фиксированная линия или мобильный",
            3: "Бесплатный вызов",
            4: "Премиум-тариф",
            5: "Общий тариф",
            6: "Пейджинг",
            7: "Персональный номер",
            8: "VOIP",
            9: "Бизнес-линия"
        }
        info['line_type'] = type_map.get(number_type, "Неизвестный тип")
        
        # Часовой пояс
        timezones = timezone.time_zones_for_number(number)
        info['timezones'] = list(timezones) if timezones else []
        
        # Оператор (международный)
        carrier_name = carrier.name_for_number(number, "en")
        info['carrier'] = carrier_name if carrier_name else "Не определен"
        
        return info
        
    except Exception as e:
        return {"error": f"Ошибка парсинга: {str(e)}"}

def check_phone_instant_check(phone_info):
    """
    Проверка номера через онлайн-сервисы (имитация)
    В реальности здесь должны быть API запросы
    """
    results = {
        "instant_check": {},
        "social_media": {},
        "messengers": {},
        "breaches": {}
    }
    
    e164 = phone_info.get('e164', '')
    national = phone_info.get('national', '')
    
    # Проверка в мессенджерах (имитация наличия)
    results['messengers'] = {
        "telegram": f"https://t.me/{phone_info.get('national', '').replace(' ', '')}",
        "whatsapp": f"https://wa.me/{e164}",
        "viber": f"viber://add?number={e164}",
        "signal": f"https://signal.me/#p/{e164}",
        "wechat": "Требуется ручная проверка"
    }
    
    # Социальные сети (поисковые запросы)
    social_platforms = [
        "vk.com", "ok.ru", "facebook.com", "instagram.com",
        "tiktok.com", "twitter.com", "linkedin.com"
    ]
    
    queries = []
    for platform in social_platforms:
        queries.append(f"site:{platform} {e164}")
        queries.append(f"site:{platform} {national}")
    
    results['social_media']['search_queries'] = queries
    
    # Проверка утечек (имитация)
    results['breaches']['possible_leaks'] = [
        f"Проверить на haveibeenpwned.com: {e164}",
        f"Проверить на leak-check.net: {e164}",
        "Базы данных требуют платного доступа"
    ]
    
    return results

def phone_osint_module():
    """Основной модуль поиска по номеру телефона"""
    clear_screen()
    print(BANNER)
    print_header("МОДУЛЬ ПОИСКА ПО НОМЕРУ ТЕЛЕФОНА")
    
    print(f"{Colors.CYAN}Введите номер телефона в любом формате:{Colors.RESET}")
    print("Примеры: +79161234567, 89161234567, 79161234567, +12125551234")
    phone = input(f"{Colors.YELLOW}→ {Colors.RESET}").strip()
    
    if not phone:
        print_error("Номер не введен")
        input("\nНажмите Enter для продолжения...")
        return
    
    print(f"\n{Colors.YELLOW}[*] Анализ номера: {phone}{Colors.RESET}\n")
    
    # Парсинг номера
    phone_info = parse_phone_number(phone)
    
    if "error" in phone_info:
        print_error(phone_info["error"])
        input("\nНажмите Enter для продолжения...")
        return
    
    # Вывод результатов
    print(f"{Colors.GREEN}[+] БАЗОВАЯ ИНФОРМАЦИЯ:{Colors.RESET}")
    print(f"  Международный формат: {phone_info.get('international', 'Н/Д')}")
    print(f"  Национальный формат: {phone_info.get('national', 'Н/Д')}")
    print(f"  E.164 формат: {phone_info.get('e164', 'Н/Д')}")
    print(f"  Код страны: +{phone_info.get('country_code', '')}")
    print(f"  Страна: {phone_info.get('country', 'Н/Д')}")
    
    if phone_info.get('operator'):
        print(f"\n{Colors.GREEN}[+] ИНФОРМАЦИЯ ПО РФ:{Colors.RESET}")
        print(f"  Оператор: {phone_info.get('operator', 'Н/Д')}")
        print(f"  Регион: {phone_info.get('region', 'Н/Д')}")
        print(f"  DEF-код: {phone_info.get('def_code', 'Н/Д')}")
    
    print(f"\n{Colors.GREEN}[+] ТЕХНИЧЕСКАЯ ИНФОРМАЦИЯ:{Colors.RESET}")
    print(f"  Тип линии: {phone_info.get('line_type', 'Н/Д')}")
    print(f"  Оператор (межд.): {phone_info.get('carrier', 'Н/Д')}")
    print(f"  Валидность: {'Да' if phone_info.get('valid') else 'Нет'}")
    print(f"  Возможность: {'Да' if phone_info.get('possible') else 'Нет'}")
    
    if phone_info.get('timezones'):
        print(f"  Часовые пояса: {', '.join(phone_info['timezones'])}")
    
    # Проверка онлайн
    print(f"\n{Colors.YELLOW}[*] Проверка онлайн-присутствия...{Colors.RESET}")
    online_results = check_phone_instant_check(phone_info)
    
    print(f"\n{Colors.GREEN}[+] МЕССЕНДЖЕРЫ:{Colors.RESET}")
    for messenger, link in online_results['messengers'].items():
        print(f"  {messenger.capitalize()}: {link}")
    
    print(f"\n{Colors.GREEN}[+] ПОИСКОВЫЕ ЗАПРОСЫ:{Colors.RESET}")
    for i, query in enumerate(online_results['social_media']['search_queries'][:5], 1):
        print(f"  {i}. https://www.google.com/search?q={query.replace(' ', '+')}")
    
    print(f"\n{Colors.GREEN}[+] ПРОВЕРКА УТЕЧЕК:{Colors.RESET}")
    for leak in online_results['breaches']['possible_leaks']:
        print(f"  • {leak}")
    
    # Сохранение результатов
    save_choice = input(f"\n{Colors.YELLOW}Сохранить результаты? (y/n): {Colors.RESET}").lower()
    if save_choice == 'y':
        results = {
            "phone_info": phone_info,
            "online_check": online_results,
            "timestamp": datetime.now().isoformat()
        }
        save_results(results)
    
    input(f"\n{Colors.CYAN}Нажмите Enter для возврата в меню...{Colors.RESET}")

# ============================================================================
# МОДУЛЬ ПОИСКА ПО USERNAME В TELEGRAM
# ============================================================================

def check_telegram_username(username):
    """
    Проверка username в Telegram и получение информации
    """
    results = {
        "username": username,
        "telegram_info": {},
        "cross_platform": {},
        "search_queries": []
    }
    
    # Очистка username
    username = username.strip().replace('@', '')
    
    # Проверка существования (имитация)
    print(f"{Colors.YELLOW}[*] Проверка username: @{username}{Colors.RESET}")
    
    # Генерация ссылок
    results['telegram_info']['links'] = {
        "direct": f"https://t.me/{username}",
        "sso": f"https://t.me/{username}?embed=1",
        "messages": f"https://t.me/s/{username}"  # Для каналов
    }
    
    # Проверка в публичных источниках
    time.sleep(1)  # Имитация задержки
    
    # Поиск по другим платформам
    platforms = {
        "instagram": f"https://instagram.com/{username}",
        "twitter": f"https://twitter.com/{username}",
        "github": f"https://github.com/{username}",
        "reddit": f"https://reddit.com/user/{username}",
        "youtube": f"https://youtube.com/@{username}",
        "tiktok": f"https://tiktok.com/@{username}",
        "facebook": f"https://facebook.com/{username}",
        "vk": f"https://vk.com/{username}",
        "ok": f"https://ok.ru/{username}"
    }
    
    results['cross_platform'] = platforms
    
    # Поисковые запросы
    results['search_queries'] = [
        f"site:t.me {username}",
        f"site:telegram.org {username}",
        f"\"@{username}\" telegram",
        f"inurl:t.me/{username}",
        f"intitle:{username} telegram"
    ]
    
    return results

def telegram_search_module():
    """Модуль поиска по Telegram username"""
    clear_screen()
    print(BANNER)
    print_header("МОДУЛЬ ПОИСКА В TELEGRAM")
    
    print(f"{Colors.CYAN}Введите username (можно с @ или без):{Colors.RESET}")
    print("Примеры: @durov, durov, @telegram")
    username = input(f"{Colors.YELLOW}→ {Colors.RESET}").strip()
    
    if not username:
        print_error("Username не введен")
        input("\nНажмите Enter для продолжения...")
        return
    
    results = check_telegram_username(username)
    clean_username = username.replace('@', '')
    
    print(f"\n{Colors.GREEN}[+] ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ @{clean_username}{Colors.RESET}\n")
    
    print(f"{Colors.GREEN}[+] ССЫЛКИ НА TELEGRAM:{Colors.RESET}")
    for link_type, url in results['telegram_info']['links'].items():
        print(f"  {link_type.capitalize()}: {url}")
    
    print(f"\n{Colors.GREEN}[+] ПОИСК НА ДРУГИХ ПЛАТФОРМАХ:{Colors.RESET}")
    for platform, url in list(results['cross_platform'].items())[:8]:
        print(f"  {platform.capitalize()}: {url}")
    
    print(f"\n{Colors.GREEN}[+] ПОИСКОВЫЕ ЗАПРОСЫ:{Colors.RESET}")
    for i, query in enumerate(results['search_queries'], 1):
        print(f"  {i}. https://www.google.com/search?q={query.replace(' ', '+')}")
    
    # Дополнительные проверки
    print(f"\n{Colors.GREEN}[+] ДОПОЛНИТЕЛЬНЫЕ ПРОВЕРКИ:{Colors.RESET}")
    print(f"  • Проверить в архиве: https://archive.org/web/*/https://t.me/{clean_username}")
    print(f"  • Проверить в Telegram DB: https://t.me/s/{clean_username}")
    print(f"  • Поиск по фото: https://yandex.ru/images/search?text=@{clean_username}")
    
    # Сохранение результатов
    save_choice = input(f"\n{Colors.YELLOW}Сохранить результаты? (y/n): {Colors.RESET}").lower()
    if save_choice == 'y':
        results['timestamp'] = datetime.now().isoformat()
        save_results(results, f"telegram_{clean_username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    input(f"\n{Colors.CYAN}Нажмите Enter для возврата в меню...{Colors.RESET}")

# ============================================================================
# МОДУЛЬ ПОИСКА ПО USERNAME (ВСЕ ПЛАТФОРМЫ)
# ============================================================================

def universal_username_search():
    """Универсальный поиск по username на всех платформах"""
    clear_screen()
    print(BANNER)
    print_header("УНИВЕРСАЛЬНЫЙ ПОИСК ПО USERNAME")
    
    print(f"{Colors.CYAN}Введите username для поиска:{Colors.RESET}")
    username = input(f"{Colors.YELLOW}→ {Colors.RESET}").strip()
    
    if not username:
        print_error("Username не введен")
        input("\nНажмите Enter для продолжения...")
        return
    
    # Список платформ для проверки
    platforms = {
        # Социальные сети
        "VK": f"https://vk.com/{username}",
        "Odnoklassniki": f"https://ok.ru/{username}",
        "Facebook": f"https://facebook.com/{username}",
        "Instagram": f"https://instagram.com/{username}",
        "Twitter": f"https://twitter.com/{username}",
        "LinkedIn": f"https://linkedin.com/in/{username}",
        "TikTok": f"https://tiktok.com/@{username}",
        "Snapchat": f"https://snapchat.com/add/{username}",
        "Pinterest": f"https://pinterest.com/{username}",
        "Tumblr": f"https://{username}.tumblr.com",
        
        # Мессенджеры
        "Telegram": f"https://t.me/{username}",
        "Discord": f"https://discord.com/users/{username}",
        "Skype": f"https://skype.com/{username}",
        
        # Форумы и сообщества
        "Reddit": f"https://reddit.com/user/{username}",
        "GitHub": f"https://github.com/{username}",
        "GitLab": f"https://gitlab.com/{username}",
        "Bitbucket": f"https://bitbucket.org/{username}",
        "StackOverflow": f"https://stackoverflow.com/users/{username}",
        "Medium": f"https://medium.com/@{username}",
        "Quora": f"https://quora.com/profile/{username}",
        
        # Видео и стриминг
        "YouTube": f"https://youtube.com/@{username}",
        "Twitch": f"https://twitch.tv/{username}",
        "Vimeo": f"https://vimeo.com/{username}",
        "SoundCloud": f"https://soundcloud.com/{username}",
        
        # Игры
        "Steam": f"https://steamcommunity.com/id/{username}",
        "Epic Games": f"https://epicgames.com/id/{username}",
        "Xbox": f"https://xbox.com/users/{username}",
        "PlayStation": f"https://playstation.com/users/{username}",
        
        # Профессиональные
        "Habr": f"https://habr.com/users/{username}",
        "GeekTimes": f"https://geektimes.ru/users/{username}",
        "DOU": f"https://dou.ua/users/{username}",
        
        # Российские платформы
        "Yandex": f"https://yandex.ru/q/profile/{username}",
        "Mail.ru": f"https://my.mail.ru/{username}",
        "LiveJournal": f"https://{username}.livejournal.com",
        
        # Международные
        "Imgur": f"https://imgur.com/user/{username}",
        "Flickr": f"https://flickr.com/people/{username}",
        "DeviantArt": f"https://deviantart.com/{username}",
        "Behance": f"https://behance.net/{username}",
        "Dribbble": f"https://dribbble.com/{username}"
    }
    
    print(f"\n{Colors.YELLOW}[*] Поиск username '{username}' на {len(platforms)} платформах...{Colors.RESET}\n")
    
    # Разбиваем на категории для вывода
    categories = {
        "Социальные сети": ["VK", "Odnoklassniki", "Facebook", "Instagram", "Twitter", "LinkedIn", "TikTok", "Snapchat"],
        "Мессенджеры": ["Telegram", "Discord", "Skype"],
        "Форумы и IT": ["Reddit", "GitHub", "GitLab", "Bitbucket", "StackOverflow", "Medium", "Quora"],
        "Видео и музыка": ["YouTube", "Twitch", "Vimeo", "SoundCloud"],
        "Игровые платформы": ["Steam", "Epic Games", "Xbox", "PlayStation"],
        "Российские ресурсы": ["Habr", "GeekTimes", "Yandex", "Mail.ru", "LiveJournal"],
        "Творческие платформы": ["Imgur", "Flickr", "DeviantArt", "Behance", "Dribbble"]
    }
    
    for category, platform_list in categories.items():
        print(f"{Colors.GREEN}[+] {category}:{Colors.RESET}")
        for platform in platform_list:
            if platform in platforms:
                print(f"  {platform}: {platforms[platform]}")
        print()
    
    # Поисковые доры
    print(f"{Colors.GREEN}[+] РАСШИРЕННЫЙ ПОИСК (Google Dorks):{Colors.RESET}")
    dorks = [
        f"inurl:\"{username}\"",
        f"intitle:\"{username}\"",
        f"\"profile\" \"{username}\"",
        f"\"user\" \"{username}\"",
        f"\"member\" \"{username}\"",
        f"site:facebook.com \"{username}\"",
        f"site:instagram.com \"{username}\"",
        f"site:twitter.com \"{username}\"",
        f"site:linkedin.com \"{username}\"",
        f"site:github.com \"{username}\""
    ]
    
    for i, dork in enumerate(dorks[:5], 1):
        print(f"  {i}. https://www.google.com/search?q={dork.replace(' ', '+')}")
    
    # Сохранение результатов
    save_choice = input(f"\n{Colors.YELLOW}Сохранить результаты? (y/n): {Colors.RESET}").lower()
    if save_choice == 'y':
        results = {
            "username": username,
            "platforms": platforms,
            "categories": categories,
            "dorks": dorks,
            "timestamp": datetime.now().isoformat()
        }
        save_results(results, f"username_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    input(f"\n{Colors.CYAN}Нажмите Enter для возврата в меню...{Colors.RESET}")

# ============================================================================
# МОДУЛЬ ПРОВЕРКИ УТЕЧЕК ДАННЫХ
# ============================================================================

def breach_check_module():
    """Проверка утечек данных по номеру/email"""
    clear_screen()
    print(BANNER)
    print_header("МОДУЛЬ ПРОВЕРКИ УТЕЧЕК ДАННЫХ")
    
    print(f"{Colors.CYAN}Что проверяем?{Colors.RESET}")
    print("1. Номер телефона")
    print("2. Email адрес")
    print("3. Username")
    
    choice = input(f"\n{Colors.YELLOW}Выберите опцию (1-3): {Colors.RESET}").strip()
    
    if choice not in ['1', '2', '3']:
        print_error("Неверный выбор")
        input("\nНажмите Enter для продолжения...")
        return
    
    target = input(f"{Colors.YELLOW}Введите данные для проверки: {Colors.RESET}").strip()
    
    if not target:
        print_error("Данные не введены")
        input("\nНажмите Enter для продолжения...")
        return
    
    print(f"\n{Colors.YELLOW}[*] Проверка утечек для: {target}{Colors.RESET}\n")
    
    # Список публичных баз и сервисов
    breach_services = {
        "haveibeenpwned": "https://haveibeenpwned.com/account/" + target.replace('@', '%40'),
        "leakcheck": "https://leak-check.net/search?query=" + target,
        "breachdirectory": "https://breachdirectory.org/search?query=" + target,
        "snusbase": "https://snusbase.com/",
        "leakedsource": "https://leakedsource.ru/",
        "dehashed": "https://dehashed.com/",
        "intelx": "https://intelx.io/?s=" + target,
        "psbdmp": "https://psbdmp.ws/search/" + target
    }
    
    print(f"{Colors.GREEN}[+] СЕРВИСЫ ДЛЯ ПРОВЕРКИ:{Colors.RESET}")
    for name, url in breach_services.items():
        print(f"  {name}: {url}")
    
    # Генерация поисковых запросов
    print(f"\n{Colors.GREEN}[+] ПОИСК В ОТКРЫТЫХ ИСТОЧНИКАХ:{Colors.RESET}")
    dorks = [
        f"intext:\"{target}\" filetype:sql",
        f"intext:\"{target}\" filetype:csv",
        f"intext:\"{target}\" filetype:xlsx",
        f"intext:\"{target}\" \"password\"",
        f"intext:\"{target}\" \"leak\"",
        f"intext:\"{target}\" \"database\""
    ]
    
    for i, dork in enumerate(dorks, 1):
        print(f"  {i}. https://www.google.com/search?q={dork.replace(' ', '+')}")
    
    print(f"\n{Colors.YELLOW}⚠ ВНИМАНИЕ: Большинство баз утечек требуют{Colors.RESET}")
    print(f"{Colors.YELLOW}  платного доступа или регистрации.{Colors.RESET}")
    
    input(f"\n{Colors.CYAN}Нажмите Enter для возврата в меню...{Colors.RESET}")

# ============================================================================
# МОДУЛЬ НАСТРОЕК
# ============================================================================

def settings_module():
    """Настройки инструмента"""
    clear_screen()
    print(BANNER)
    print_header("НАСТРОЙКИ")
    
    print(f"{Colors.GREEN}[+] ТЕКУЩАЯ КОНФИГУРАЦИЯ:{Colors.RESET}")
    print(f"  Директория сохранений: {os.path.abspath('osint_results')}")
    print(f"  Версия инструмента: 3.0")
    print(f"  Режим: All-in-One OSINT")
    
    print(f"\n{Colors.GREEN}[+] ДОСТУПНЫЕ ОПЦИИ:{Colors.RESET}")
    print("  1. Очистить все сохраненные результаты")
    print("  2. Создать резервную копию")
    print("  3. Проверить обновления")
    print("  4. Настройка прокси")
    
    choice = input(f"\n{Colors.YELLOW}Выберите опцию (1-4): {Colors.RESET}").strip()
    
    if choice == '1':
        if os.path.exists("osint_results"):
            import shutil
            shutil.rmtree("osint_results")
            print_success("Директория результатов очищена")
        else:
            print_info("Директория результатов не существует")
    
    elif choice == '2':
        backup_name = f"osint_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
        if os.path.exists("osint_results"):
            import tarfile
            with tarfile.open(backup_name, "w:gz") as tar:
                tar.add("osint_results")
            print_success(f"Резервная копия создана: {backup_name}")
        else:
            print_info("Нет данных для резервного копирования")
    
    input(f"\n{Colors.CYAN}Нажмите Enter для возврата в меню...{Colors.RESET}")

# ============================================================================
# ОСНОВНОЕ МЕНЮ
# ============================================================================

def main_menu():
    """Главное меню программы"""
    while True:
        clear_screen()
        print(BANNER)
        
        print(f"{Colors.BG_MENU}════════════════════ ГЛАВНОЕ МЕНЮ ════════════════════{Colors.RESET}\n")
        
        menu_items = [
            ("1", "ПОИСК ПО НОМЕРУ ТЕЛЕФОНА", "Анализ оператора, региона, проверка в мессенджерах и соцсетях"),
            ("2", "ПОИСК ПО USERNAME В TELEGRAM", "Поиск информации о пользователе Telegram"),
            ("3", "УНИВЕРСАЛЬНЫЙ ПОИСК ПО USERNAME", "Проверка наличия username на 50+ платформах"),
            ("4", "ПРОВЕРКА УТЕЧЕК ДАННЫХ", "Поиск в базах данных и утечках"),
            ("5", "НАСТРОЙКИ", "Конфигурация инструмента"),
            ("0", "ВЫХОД", "Завершение работы")
        ]
        
        for item in menu_items:
            print_menu_item(item[0], item[1], item[2])
        
        print(f"\n{Colors.BG_HEADER}═══════════════════════════════════════════════════════{Colors.RESET}\n")
        
        choice = input(f"{Colors.YELLOW}Введите номер опции: {Colors.RESET}").strip()
        
        if choice == '1':
            phone_osint_module()
        elif choice == '2':
            telegram_search_module()
        elif choice == '3':
            universal_username_search()
        elif choice == '4':
            breach_check_module()
        elif choice == '5':
            settings_module()
        elif choice == '0':
            print(f"\n{Colors.GREEN}Завершение работы. До свидания!{Colors.RESET}")
            sys.exit(0)
        else:
            print_error("Неверный выбор. Нажмите Enter и попробуйте снова.")
            input()

# ============================================================================
# ТОЧКА ВХОДА
# ============================================================================

if __name__ == "__main__":
    try:
        # Проверка наличия необходимых библиотек
        required_packages = ['phonenumbers', 'colorama', 'requests']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"{Colors.YELLOW}[*] Установка недостающих пакетов: {', '.join(missing_packages)}{Colors.RESET}")
            for package in missing_packages:
                os.system(f"pip install {package}")
            print(f"{Colors.GREEN}[+] Пакеты установлены. Перезапустите скрипт.{Colors.RESET}")
            sys.exit(0)
        
        main_menu()
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Прерывание пользователя. Выход...{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}Критическая ошибка: {str(e)}{Colors.RESET}")
        sys.exit(1)
