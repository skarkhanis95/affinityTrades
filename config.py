from datetime import timedelta

class Config:
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

    #Database Details
    DB_HOST = "localhost"  # e.g., "localhost"
    DB_USER = "affinity_db_user"  # e.g., "root"
    DB_PASSWORD = "whisky3115" # e.g., "password"
    DATABASE = "affinityTrades"  # e.g., "test_db"

