# amoCRM → PostgreSQL ETL

## 1. Loyiha haqida

Bu loyiha amoCRM'dagi **kontaktlar**, **kompaniyalar** va **bitimlarni** avtomatik olib, **PostgreSQL** bazasiga yozadi. Ma'lumotlar keyin tahlil uchun (SQL, Power BI va h.k.) tayyor turadi.

Ishlatilgan texnologiyalar: Python (pandas, SQLAlchemy), amocrm-api kutubxonasi, PostgreSQL, Apache Airflow va Docker.

## 2. Arxitektura

```
amoCRM  ──►  extracter.py  ──►  contacts.py / company.py / transactions.py  ──►  load.py  ──►  PostgreSQL
                                              ▲
                                  Airflow DAG (dag.py) har kuni ishga tushiradi
```

```
amoCRM/
├── dags/
│   ├── dag.py                # Airflow DAG: 3 task va jadval
│   └── pipelines/
│       ├── sozlamalar.py     # BARCHA sozlamalar (kalit, parol, host)
│       ├── extracter.py      # amoCRM'ga ulanish, ma'lumot olish
│       ├── load.py           # PostgreSQL'ga yozish
│       ├── functions.py      # yordamchi funksiyalar
│       ├── contacts.py       # kontaktlar pipeline'i
│       ├── company.py        # kompaniyalar pipeline'i
│       └── transactions.py   # bitimlar pipeline'i
├── docker-compose.yaml       # Airflow servislari
├── Dockerfile
├── requirements.txt
├── .env                      # FERNET_KEY, AIRFLOW_UID (Airflow uchun)
├── access_token.txt          # avtomatik yaratiladi
└── refresh_token.txt         # avtomatik yaratiladi
```

## 3. ETL jarayoni

1. **Extract:** `extracter.py` amoCRM'dan hamma kontakt, kompaniya va bitimlarni oladi. Token muddati tugasa, o'zi yangilaydi.
2. **Transform:** `contacts.py`, `company.py`, `transactions.py` xom ma'lumotdan kerakli ustunlarni ajratib, jadval (pandas DataFrame) tayyorlaydi (qo'shimcha maydonlar va teglar `functions.py` / `extracter.py` yordamida olinadi).
3. **Load:** `load.py` jadvallarni PostgreSQL'ning `amocrm` bazasiga `contacts`, `company`, `transactions` nomlari bilan yozadi. Har safar jadval yangidan yoziladi (eski ma'lumot almashadi).

Airflow'da tartib: `contacts → company → transactions`.

## 4. Qanday ishga tushiriladi (How to run)

### 4.1. Tayyorlash

Kerak: Docker Desktop, PostgreSQL, Git (lokal sinash uchun qo'shimcha Python 3.13).

```powershell
git clone https://github.com/MatchanovDeveloper/amoCRM-ETL-Docker-va-Airflow.git
cd amoCRM-ETL-Docker-va-Airflow
```

PostgreSQL'da `amocrm` bazasini oldindan yarating (pgAdmin → Databases → Create → Database). Yoki yuklamoqchi bo'lgan bazangizni nomini yozing

### 4.2. Login va parollarni qayerdan olish

| Nima | Qayerdan olinadi |
|---|---|
| `AMO_SUBDOMAIN` | amoCRM manzilidagi nom: `https://BU_YERDA.amocrm.ru` |
| `AMO_LONG_TOKEN` | amoCRM → Sozlamalar → Integratsiyalar → o'z integratsiyangiz → **Keys and accesses** → *long-lived token* yarating (muddati 1-5 yil). Token `eyJ...` bilan boshlanadi |
| `PG_USER`, `PG_PASSWORD` | PostgreSQL logini (odatda `postgres`) va paroli. Parolni o'zingiz belgilaysiz: `ALTER USER postgres PASSWORD 'PAROL';` |
| `PG_NAME` | Baza nomi (`amocrm`) |
| `FERNET_KEY` | Terminalda yaratiladi: `python -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"` xato chiqsa: [bu yerga qarang](#fernet_key-xatosi) |
| `AIRFLOW_UID` | Windows'da `50000` |
| Airflow login / parol | `airflow` / `airflow` (<http://localhost:8080>) |

### 4.3. `.env` faylni yaratish

Maxfiy bo'lgani uchun `.env` GitHub'da yo'q. Namunadan nusxa oling va to'ldiring:

```powershell
Copy-Item .env.example .env
notepad .env
```

```dotenv
AIRFLOW_UID=50000
FERNET_KEY=<yuqoridagi buyruq chiqargan kalit>
AMO_SUBDOMAIN=<subdomen>
AMO_LONG_TOKEN=eyJ...
PG_USER=postgres
PG_PASSWORD=<parol>
PG_NAME=amocrm
```
### FERNET_KEY xatosi

`FERNET_KEY` ni yaratayotganda `Python was not found` chiqsa, Python kerak emas, shu buyruq kalitni PowerShell'ning o'zida yaratadi:

```powershell
$b = New-Object byte[] 32; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b); [Convert]::ToBase64String($b).Replace('+','-').Replace('/','_')
```

Chiqqan qatorni `.env` dagi `FERNET_KEY=` dan keyin yozing.

Qiymatlar qo'shtirnoqsiz, bo'sh joysiz, bir qatorda yozilsin. `settings.py` ga tegmaysiz, u hamma narsani `.env` dan o'qiydi.


### 4.4. How to run (localhost)

#### 4.4.1. Python'ni tekshiring

```powershell
python --version
```

`Python 3.x.x` chiqsa, 4.4.3 ga o'ting.

#### 4.4.2. `Python was not found` chiqsa

Python o'rnatilmagan bo'lsa, o'rnating va VS Code'ni qayta oching:

```powershell
winget install Python.Python.3.13
```

O'rnatilgan bo'lsa, ulang:

```powershell
Set-Alias python "$env:LOCALAPPDATA\Python\pythoncore-3.14-64\python.exe"
```

#### 4.4.3. Paketlarni o'rnating

```powershell
pip install -r requirements.txt
```

#### 4.4.4. `.env` ni terminalga yuklang

```powershell
Get-Content .env | Where-Object { $_ -match '^\s*[^#=\s]+=' } | ForEach-Object { $k,$v = $_ -split '=',2; Set-Item "env:$($k.Trim())" $v.Trim() }
```

#### 4.4.5. Fayllarni shu tartibda ishga tushiring

```powershell
python dags\pipelines\contacts.py
python dags\pipelines\company.py
python dags\pipelines\transactions.py
```


### 4.5. Docker bilan avtomatlashtirish

1. Docker Desktop'ni oching ("Engine running" chiqquncha kuting).
2. Birinchi marta:

```powershell
docker compose up airflow-init
docker compose up -d --build
docker compose ps
```

`docker compose ps` da hamma servis `healthy` yoki `running` bo'lsin. Keyingi safarlarda faqat `docker compose up -d`.

3. <http://localhost:8080> ni oching (login `airflow`, parol `airflow`), `amo_crm` DAG'ini yoqing (Unpause), **Trigger** bosing. Uchala task (`contacts` → `company` → `transactions`) yashil bo'lishi kerak.
4. `.env` ni keyin o'zgartirsangiz: `docker compose down`, so'ng `docker compose up -d` (`-v` qo'shmang).


### 4.6. Har kuni avtomatik yangilash

`dags/dag.py` ichidagi `schedule` qatori vaqtni belgilaydi:

```python
schedule="0 6 * * *",   # har kuni 06:00 (Toshkent vaqti)
```

Boshqa vaqt uchun shu cron ifodani o'zgartiring (`soat`, `daqiqa` tartibiga e'tibor bering: `daqiqa soat kun oy hafta_kuni`). DAG vaqti Toshkent bo'yicha hisoblanishi uchun `start_date` da `tz="Asia/Tashkent"` bo'lishi kerak. Avtomatik ishlashi uchun o'sha vaqtda kompyuter yoqilgan va Docker Desktop ochiq bo'lishi shart.

### 4.7. Muhim eslatmalar

- **Token bekor bo'lsa** (`Token has been revoked`): `access_token.txt` va `refresh_token.txt` ni o'chiring, amoCRM'dan yangi kod olib `AMO_AUTH_CODE` ga yozing, bir marta ishga tushiring, so'ng kodni yana bo'sh qoldiring.
- **Airflow ishlab turganda lokal skriptni ishga tushirmang:** ikkalasi bir xil tokenni yangilab, bir-birini bekor qiladi.
- **To'xtatish:** `docker compose stop`. `docker compose down -v` ni ishlatmang, u Airflow bazasini o'chirib yuboradi.
