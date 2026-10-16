"""Dummy Supabase settings so modules import without a real project (the tests mock the database)."""
import os

os.environ.setdefault("SUPABASE_URL", "http://localhost:54321")
os.environ.setdefault("SUPABASE_KEY", "test-key-not-real")
os.environ.setdefault("SMTP_PORT", "1025")
