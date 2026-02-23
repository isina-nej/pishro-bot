#!/usr/bin/env python3
"""
Simple bot test script to verify aiogram works
"""
import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

# Try importing aiogram
try:
    import aiogram
    print(f"✅ aiogram imported successfully from: {aiogram.__file__}")
except ImportError as e:
    print(f"❌ aiogram import failed: {e}")
    print("\n⚠️  Note: You need to install dependencies first.")
    print("Run: pip3 install -r requirements.txt")
