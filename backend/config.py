from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")

# placeholder | always_pass | always_fail
# OpenAI teammate: switch to "openai" once integrations/openai_client.py is filled in.
JUDGE_MODE = os.getenv("JUDGE_MODE", "placeholder")

# all = every challenge on a product must pass to refund it
# majority = more than half the challenges must pass
PRODUCT_PASS_MODE = os.getenv("PRODUCT_PASS_MODE", "all")

CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
