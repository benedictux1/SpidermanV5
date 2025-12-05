# Quick Start: Deploy to Render

## 🚀 Fastest Path to Deployment

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Ready for Render deployment"
git remote add origin https://github.com/yourusername/kith-platform.git
git push -u origin main
```

### 2. Deploy on Render (5 minutes)

**Option A: Using Blueprint (Easiest)**
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repo
4. Render will auto-detect `render.yaml`
5. Add your API keys in environment variables:
   - `GEMINI_API_KEY` (get from [Google AI Studio](https://makersuite.google.com/app/apikey))
   - `OPENAI_API_KEY` (optional, for fallback)
6. Click **"Apply"**

**Option B: Manual Setup**
1. Create PostgreSQL database on Render
2. Create Web Service:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 main:app`
3. Add environment variables (see DEPLOYMENT.md)
4. Add persistent disk for ChromaDB

### 3. Initialize Database

Once deployed, open Render Shell and run:
```bash
python init_db.py --create-admin --username admin --password YourSecurePassword123
```

### 4. Access Your App

Visit your Render URL (e.g., `https://kith-platform.onrender.com`) and log in!

---

📖 **For detailed instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md)**

