import os 

API_CONFIG = {
    "BASE_URL" : "https://openapi.koreainvestment.com:9443",
    "TOKEN_API" : "",
    "BALANCE_API" : "",
    "OPENAI" : {
        "ACCESS_KEY" : "your openai accesskey",
        "MODEL_NAME" : "gpt-4o",
        "TEMPERATURE" : 0
    },
    "ORDER_API" : "",
    "DEV" : {
        "BASE_URL" : "https://openapivts.koreainvestment.com:29443",
        "TOKEN_API" : "",
        "BALANCE_API" : "",
        "ORDER_API" : "",
    }
}

AUTH_CONFIG = {
    "APP_KEY" : os.getenv("APP_KEY", "your app key"),
    "APP_SECRET" : os.getenv("APP_SECRET", "your secret key"),
    "ACCOUNT_NO" : os.getenv("ACCOUNT_NO", "your account no"),
    "OPTION_ACCOUNT_NO" : os.getenv("OPTION_ACCOUNT_NO", "option_account_no"),
    "KIS_AGENT" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "PROD_DIGIT" : "01",
    "DEV" : {
        "APP_KEY" : os.getenv("DEV_APP_KEY", "your_app_key"),
        "APP_SECRET" : os.getenv("DEV_APP_SECRET", "your_app_secret"),
        "ACCOUNT_NO" : os.getenv("DEV_ACCOUNT_NO", "account_no"),
        "OPTION_ACCOUNT_NO" : os.getenv("DEV_OPTION_ACCOUNT_NO", "option_account_no"),
    }
}

LOGGING_CONFIG = {
    "LEVEL" : "INFO",
    "FORMAT" : "%(asctime)s - %(levelname)s - %(message)s",
    "DATEFMT" : "%Y-%m-%d %H:%M:%S"
}

STRATEGY_CONFIG = {
    "PROFIT_THRESHOLD" : 5.0,
    "LOSS_THRESHOLD" : -3.0,
    "USE_GPT" : True
}