# Quick Fix: Set Python 3.12 in Render

Since you only see "Python 3" in the settings, here's the fastest way to fix it:

## Step 1: Go to Environment Tab

1. In the left sidebar, click **"Environment"** (under "MANAGE" section)
2. You should see a list of your current environment variables

## Step 2: Add Python Version

1. Click **"Add Environment Variable"** button
2. Enter:
   - **Key**: `PYTHON_VERSION`
   - **Value**: `3.12.7`
3. Click **"Save Changes"**

## Step 3: Redeploy

After adding the environment variable:

1. Go to **"Manual Deploy"** tab (in the top navigation)
2. Click **"Deploy latest commit"**
3. This will trigger a new build with Python 3.12

## Alternative: If Environment Variable Doesn't Work

If `PYTHON_VERSION` doesn't work, the `runtime.txt` file should work, but you need to:

1. Make sure `runtime.txt` is in your repo root (✅ it is)
2. Manually trigger a redeploy:
   - Go to **"Manual Deploy"** tab
   - Click **"Deploy latest commit"**

The `runtime.txt` file tells Render which Python version to use, but sometimes it only applies on a fresh deploy or manual redeploy.

---

**After redeploying, check the build logs - it should say "Installing Python version 3.12.7" instead of 3.13.4**

