#!/usr/bin/env python3
"""
Quick setup checker untuk troubleshoot bot issues
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

print("="*70)
print("🔍 TELETOSHEET BOT - SETUP CHECKER")
print("="*70)

issues = []
warnings = []
ok = []

# 1. Check .env file
print("\n📋 1. Checking .env file...")
if os.path.exists('.env'):
    ok.append(".env file exists")
    
    # Check required vars
    required_vars = [
        'TELEGRAM_API_ID',
        'TELEGRAM_API_HASH', 
        'TELEGRAM_PHONE',
        'CHANNEL_IDS',
        'GOOGLE_SHEET_ID'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == 'your_api_id_here' or value == 'your_sheet_id_here':
            issues.append(f"❌ {var} not configured in .env")
        else:
            ok.append(f"✅ {var} configured")
else:
    issues.append("❌ .env file not found!")

# 2. Check service-account.json
print("\n📋 2. Checking service-account.json...")
sa_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON', 'service-account.json')

if os.path.exists(sa_file):
    file_size = os.path.getsize(sa_file)
    
    if file_size == 0:
        issues.append(f"❌ {sa_file} is EMPTY (0 bytes) - Cannot connect to Google Sheets!")
        print(f"   ⚠️  File size: {file_size} bytes")
    elif file_size < 1000:
        warnings.append(f"⚠️  {sa_file} seems too small ({file_size} bytes)")
    else:
        ok.append(f"✅ {sa_file} exists ({file_size} bytes)")
        
        # Try to parse JSON
        try:
            with open(sa_file, 'r') as f:
                sa_data = json.load(f)
                
            if 'client_email' in sa_data:
                ok.append(f"✅ Service account email: {sa_data['client_email']}")
            else:
                warnings.append("⚠️  No client_email in service account JSON")
                
        except json.JSONDecodeError as e:
            issues.append(f"❌ Invalid JSON in {sa_file}: {e}")
else:
    issues.append(f"❌ {sa_file} not found!")

# 3. Check channel formats
print("\n📋 3. Checking channel formats...")
channel_formats = os.getenv('CHANNEL_FORMATS')
if channel_formats:
    ok.append(f"✅ CHANNEL_FORMATS configured: {channel_formats}")
else:
    warnings.append("⚠️  CHANNEL_FORMATS not set, will use DEFAULT_CHANNEL_FORMAT")

default_format = os.getenv('DEFAULT_CHANNEL_FORMAT', 'standard')
ok.append(f"✅ Default format: {default_format}")

# 4. Check logs directory
print("\n📋 4. Checking logs...")
if os.path.exists('logs'):
    log_file = 'logs/bot.log'
    if os.path.exists(log_file):
        log_size = os.path.getsize(log_file)
        ok.append(f"✅ Log file exists ({log_size} bytes)")
    else:
        warnings.append("⚠️  logs/bot.log not found (bot hasn't run yet?)")
else:
    warnings.append("⚠️  logs/ directory not found")

# Print summary
print("\n" + "="*70)
print("📊 SUMMARY")
print("="*70)

if ok:
    print(f"\n✅ OK ({len(ok)}):")
    for item in ok:
        print(f"   {item}")

if warnings:
    print(f"\n⚠️  WARNINGS ({len(warnings)}):")
    for item in warnings:
        print(f"   {item}")

if issues:
    print(f"\n❌ ISSUES ({len(issues)}):")
    for item in issues:
        print(f"   {item}")

# Final verdict
print("\n" + "="*70)
if issues:
    print("🔴 SETUP INCOMPLETE - Fix issues above before running bot")
    print("\n🔧 QUICK FIX:")
    
    if any('service-account.json' in issue and 'EMPTY' in issue for issue in issues):
        print("\n1. Download Service Account Key dari Google Cloud Console")
        print("   https://console.cloud.google.com/iam-admin/serviceaccounts")
        print("\n2. Copy file ke project:")
        print("   mv ~/Downloads/your-project-xxxx.json service-account.json")
        print("\n3. Verify:")
        print("   ls -lh service-account.json")
        print("\n4. Share Google Sheet dengan service account email")
        print("\n5. Restart bot:")
        print("   source venv/bin/activate && python main.py")
        
elif warnings and not issues:
    print("🟡 SETUP OK with warnings - Bot should run but check warnings")
else:
    print("🟢 SETUP COMPLETE - Ready to run!")
    print("\n🚀 Start bot with:")
    print("   source venv/bin/activate && python main.py")

print("="*70)
