# Detailed Render Setup Guide - Step by Step

This guide provides exact, click-by-click instructions for setting up your Kith Platform on Render.

---

## Step 1: Create PostgreSQL Database

### 1.1 Navigate to Render Dashboard
1. Go to [https://dashboard.render.com](https://dashboard.render.com)
2. Log in (or create an account if needed)

### 1.2 Create New PostgreSQL Database
1. Click the **"New +"** button (top right corner)
2. Select **"PostgreSQL"** from the dropdown menu

### 1.3 Configure Database Settings
Fill in the following fields:

- **Name**: `kith-platform-db`
- **Database**: `kith_platform` (leave as default or change)
- **User**: `kith_user` (leave as default or change)
- **Region**: Choose the region closest to you (e.g., `Oregon`, `Frankfurt`, `Singapore`)
- **PostgreSQL Version**: Leave as default (usually latest)
- **Plan**: 
  - For testing: Select **"Free"** (expires after 90 days)
  - For production: Select **"Starter"** ($7/month, persistent)

### 1.4 Create and Save Database URL
1. Click **"Create Database"**
2. Wait for the database to be provisioned (takes 1-2 minutes)
3. Once ready, click on your database name to open its details
4. **IMPORTANT**: Find the **"Internal Database URL"** section
   - It looks like: `postgres://kith_user:password@dpg-xxxxx-a.oregon-postgres.render.com/kith_platform`
   - **Copy this entire URL** - you'll need it in Step 2
   - ⚠️ Use the **Internal** URL, not the External one (for security)

---

## Step 2: Create Web Service

### 2.1 Create New Web Service
1. In Render Dashboard, click **"New +"** button again
2. Select **"Web Service"** from the dropdown

### 2.2 Connect GitHub Repository
1. If not already connected:
   - Click **"Connect account"** or **"Configure account"**
   - Authorize Render to access your GitHub
   - Select your GitHub account
2. In the repository list, find and select **"SpidermanV5"**
3. Click **"Connect"**

### 2.3 Configure Basic Settings
Fill in these fields:

- **Name**: `kith-platform` (or any name you prefer)
- **Region**: Choose the **same region** as your database (for better performance)
- **Branch**: `main` (should be auto-detected)
- **Root Directory**: Leave **empty** (or `.` if needed)
- **Runtime**: `Python 3` (should be auto-detected)

### 2.4 Configure Build & Start Commands
Scroll down to **"Build & Deploy"** section:

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 main:app
```

### 2.5 Select Plan
- **Plan**: 
  - For testing: **"Free"** (spins down after 15 min inactivity)
  - For production: **"Starter"** ($7/month, always on)

### 2.6 Add Environment Variables
Scroll to **"Environment Variables"** section and click **"Add Environment Variable"** for each:

1. **FLASK_ENV**
   - Key: `FLASK_ENV`
   - Value: `production`

2. **FLASK_SECRET_KEY**
   - Key: `FLASK_SECRET_KEY`
   - Value: Generate a secure random key:
     - Open terminal and run: `python -c "import secrets; print(secrets.token_hex(32))"`
     - Copy the output (64 character hex string)
     - Paste as the value - da5709ddf4f3bb9dcc6cca502ff4bb97a41e6821796c95c4dea7d792c3edf379
     
3. **DATABASE_URL**
   - Key: `DATABASE_URL`
   - Value: Paste the **Internal Database URL** you copied from Step 1.4
     - Example: `postgres://kith_user:password@dpg-xxxxx-a.oregon-postgres.render.com/kith_platform`
   - ⚠️ Render may show it as `postgres://` but our code converts it to `postgresql://` automatically

4. **CHROMA_DB_DIR**
   - Key: `CHROMA_DB_DIR`
   - Value: `/opt/render/project/src/chroma_db`

5. **GEMINI_API_KEY** (Required for AI features)
   - Key: `GEMINI_API_KEY`
   - Value: Your Gemini API key
   - How to get it:
     1. Go to [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
     2. Sign in with Google account
     3. Click **"Create API Key"**
     4. Copy the key and paste here

6. **GEMINI_MODEL** (Optional)
   - Key: `GEMINI_MODEL`
   - Value: `gemini-2.0-flash-exp` (or leave empty to use default)

7. **OPENAI_API_KEY** (Optional - fallback if Gemini fails)
   - Key: `OPENAI_API_KEY`
   - Value: Your OpenAI API key
   - How to get it:
     1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
     2. Sign in and click **"Create new secret key"**
     3. Copy the key and paste here

### 2.7 Create the Service
1. Scroll to the bottom
2. Click **"Create Web Service"**
3. Wait for the first deployment to complete (takes 3-5 minutes)

---

## Step 3: Add Persistent Disk for ChromaDB

### 3.1 Navigate to Your Web Service
1. In Render Dashboard, click on your web service name (`kith-platform`)

### 3.2 Add Disk
1. Click on the **"Disks"** tab (in the top navigation)
2. Click **"Add Disk"** button

### 3.3 Configure Disk Settings
Fill in:

- **Name**: `chromadb-storage`
- **Mount Path**: `/opt/render/project/src/chroma_db`
- **Size**: `1` GB (minimum, increase if needed later)

### 3.4 Create Disk
1. Click **"Add Disk"**
2. ⚠️ **Important**: After adding the disk, you need to **redeploy** your service for it to be mounted
3. Go to **"Manual Deploy"** tab
4. Click **"Deploy latest commit"** (or wait for auto-deploy)

---

## Step 4: Initialize Database

### 4.1 Open Shell
1. In your web service dashboard, click the **"Shell"** tab (top navigation)
2. Wait for the shell to connect

### 4.2 Run Database Initialization
In the shell, run:

```bash
python init_db.py --create-admin --username admin --password YourSecurePassword123
```

**Replace `YourSecurePassword123` with a strong password of your choice!**

Expected output:
```
Initializing database...
✅ Database tables created successfully!
✅ Admin user 'admin' created successfully!

✅ Database initialization complete!
```

### 4.3 Verify Database
You can verify tables were created by running:

```bash
python -c "from app import create_app; from app.utils.database import DatabaseManager; from app.models import User; app = create_app('production'); db = DatabaseManager(); session = db.get_session().__enter__(); users = session.query(User).all(); print(f'Found {len(users)} users'); print([u.username for u in users])"
```

---

## Step 5: Access Your Application

### 5.1 Get Your Application URL
1. In your web service dashboard, look at the top
2. You'll see a URL like: `https://kith-platform.onrender.com`
3. This is your application URL

### 5.2 Test the Application
1. Open the URL in your browser
2. You should see the login page
3. Log in with:
   - Username: `admin`
   - Password: The password you set in Step 4.2

### 5.3 Verify Health Check
Visit: `https://your-app-url.onrender.com/health`

You should see:
```json
{
  "status": "healthy",
  "timestamp": "2024-..."
}
```

---

## Troubleshooting

### Database Connection Issues
- **Error**: "Could not connect to database"
  - **Solution**: Verify `DATABASE_URL` uses the **Internal Database URL** (not External)
  - Check that database and web service are in the same region

### ChromaDB Storage Issues
- **Error**: "Permission denied" or "Directory not found"
  - **Solution**: 
    1. Verify disk is mounted at `/opt/render/project/src/chroma_db`
    2. Redeploy the service after adding the disk
    3. Check disk is attached in the "Disks" tab

### Build Failures
- **Error**: "Module not found" or "pip install failed"
  - **Solution**: 
    1. Check `requirements.txt` exists and has all dependencies
    2. Check build logs for specific error
    3. Verify Python version compatibility

### Application Won't Start
- **Error**: "Application failed to start"
  - **Solution**:
    1. Check logs in Render dashboard
    2. Verify all environment variables are set
    3. Check that `main:app` is correct (Flask app object)
    4. Verify Gunicorn is in requirements.txt

### First Request is Slow
- **Issue**: First request takes 30-60 seconds
  - **Explanation**: Free tier services spin down after 15 min inactivity
  - **Solution**: Upgrade to Starter plan ($7/month) for always-on service

---

## Quick Reference: Environment Variables Checklist

Before deploying, ensure you have:

- [ ] `FLASK_ENV` = `production`
- [ ] `FLASK_SECRET_KEY` = (64-char hex string)
- [ ] `DATABASE_URL` = (Internal PostgreSQL URL)
- [ ] `CHROMA_DB_DIR` = `/opt/render/project/src/chroma_db`
- [ ] `GEMINI_API_KEY` = (Your Gemini API key)
- [ ] `GEMINI_MODEL` = `gemini-2.0-flash-exp` (optional)
- [ ] `OPENAI_API_KEY` = (Your OpenAI API key, optional)

---

## Cost Summary

### Free Tier (Testing)
- Web Service: Free (spins down after 15 min)
- PostgreSQL: Free (expires after 90 days)
- Disk: Free (1 GB)
- **Total: $0/month** (but not suitable for production)

### Starter Plan (Production)
- Web Service: $7/month (always on)
- PostgreSQL: $7/month (persistent)
- Disk: Included
- **Total: ~$14/month**

---

## Next Steps After Deployment

1. ✅ Test all features (login, create contacts, add notes)
2. ✅ Set up a custom domain (optional)
3. ✅ Configure automated backups for database
4. ✅ Set up monitoring and alerts
5. ✅ Review security settings

---

**Congratulations! Your Kith Platform is now live! 🎉**

For questions or issues, check the logs in Render Dashboard → Your Service → Logs tab.

