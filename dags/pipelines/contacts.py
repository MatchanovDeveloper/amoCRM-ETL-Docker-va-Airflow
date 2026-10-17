
import json
import pandas as pd
from extracter import get_contact, get_field
from load import loader
from functions import format_uzb_phone, city_fixer


## ==== ETXRACT ====
print("Extracting Contacts started...")

data = get_contact()



df = []

for row in data:
    
    df.append({
        'id': row['id'],
        'contact_id': get_field(row, 'Contact_ID'),
        'company_id': get_field(row, 'Company_id'),
        'name': row['name'],
        'role': get_field(row, 'POSITION'),
        'company': get_field(row, 'Company'),
        'phone': get_field(row, 'PHONE'),
        # 'company': get_field(row, 'Company'),
        'email': get_field(row, 'EMAIL'),
        'tags': get_field(row, 'Tags'),
        'city': get_field(row, 'City'),
        'source': get_field(row, 'Source'),
    })

contact = pd.DataFrame(df)




## ==== TRANSFORM ====
print("Transforming Contacts started...")

contact.dtypes

contact['id'] = contact['id'].drop_duplicates(inplace=False)   #duplicatelarni olib tashash

contact['tags'] = contact['tags'].str.title()

contact['source'] = contact['source'].str.capitalize()


contact['name'] = contact['name'].str.replace(
    r"(['‘’`])([A-Z])", 
    lambda m: m.group(1) + m.group(2).lower(), 
    regex=True
)

contact['phone'] = contact['phone'].apply(format_uzb_phone)

contact['email'] = contact['email'].str.lower()

contact['city'] = city_fixer(contact, 'city')

contact['company'] =contact['company'].str.rstrip('.')
forms = r'(mchj|xk|Xk|yatt|oaj|aj|ok|qk|yoaj|000|Мчж|Ятт|Oaj)'

contact['company'] =contact['company'].str.replace(
    rf'(?i)\b{forms}$', lambda x: x.group(0).upper(), regex=True
)





## ==== LOAD ====
print("Loading Contacts started...")
loader(contact, 'contacts')
print("Contacts loaded successfully!")


