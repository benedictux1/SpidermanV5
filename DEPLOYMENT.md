# Deployment Guide for Kith Platform on Render

This guide will walk you through deploying the Kith Platform on Render.com so you can access it from any computer or phone.

## Prerequisites

1. A GitHub account (or GitLab/Bitbucket)
2. A Render.com account (free tier available)
3. API keys for AI services:
   - Gemini API key (recommended) - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - OpenAI API key (optional, as fallback) - Get from [OpenAI Platform](https://platform.openai.com/api-keys)

## Step 1: Prepare Your Repository

1. **Initialize Git** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit - ready for deployment"
   ```

2. **Push to GitHub**:
   - Create a new repository on GitHub
   - Push your code:
     ```bash
     git remote add origin https://github.com/yourusername/kith-platform.git
     git branch -M main
     git push -u origin main
     ```

## Step 2: Create PostgreSQL Database on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `kith-platform-db`
   - **Database**: `kith_platform`
   - **User**: `kith_user`
   - **Region**: Choose closest to you
   - **Plan**: Free (for testing) or Starter ($7/month for production)
4. Click **"Create Database"**
5. **Important**: Copy the **Internal Database URL** (you'll need this later)

## Step 3: Deploy Web Service on Render

### Option A: Using render.yaml (Recommended - Automated)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml` and create:
   - Web service
   - PostgreSQL database
   - Persistent disk for ChromaDB
5. Review and click **"Apply"**

### Option B: Manual Setup

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `kith-platform`
   - **Environment**: `Python 3`
   - **Region**: Same as database
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave empty (or `.` if needed)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 main:app`
   - **Plan**: Free (for testing) or Starter ($7/month for production)

5. **Add Environment Variables**:
   - `FLASK_ENV` = `production`
   - `FLASK_SECRET_KEY` = Generate a random secret (use: `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `DATABASE_URL` = Your PostgreSQL Internal Database URL from Step 2
   - `CHROMA_DB_DIR` = `/opt/render/project/src/chroma_db`
   - `GEMINI_API_KEY` = Your Gemini API key
   - `GEMINI_MODEL` = `gemini-2.0-flash-exp` (optional, this is the default)
   - `OPENAI_API_KEY` = Your OpenAI API key (optional, for fallback)

6. **Add Persistent Disk** (for ChromaDB):
   - Go to **"Disks"** tab
   - Click **"Add Disk"**
   - Name: `chromadb-storage`
   - Mount Path: `/opt/render/project/src/chroma_db`
   - Size: 1 GB (minimum)

7. Click **"Create Web Service"**

## Step 4: Initialize Database

After the service is deployed:

1. Go to your web service on Render
2. Click on **"Shell"** tab
3. Run the following commands:
   ```bash
   python -c "from app import create_app; from app.utils.database import DatabaseManager; from app.models import User, Contact, RawNote, SynthesizedEntry; app = create_app('production'); db = DatabaseManager(); db.create_all_tables(); print('Database initialized!')"
   ```

   Or create a simple initialization script:
   ```bash
   python -c "
   from app import create_app
   from app.utils.database import DatabaseManager
   from app.models import User, Contact, RawNote, SynthesizedEntry
   
   app = create_app('production')
   db = DatabaseManager()
   db.create_all_tables()
   print('✅ Database tables created successfully!')
   "
   ```

4. **Create your first admin user**:
   ```bash
   python -c "
   from app import create_app
   from app.models import User
   from app.utils.database import DatabaseManager
   from werkzeug.security import generate_password_hash
   
   app = create_app('production')
   db = DatabaseManager()
   
   with db.get_session() as session:
       # Check if admin exists
       admin = session.query(User).filter(User.username == 'admin').first()
       if not admin:
           admin = User(
               username='admin',
               password_hash=generate_password_hash('your-secure-password-here'),
               role='admin',
               is_active=True
           )
           session.add(admin)
           print('✅ Admin user created!')
       else:
           print('Admin user already exists')
   "
   ```

## Step 5: Access Your Application

1. Once deployed, Render will provide a URL like: `https://kith-platform.onrender.com`
2. Visit the URL in your browser
3. Log in with your admin credentials
4. Your app is now accessible from any device!

## Step 6: Set Up Custom Domain (Optional)

1. Go to your web service settings
2. Click **"Custom Domains"**
3. Add your domain
4. Follow Render's DNS configuration instructions

## Troubleshooting

### Database Connection Issues
- Ensure `DATABASE_URL` uses the **Internal Database URL** (not External)
- Check that the database URL format is correct: `postgresql://user:password@host:port/database`
- Render automatically converts `postgres://` to `postgresql://` in the code

### ChromaDB Storage Issues
- Ensure persistent disk is mounted at `/opt/render/project/src/chroma_db`
- Check disk size if you're running out of space

### Build Failures
- Check build logs in Render dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify Python version compatibility

### Application Errors
- Check logs in Render dashboard
- Verify all environment variables are set correctly
- Ensure database tables are initialized

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `FLASK_ENV` | Yes | Set to `production` |
| `FLASK_SECRET_KEY` | Yes | Random secret key for sessions |
| `DATABASE_URL` | Yes | PostgreSQL connection string (auto-provided by Render) |
| `CHROMA_DB_DIR` | No | ChromaDB storage path (default: `/opt/render/project/src/chroma_db`) |
| `GEMINI_API_KEY` | Recommended | Google Gemini API key |
| `GEMINI_MODEL` | No | Gemini model name (default: `gemini-2.0-flash-exp`) |
| `OPENAI_API_KEY` | Optional | OpenAI API key (fallback) |

## Cost Estimate

**Free Tier** (for testing):
- Web Service: Free (spins down after 15 min inactivity)
- PostgreSQL: Free (limited to 90 days)
- Disk: Free (1 GB)

**Starter Plan** (recommended for production):
- Web Service: $7/month (always on)
- PostgreSQL: $7/month (persistent)
- Disk: Included
- **Total: ~$14/month**

## Next Steps

1. Set up automated backups for your database
2. Configure monitoring and alerts
3. Set up CI/CD for automatic deployments
4. Consider upgrading to higher plans for better performance

## Support

If you encounter issues:
1. Check Render logs
2. Review application logs
3. Verify environment variables
4. Check database connectivity

---

**Congratulations!** Your Kith Platform is now live and accessible from anywhere! 🎉

