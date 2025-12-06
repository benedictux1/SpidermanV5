# How to Set Python Version in Render

Render is currently using Python 3.13.4, but we need Python 3.12 for compatibility. Here's how to fix it:

## Option 1: Set Python Version in Service Settings (Recommended)

1. Go to your Render service: https://dashboard.render.com/web/srv-d4pg253uibrs73esjra0
2. Click on **"Settings"** tab
3. Scroll down to **"Environment"** section
4. Look for **"Python Version"** or **"Runtime"** setting
5. If available, change it to **Python 3.12.7** or **Python 3.12**
6. Save changes
7. This will trigger a new deployment

## Option 2: Add Environment Variable

If the above doesn't work, you can try adding an environment variable:

1. Go to your service → **"Environment"** tab
2. Click **"Add Environment Variable"**
3. Key: `PYTHON_VERSION`
4. Value: `3.12.7`
5. Save and redeploy

## Option 3: runtime.txt (Should work but might need service restart)

The `runtime.txt` file should work, but Render might need:
- The file to be in the root directory (✅ it is)
- The format to be exactly `python-3.12.7` (✅ it is)
- A manual redeploy after adding the file

Try manually triggering a redeploy:
1. Go to **"Manual Deploy"** tab
2. Click **"Deploy latest commit"**

## Why This Matters

- Python 3.13 is very new and some packages don't have full support yet
- `psycopg` (psycopg3) works better with Python 3.12
- Python 3.12 is the current stable LTS version

---

**After setting Python version, the build should succeed!**

