# Automation Guide for Render Setup

This guide shows what has been automated and what needs manual steps.

## ✅ What's Automated

### 1. Database Table Auto-Initialization
**Status**: ✅ **AUTOMATED**

Database tables are now automatically created when the app starts if they don't exist. No manual initialization needed!

- Tables are created automatically on first app startup
- Safe to run multiple times (only creates if missing)
- No action required from you

### 2. Environment Variables
**Status**: ⚠️ **PARTIALLY AUTOMATED** (if you've already set them up)

If you've already added environment variables in Step 2, you're done! If not, you can update them using the Render MCP tools.

## ⚠️ What Needs Manual Steps

### 1. Persistent Disk for ChromaDB
**Status**: ❌ **MUST BE DONE MANUALLY**

Render MCP doesn't have a tool for adding persistent disks. You need to do this in the Render dashboard:

1. Go to your web service: https://dashboard.render.com/web/srv-d4pg253uibrs73esjra0
2. Click **"Disks"** tab
3. Click **"Add Disk"**
4. Fill in:
   - **Name**: `chromadb-storage`
   - **Mount Path**: `/opt/render/project/src/chroma_db`
   - **Size**: `1` GB
5. Click **"Add Disk"**
6. **Important**: After adding, go to **"Manual Deploy"** tab and click **"Deploy latest commit"** to mount the disk

### 2. Create Admin User
**Status**: ✅ **SIMPLIFIED** (easy one-command script)

I've created a simple script `create_admin.py` that makes this super easy:

**Option A: Interactive (Recommended)**
```bash
python create_admin.py
```
It will prompt you for the password (input is hidden).

**Option B: Command Line**
```bash
python create_admin.py --username admin --password YourSecurePassword123
```

**Where to run this:**
- In Render Dashboard → Your Service → **"Shell"** tab
- Or locally if you have database access

---

## Quick Setup Summary

### Already Done ✅
- [x] PostgreSQL database created
- [x] Web service created
- [x] Environment variables configured
- [x] Database tables auto-initialize on startup

### Still Need To Do ⚠️

1. **Add Persistent Disk** (5 minutes - manual):
   - Dashboard → Disks → Add Disk
   - Name: `chromadb-storage`
   - Mount: `/opt/render/project/src/chroma_db`
   - Size: 1 GB
   - Redeploy after adding

2. **Create Admin User** (1 minute - automated script):
   ```bash
   python create_admin.py
   ```
   Run this in Render Shell tab

---

## Testing Your Setup

After completing the above:

1. **Check Health**: Visit `https://spidermanv5.onrender.com/health`
   - Should return: `{"status": "healthy", ...}`

2. **Check Database**: Tables should exist automatically
   - No manual initialization needed!

3. **Login**: Visit `https://spidermanv5.onrender.com`
   - Use the admin credentials you created

---

## Need Help?

- **Service URL**: https://spidermanv5.onrender.com
- **Service Dashboard**: https://dashboard.render.com/web/srv-d4pg253uibrs73esjra0
- **Database Dashboard**: https://dashboard.render.com/d/dpg-d4pfv8buibrs73eshmug-a

---

## What Changed in the Code

1. **`app/__init__.py`**: Added automatic database table initialization on startup
2. **`create_admin.py`**: New simple script for creating admin users
3. **Auto-initialization**: Tables are created automatically - no manual `init_db.py` needed for tables (only for admin user)

---

**You're almost there! Just add the disk and create your admin user! 🚀**

