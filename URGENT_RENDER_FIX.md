# 🚨 URGENT: Manual Render Override Required

## The Problem
Your git push succeeded but Render is STILL using the old command:
- ❌ Still running: `gunicorn --bind 0.0.0.0:$PORT --workers 2 app:app`
- ✅ Should run: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 wsgi:app`

## Immediate Fix: Override Start Command in Render

### Step 1: Go to Render Settings
1. Open https://dashboard.render.com
2. Click on your Calculator Suite service
3. Click on **"Settings"** tab

### Step 2: Find Start Command Section
1. Scroll down to **"Build & Deploy"** section
2. Look for **"Start Command"** field
3. It might be showing: `gunicorn --bind 0.0.0.0:$PORT --workers 2 app:app`

### Step 3: Update Start Command
1. **Clear the current command**
2. **Paste this exactly**:
   ```
   gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 wsgi:app
   ```
3. **Click "Save Changes"**

### Step 4: Trigger Manual Deploy
1. Go back to the service dashboard
2. Click **"Manual Deploy"** button
3. Select **"Deploy latest commit"**
4. Click **"Deploy"**

## Alternative Commands to Try

If the above doesn't work, try these alternatives:

### Option 1: Direct Python
```
python wsgi.py
```

### Option 2: Module path
```
gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --chdir /opt/render/project/src wsgi:app
```

### Option 3: Python module
```
python -m gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 wsgi:app
```

## Why This is Happening
1. Render might be caching the old Procfile
2. There might be a start command override in settings
3. The deployment might not be picking up the new files

## Verification
After making this change:
- New deployment should start
- Look for: `Running 'gunicorn ... wsgi:app'`
- No more import errors
- Service goes "Live"

---

**This manual override will fix the issue immediately while we investigate why Render isn't using the updated Procfile.**