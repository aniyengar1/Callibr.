import os

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY", "")

if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL environment variable is not set")
if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY environment variable is not set")
