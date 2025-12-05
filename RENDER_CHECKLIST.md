# Render Setup Checklist

Use this checklist while setting up your deployment. Check off each item as you complete it.

## Pre-Deployment
- [ ] GitHub repository created and code pushed
- [ ] Render.com account created
- [ ] Gemini API key obtained from [Google AI Studio](https://makersuite.google.com/app/apikey)
- [ ] OpenAI API key obtained (optional, from [OpenAI Platform](https://platform.openai.com/api-keys))

## Step 1: PostgreSQL Database
- [ ] Clicked "New +" → "PostgreSQL"
- [ ] Set Name: `kith-platform-db`
- [ ] Set Database: `kith_platform`
- [ ] Set User: `kith_user`
- [ ] Selected Region (same as web service)
- [ ] Selected Plan (Free for testing, Starter for production)
- [ ] Clicked "Create Database"
- [ ] **Copied Internal Database URL** (save this!)

## Step 2: Web Service
- [ ] Clicked "New +" → "Web Service"
- [ ] Connected GitHub account
- [ ] Selected repository: `SpidermanV5`
- [ ] Set Name: `kith-platform`
- [ ] Set Region (same as database)
- [ ] Set Branch: `main`
- [ ] Set Build Command: `pip install -r requirements.txt`
- [ ] Set Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 main:app`
- [ ] Selected Plan (Free for testing, Starter for production)

## Step 3: Environment Variables
Add each of these in the Environment Variables section:

- [ ] `FLASK_ENV` = `production`
- [ ] `FLASK_SECRET_KEY` = (generated 64-char hex string)
- [ ] `DATABASE_URL` = (Internal Database URL from Step 1)
- [ ] `CHROMA_DB_DIR` = `/opt/render/project/src/chroma_db`
- [ ] `GEMINI_API_KEY` = (your Gemini API key)
- [ ] `GEMINI_MODEL` = `gemini-2.0-flash-exp` (optional)
- [ ] `OPENAI_API_KEY` = (your OpenAI API key, optional)

## Step 4: Persistent Disk
- [ ] Clicked "Disks" tab in web service
- [ ] Clicked "Add Disk"
- [ ] Set Name: `chromadb-storage`
- [ ] Set Mount Path: `/opt/render/project/src/chroma_db`
- [ ] Set Size: `1` GB
- [ ] Clicked "Add Disk"
- [ ] Redeployed service (Manual Deploy → Deploy latest commit)

## Step 5: Database Initialization
- [ ] Opened "Shell" tab in web service
- [ ] Ran: `python init_db.py --create-admin --username admin --password YourSecurePassword123`
- [ ] Verified output shows "Database initialization complete!"
- [ ] Saved admin password securely

## Step 6: Verification
- [ ] Service deployed successfully (green status)
- [ ] Visited application URL (e.g., `https://kith-platform.onrender.com`)
- [ ] Login page loads
- [ ] Can log in with admin credentials
- [ ] Health check works: `https://your-app-url.onrender.com/health`
- [ ] Can create a contact
- [ ] Can add a note

## Post-Deployment
- [ ] Tested all major features
- [ ] Saved application URL
- [ ] Saved admin credentials securely
- [ ] Considered upgrading to Starter plan for production use

---

## Quick Commands Reference

### Generate Secret Key
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Initialize Database (in Render Shell)
```bash
python init_db.py --create-admin --username admin --password YourSecurePassword123
```

### Verify Database (in Render Shell)
```bash
python -c "from app import create_app; from app.utils.database import DatabaseManager; from app.models import User; app = create_app('production'); db = DatabaseManager(); session = db.get_session().__enter__(); users = session.query(User).all(); print(f'Found {len(users)} users')"
```

---

**Need help?** See `RENDER_SETUP_GUIDE.md` for detailed step-by-step instructions.

