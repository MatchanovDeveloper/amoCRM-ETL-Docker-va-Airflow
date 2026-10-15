
import pandas as pd
from extracter import get_company, get_field, get_tags
from load import loader
from functions import parse_mixed_dates, city_fixer, format_uzb_phone
import re

## ==== EXTRACT ====

data = get_company()

df = pd.DataFrame(data)



## ==== TRANSFORM ====

company = []

for i in data:

    company.append({
        'id': i['id'],
        'Company_ID': get_field(i, 'Company_ID'),
        'name': i['name'],
        'phone': get_field(i, 'PHONE'),
        'email': get_field(i, 'EMAIL'),
        'web-site': get_field(i, 'WEB'),
        'address': get_field(i, 'ADDRESS'),
        'City': get_field(i, 'City'),
        'Employees_no': get_field(i, 'Employees'),
        'Revenue': get_field(i, 'Revenue (UZS)'),
        'Registered': get_field(i, 'Registered'),
        'Tag': get_tags(i)
    })

df = pd.DataFrame(company)

df.dtypes

str_to_num = [
    'Employees_no',
    'Revenue'
]

for i in str_to_num:
    df[i] = pd.to_numeric(df[i], errors='coerce')

#----------------------------


# Registered ustunini to'g'irlash


df['Registered'] = df['Registered'].apply(parse_mixed_dates)


#----------------------------

# -- joy nomlarini bir xil shaklga keltirish
df.groupby('City')['Revenue'].sum()   # nechta har xil city variantlarini ko'rish uchun


df['City'] = city_fixer(df, 'City')

#----------------------------

# -- Bo'sh va Null katakchalarni '-' bilan almashtirish
cols = ['City', 'Employees_no', 'address', 'email', 'web-site', 'Revenue', 'Registered', 'Tag']
df[cols] = df[cols].replace(r'^\s*$', '-', regex=True).replace('Missing value', '-').fillna('-')

#----------------------------


df['email'] = df['email'].str.lower()
df['web-site'] = df['web-site'].str.lower()
df['name'] = df['name'].str.title()



#----------------------------


df['phone'] = df['phone'].apply(format_uzb_phone)

#----------------------------


# name ustuni oxiridagi kelib qolgan . larni olib tashab, oxirgi kerakli so'zlarni upper() qilib to'g'irlash
df['name'] = df['name'].str.rstrip('.')
forms = r'(mchj|xk|Xk|yatt|oaj|aj|ok|qk|yoaj|000|Мчж|Ятт|Oaj)'

df['name'] = df['name'].str.replace(
    rf'(?i)\b{forms}$', lambda x: x.group(0).upper(), regex=True
)

#----------------------------







## ==== LOAD ====

loader(df, 'company')
