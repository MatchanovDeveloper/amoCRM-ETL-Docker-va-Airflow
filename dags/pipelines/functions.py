import pandas as pd
from dateutil import parser
import re


## date ustunini to'g'irlash uchun:

def parse_mixed_dates(val):
    if pd.isna(val):
        return pd.NaT
    
    val = str(val).strip()
    # "unknown" yoki shunga o'xshash yaroqsiz qiymatlarni NaT (bo'sh) qilish
    if val.lower() in ['unknown', 'none', 'null', 'nan', '']:
        return pd.NaT
    
    try:
        # yearfirst=True: '15-09-17' yoki '04-01-25' kabilarda yil boshida kelganini inobatga oladi
        # dayfirst=False (agar MM/DD/YYYY bo'lsa) yoki dayfirst=True qilib sozlash mumkin
        return parser.parse(val, yearfirst=True)
    except Exception:
        return pd.NaT

#-------------------------------------------------

# citylarning har xil variantlarini bir xil qilish uchun

def city_fixer(data_frame, col_name):
    # 1. Shaharlar lug'ati (mapping)
    city_mapping = {
        'Andijon': ['ANDIJON', 'Andijan', 'Андижан', 'ANDIJAN'],
        'Buxoro': ['BUKHARA', 'Bukhara', 'Бухара'],
        "Farg'ona": ["Farg'ona", 'Fargona', 'Fergana', 'Фергана'],
        'Jizzax': ['Jizzakh', 'Jizzax', 'Джизак'],
        'Qarshi': ['KARSHI', 'Karshi', 'Карши'],
        'Namangan': ['NAMANGAN', 'Namangan', 'namangan', 'Наманган'],
        'Nukus': ['NUKUS', 'Нукус'],
        'Navoiy': ['Navoi', 'Навои'],
        'Samarqand': ['SAMARKAND', 'Samarkand', 'samarkand', 'Самарканд'],
        'Toshkent': ['TASHKENT', 'Toshkent', 'tashkent', 'Ташкент', 'Tashkent'],
        'Toshkent shahri': ['Tashkent city', 'Toshkent sh.'],
        'Termiz': ['Termez', 'Термез'],
        'Urganch': ['Urganch', 'Urgench', 'Ургенч'],
        'Null': ['NULL', 'n/a', 'null', 'none', 'N/A', '-', ' ']
    }

    # 2. Har bir shahar variantini to'g'ri nomga almashtirish
    for correct_name, variants in city_mapping.items():
        data_frame[col_name] = data_frame[col_name].replace(variants, correct_name)

    # 3. Manzil imlolarini to'g'rilash (Title case va tutuq belgisi)
    data_frame[col_name] = data_frame[col_name].astype(str).str.title()
    data_frame[col_name] = data_frame[col_name].str.replace(
        r"(')([A-Z])", lambda x: x.group(1) + x.group(2).lower(), regex=True
    )

    return data_frame[col_name]


#---------------------------------------------------

# phone numberlarni to'g'rilash uchun

def format_uzb_phone(val):
    if pd.isna(val) or val == '-' or str(val).strip() == '':
        return '-'
        
    val_str = str(val).split('.')[0].strip()
    
    # Faqat raqamlarni ajratib olish (qavs, probel, plyus, chiziqchalarni tozalaydi)
    digits = re.sub(r'\D', '', val_str)
    
    if len(digits) == 9:
        digits = '998' + digits
    
    if len(digits) == 12 and digits.startswith('998'):
        
        # A) Standart xalqaro format: +998901234567
        # return f"+{digits}"
        
        # B) Formatlangan ko'rinish: +998 (90) 123-45-67
        return f"+{digits[:3]} ({digits[3:5]}) {digits[5:8]}-{digits[8:10]}-{digits[10:12]}"
        
    return '-'












