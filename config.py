from datetime import timedelta

class Config:

    #Managers
    MANAGERS = ["skarkhanis95@gmail.com", "manager2@example.com"]

    SECRET_KEY = 'whisky3105'
    API_BASE_URL = "https://api.affinitytrades.com/api/v2/my"
    API_SIGNIN_WIZARD = f"{API_BASE_URL}/signin/wizard"
    API_SIGNIN = f"{API_BASE_URL}/signin"
    API_BASE_URL_V1 = "https://api.b2broker.com/api/v1"
    PROFILE_ENDPOINT = f"https://api.affinitytrades.com/api/v1/me?with=phone,info,addresses.country,verification_level"
    PROFILE_PHOTO_API = f"{API_BASE_URL_V1}/me/profile_picture?length_side_square=232"
    API_LOGIN_ENDPOINT = f"{API_BASE_URL}/auth/login"
    API_REFRESH_TOKEN_ENDPOINT = f"{API_BASE_URL}/auth/refresh"

    # Other configurations
    # SESSION_COOKIE_SECURE = True  # For production
    # PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_TIMEOUT = 3600

    #Wallets APIs

    ACCOUNTS_API = f"{API_BASE_URL}/accounts?limit=1000"
    WITHDRAWL_INR_USD_RATE = 82.00
    TRANSACTIONS_API = f"{API_BASE_URL}/transactions?offset=0&limit=100"

    #Service APIs and Account
    ADMIN_URL = "https://api.affinitytrades.com/api/v2"
    ADMIN_SIGNIN_URL = f"{ADMIN_URL}/signin"
    ADMIN_REFRESH_URL = f"{ADMIN_URL}/refresh"
    SERVICE_ACCOUNT_EMAIL = "skarkhanis95@gmail.com"
    SERVICE_ACCOUNT_PASSWORD = "Whisky@3195"

    #Funds APIs
    GET_DEPOSIT_TRANSACTIONS_API = f"{API_BASE_URL}/transactions?offset=0&limit=10&filter%5Btype%5D=deposit"
    GET_DEPOSIT_METHODS_API = f"{API_BASE_URL}/deposit-methods"
    POST_DEPOSIT_API = f"{API_BASE_URL}/deposits"
    USD_CURRENCY_CODE = 840
    INR_DEPOSIT_DATA_MOBILE_FIELD = "7c4a16e2-58e7-4107-9fc6-9b6988450a3c"
    CAN_TRANSFER_API = "https://api.affinitytrades.com/api/v1/investment/common/minimum_deposit/can_transfer"
    TRANSFER_API = "https://api.affinitytrades.com/api/v1/transfer"
    GET_WITHDRAWAL_METHODS_API = f"{API_BASE_URL}/withdrawal-methods"

    #Database Details
    # DB_HOST = "affintytrades-mysql-affinitytradessupport-605e.k.aivencloud.com"
    # DB_PORT = 14567
    # DB_USER = "avnadmin"  # e.g., "root"
    # DB_PASSWORD = ""
    # DATABASE = "defaultdb"  # e.g., "test_db"
    DB_HOST = "affinitytrades2024.mysql.pythonanywhere-services.com"
    DB_PORT = 3306
    DB_USER = "affinitytrades20"  # e.g., "root"
    DB_PASSWORD = "r87tET@PudHNz2L3U"
    DATABASE = "affinitytrades20$affinityTrades"  # e.g., "test_db"


    #PAMM CONFIG
    INVESTMENT_ACCOUNTS_API = "https://api.affinitytrades.com/api/v1/investment/common/investment_accounts/list?types%5B0%5D=7&types%5B1%5D=6&investment_platform_id=1"

    # REGISTER SETTINGS
    CREATE_PAMM_ACCOUNT_URL = "https://api.affinitytrades.com/api/v1/investment/pamm/accounts/create?investment_platform_id=1&groupType=6"
    MASTER_ACCOUNT_NUMBER = "10588"
    INVESTMENT_PLATFORM_ID = 1
    CAN_SUBSCRIBE_URL = "https://api.affinitytrades.com/api/v1/investment/common/minimum_deposit/can_subscribe"
    SUBSCRIBE_URL = "https://api.affinitytrades.com/api/v1/investment/pamm/subscriptions/create"
    ALLOCATION_METHOD = 4
    RISK_RATIO = 1
    SEARCH_ACCOUNT = "https://api.affinitytrades.com/api/v2/accounts"
    SEARCH_CLIENT = "https://api.affinitytrades.com/api/v2/clients"


    #Manager APIS
    search_clients = "https://api.affinitytrades.com/api/v2/clients?filter%5Bemails%5D="


    # PAMM LEVELS
    LEVEL_0 = 5952.38
    LEVEL_1 = 29761.90
    LEVEL_2 = 59523.81
    LEVEL_3 = 119047.62
    LEVEL_0_NAME = "Star"
    LEVEL_1_NAME = "Double Star"
    LEVEL_2_NAME = "Level 2"
    LEVEL_3_NAME = "Level 3"

    # Runtime
    configRunTime = "Prod" # Set to 'Local' for local dev settings
