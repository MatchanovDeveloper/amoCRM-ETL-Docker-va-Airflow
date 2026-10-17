import pandas as pd

from extracter import get_transaction, get_field
from functions import city_fixer, parse_mixed_dates
from load import loader

## ==== EXTRACT ====
print("Extracting Transactions started...")
data = get_transaction()


## ==== TRANSFORM ====
print("Transforming Transactions started...")

transactions = []

for i in data:
    transactions.append({
        'id': i['id'],
        'Transaction_id': get_field(i, 'Transaction_ID'),
        'Contact_id': get_field(i, 'Contact_ID'),
        'Company_id': get_field(i, 'Company_ID'),
        'Product_name': i['name'],
        'Order_Date': get_field(i, 'Order_Date'),
        # 'Ship_Date': get_field(i, 'Ship Date'),
        'Prod_category': get_field(i, 'Product Category'),
        'Quantity_ordered': get_field(i, 'Quantity Ordered'),
        'Unit_price': get_field(i, 'Unit Price'),
        'Discount': get_field(i, 'Discount'),
        'Shipping_cost': get_field(i, 'Shipping Cost'),
        'Product_base_margin': get_field(i, 'Product Base Margin'),
        'Sales': get_field(i, 'Sales'),
        'Profit': get_field(i, 'Profit'),
        'Currency': get_field(i, 'Currency'),
        'Status': get_field(i, 'Status'),
        'Payment_method': get_field(i, 'Payment Method'),
        'Sales_manager': get_field(i, 'Sales Manager'),
        'Delivery_city': get_field(i, 'Delivery City')
    })

transactions = pd.DataFrame(transactions)


transactions.dtypes

transactions['Transaction_id'] = transactions['Transaction_id'].drop_duplicates()
transactions['Transaction_id'] = transactions['Transaction_id'].dropna()






#---------------------------------------

def fix_num(val):
    val = str(val).strip()  # trim qilish
    val = val.removesuffix("so'm")  #oxiridagi so'm yozuvini o'chirish
    val = val.removesuffix(',00')  # oxirida kelgan ,00 o'chirish
    val = val.replace(',', '') # orasida kelgan , ni olib tashlash
    val = val.replace(' ', '')
    return val

transactions['Unit_price'] = transactions['Unit_price'].apply(fix_num)


# 10% shaklida kelgan qiymatlarni 0.1 holatiga keltirish
def fix_discount(val):
    val_str = str(val).strip()
    if '%' in val_str:
        return float(val_str.removesuffix('%')) / 100
    return val

transactions['Discount'] = transactions['Discount'].apply(fix_discount)
transactions['Discount'] = transactions['Discount'].replace(',', '.', regex=True)

#---------------------------------------

transactions['Shipping_cost'] = transactions['Shipping_cost'].apply(fix_num)
#---------------------------------------

transactions['Product_base_margin'] = transactions['Product_base_margin'].apply(fix_discount)
#---------------------------------------

transactions['Sales'] = transactions['Sales'].apply(fix_num)
#---------------------------------------

transactions['Profit'] = transactions['Profit'].apply(fix_num)
#---------------------------------------

# bir nechta ustunlarni numeric typega o'zgartirish
nums = [
    'Quantity_ordered',
    'Unit_price',
    # 'Discount',
    'Shipping_cost',
    'Product_base_margin',
    'Sales',
    'Profit'
]

for num in nums:
    transactions[num] = pd.to_numeric(transactions[num], errors='coerce')

#---------------------------------------

status_mapping = {
    'Canceled': ['Bekor qilingan', 'CANCELLED', 'Canceled', 'Cancelled', 'cancelled', 'Отменено'],
    'Pending': ['Kutilmoqda', 'PENDING', 'Pend.', 'Pending', 'pending', 'В ожидании'],
    'Overdue': ["Muddati o'tgan", 'OVERDUE', 'Overdue', 'overdue', 'Просрочено'],
    'Paid': ['PAID', 'Paid', 'Payed', "To'langan", 'paid', 'Оплачено'],
    'Refunded': ['Qaytarilgan', 'REFUNDED', 'Refunded', 'refunded', 'Возврат']
}

for t, v in status_mapping.items():
    transactions['Status'] = transactions['Status'].replace(v, t)


#---------------------------------------

transactions['Payment_method'] = transactions['Payment_method'].str.title()
payment_mapping = {
    'Bank': ['Bank', "Bank O'Tkazmasi", 'Bank Transfer', 'Перечисление'],
    'Cash': ['Cash', 'Naqd', 'Наличные'],
    'Click': ['Click', 'Klik'],
    'Humo': ['Humo', 'Хумо'],
    'Payme': ['Payme', 'Пейме'],
    'Uzcard': ['Uz card', 'Uzcard']
}

for t, v in payment_mapping.items():
    transactions['Payment_method'] = transactions['Payment_method'].replace(v, t)

#-------------------------------------
transactions['Sales_manager'] = transactions['Sales_manager'].str.title()

#-------------------------------------
transactions['Delivery_city'] = city_fixer(transactions, 'Delivery_city')

#-------------------------------------
transactions['Prod_category'] = transactions['Prod_category'].str.capitalize()

#-------------------------------------

transactions.groupby('Currency')['id'].count()
transactions['Currency'] = transactions['Currency'].replace(['UZS', "so'm", 'sum', 'uzs', 'сум'], 'UZS')

#-------------------------------------

transactions['Order_Date'] = transactions['Order_Date'].apply(parse_mixed_dates)



## ==== LOAD ====
print("Loading Transactions started...")
loader(transactions, 'transactions')
print("Transactions loaded successfully!")
