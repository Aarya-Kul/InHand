from dotenv import load_dotenv
from pathlib import Path
import os

_DIR = Path(__file__).resolve().parent
load_dotenv(_DIR / ".env")
load_dotenv(_DIR / "env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")

# placeholder | always_pass | always_fail | openai
# If OPENAI_API_KEY is set, openai_client uses the model even when this is placeholder.
JUDGE_MODE = os.getenv("JUDGE_MODE", "placeholder")

# Demo: planner may propose up to 4; we always run 2–3.
MIN_CHALLENGES = int(os.getenv("MIN_CHALLENGES", "2"))
MAX_CHALLENGES = int(os.getenv("MAX_CHALLENGES", "3"))
PLAN_POOL = 4
MAX_TAKES_PER_PRODUCT = int(os.getenv("MAX_TAKES_PER_PRODUCT", "4"))
MAX_CONSECUTIVE_FAILS = int(os.getenv("MAX_CONSECUTIVE_FAILS", "2"))

# all = every challenge on a product must pass to refund it
# majority = more than half the challenges must pass
PRODUCT_PASS_MODE = os.getenv("PRODUCT_PASS_MODE", "all")

CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
