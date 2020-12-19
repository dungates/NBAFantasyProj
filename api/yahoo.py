import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

YAHOO_FANTASY_URI = "https://fantasysports.yahooapis.com/fantasy/v2/"

APP_ID = os.getenv("APP_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


def main():
    print(APP_ID)
    print(CLIENT_ID)
    print(CLIENT_SECRET)
    return 0


if __name__ == "__main__":
    main()