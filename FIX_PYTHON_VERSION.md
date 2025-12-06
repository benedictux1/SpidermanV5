# Fix for Python 3.13 Compatibility Issue

## Problem
The error `undefined symbol: _PyInterpreterState_Get` occurs because `psycopg2-binary` doesn't have proper Python 3.13 support yet.

## Solution Applied

1. **Switched to `psycopg` (psycopg3)**: Modern PostgreSQL driver with better Python 3.13+ support
2. **Added `runtime.txt`**: Pins Python to 3.12.7 for stability (Render will use this)
3. **Updated connection strings**: Explicitly use `postgresql+psycopg://` driver

## Changes Made

### requirements.txt
- Changed: `psycopg2-binary==2.9.9` → `psycopg[binary]==3.2.0`

### runtime.txt (NEW)
- Added: `python-3.12.7` (ensures Render uses Python 3.12)

### app/utils/database.py
- Updated connection string to use `postgresql+psycopg://` driver

### app/__init__.py
- Updated connection string to use `postgresql+psycopg://` driver

## Next Steps

1. **Commit and push these changes**:
   ```bash
   git add .
   git commit -m "Fix Python 3.13 compatibility - switch to psycopg3 and pin Python 3.12"
   git push origin main
   ```

2. **Wait for Render to redeploy** (automatic if auto-deploy is enabled)

3. **Try the database initialization again**:
   ```bash
   python init_db.py --create-admin --username admin --password 123
   ```

   Or use the simpler script:
   ```bash
   python create_admin.py --username admin --password 123
   ```

## Alternative: If Issues Persist

If you still encounter issues, you can manually set Python version in Render:

1. Go to your service settings
2. Under "Environment", you might see Python version options
3. Or add environment variable: `PYTHON_VERSION=3.12.7`

But the `runtime.txt` file should handle this automatically.

---

**Note**: The `runtime.txt` file tells Render which Python version to use. This ensures compatibility with all packages.

