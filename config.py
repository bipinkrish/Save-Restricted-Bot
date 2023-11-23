import os

class Config(object):
    # pyro client config
    API_ID    = os.environ.get("API_ID", "")  # ⚠️ Required
    API_HASH  = os.environ.get("API_HASH", "") # ⚠️ Required
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "") # ⚠️ Required
    ADMIN = int(os.environ.get("ADMIN, "")) # ⚠️ Required
    STRING_SESSION = os.environ.get("STRING_SESSION", "") # ⚠️ Required
    PORT = int(os.environ.get("PORT", "8080"))
