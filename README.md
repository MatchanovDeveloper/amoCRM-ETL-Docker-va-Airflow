# amoCRM → PostgreSQL ETL

## 1. About the Project

This project automatically extracts **contacts**, **companies**, and **deals** from amoCRM and loads them into a **PostgreSQL** database. The data is then ready for analysis (SQL, Power BI, etc.).

Technologies used: Python (pandas, SQLAlchemy), amocrm-api library, PostgreSQL, Apache Airflow, and Docker.

## 2. Architecture

```text
amoCRM  ──►  extracter.py  ──►  contacts.py / company.py / transactions.py  ──►  load.py  ──►  PostgreSQL
                                              ▲
                                  Airflow DAG (dag.py) har kuni ishga tushiradi
```

```text
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

## 3. ETL Process

1. **Extract:** `extracter.py` fetches all contacts, companies, and deals from amoCRM. If the token expires, it refreshes it automatically.
2. **Transform:** `contacts.py`, `company.py`, and `transactions.py` extract the required columns from the raw data and prepare a table (pandas DataFrame) (custom fields and tags are retrieved using `functions.py` / `extracter.py`).
3. **Load:** `load.py` writes the tables into the `amocrm` database in PostgreSQL under the names `contacts`, `company`, and `transactions`. Each run overwrites the tables with fresh data (replacing old records).

Order in Airflow: `contacts → company → transactions`.

## 4. How to Run

### 4.1. Preparation

Required: Docker Desktop, PostgreSQL, Git (and Python 3.13 for local testing).

```powershell
git clone https://github.com/MatchanovDeveloper/amoCRM-ETL-Docker-va-Airflow.git
cd amoCRM-ETL-Docker-va-Airflow
```

Create the `amocrm` database in PostgreSQL beforehand (pgAdmin → Databases → Create → Database), or specify the name of the database you want to load the data into.

### 4.2. Where to Get Logins and Passwords

| Item | Where to get it |
|---|---|
| `AMO_SUBDOMAIN` | The subdomain in your amoCRM URL: `https://HERE.amocrm.ru` |
| `AMO_LONG_TOKEN` | amoCRM → Settings → Integrations → your integration → **Keys and accesses** → generate a *long-lived token* (valid for 1–5 years). The token starts with `eyJ...` |
| `PG_USER`, `PG_PASSWORD` | Your PostgreSQL username (usually `postgres`) and password. You set the password yourself: `ALTER USER postgres PASSWORD 'PAROL';` |
| `PG_NAME` | Database name (`amocrm`) |
| `FERNET_KEY` | Generated in the terminal: `python -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"` If an error occurs: [see here](#fernet_key-error) |
| `AIRFLOW_UID` | `50000` on Windows |
| Airflow login / password | `airflow` / `airflow` (<http://localhost:8080>) |

### 4.3. Creating the `.env` File

Since it contains sensitive data, `.env` is not included on GitHub. Copy the example file and fill it in:

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

### FERNET_KEY Error

If you get `Python was not found` when generating `FERNET_KEY`, you don't need Python—this command generates the key directly in PowerShell:

```powershell
$b = New-Object byte[] 32; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b); [Convert]::ToBase64String($b).Replace('+','-').Replace('/','_')
```

Paste the generated string after `FERNET_KEY=` in `.env`.

Values must be written on a single line without quotes or spaces. Do not modify `settings.py`; it reads everything from `.env`.

### 4.4. How to Run (localhost)

#### 4.4.1. Check Python

```powershell
python --version
```

If it outputs `Python 3.x.x`, skip to step 4.4.3.

#### 4.4.2. If `Python was not found` Appears

If Python is not installed, install it and restart VS Code:

```powershell
winget install Python.Python.3.13
```

If it is already installed, link it:

```powershell
Set-Alias python "$env:LOCALAPPDATA\Python\pythoncore-3.14-64\python.exe"
```

#### 4.4.3. Install Packages

```powershell
pip install -r requirements.txt
```

#### 4.4.4. Load `.env` into the Terminal

```powershell
Get-Content .env | Where-Object { $_ -match '^\s*[^#=\s]+=' } | ForEach-Object { $k,$v = $_ -split '=',2; Set-Item "env:$($k.Trim())" $v.Trim() }
```

#### 4.4.5. Run the Files in This Order

```powershell
python dags\pipelines\contacts.py
python dags\pipelines\company.py
python dags\pipelines\transactions.py
```

### 4.5. Automation with Docker

1. Open Docker Desktop (wait until it says "Engine running").
2. For the first run:

```powershell
docker compose up airflow-init
docker compose up -d --build
docker compose ps
```

In `docker compose ps`, all services should show `healthy` or `running`. For subsequent runs, simply use `docker compose up -d`.

3. Open <http://localhost:8080> (login `airflow`, password `airflow`), enable (Unpause) the `amo_crm` DAG, and click **Trigger**. All three tasks (`contacts` → `company` → `transactions`) should turn green.
4. If you modify `.env` later: run `docker compose down`, then `docker compose up -d` (do not add `-v`).

### 4.6. Daily Automatic Updates

The `schedule` line inside `dags/dag.py` sets the run time:

```python
schedule="0 6 * * *",   # har kuni 06:00 (Toshkent vaqti)
```

To set a different time, modify this cron expression (pay attention to the `minute` and `hour` order: `minute hour day month day_of_week`). For the DAG schedule to follow Tashkent time, `start_date` must include `tz="Asia/Tashkent"`. For automatic runs to work, your computer must be turned on and Docker Desktop must be running at that scheduled time.

### 4.7. Important Notes

- **If the token is revoked** (`Token has been revoked`): delete `access_token.txt` and `refresh_token.txt`, get a new authorization code from amoCRM, put it in `AMO_AUTH_CODE`, run the pipeline once, and then leave the code blank again.
- **Do not run local scripts while Airflow is running:** both will refresh the same token and invalidate each other.
- **To stop:** `docker compose stop`. Do not use `docker compose down -v`, as it will delete the Airflow database.
