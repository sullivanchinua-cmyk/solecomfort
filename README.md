# SoleComfort – Live Search Shoe Store

Search any keyword → collects real images with pinscrape → shows products.

## Deploy on Render (Free)

1. Go to [https://render.com](https://render.com) and create a free account
2. Click **New +** → **Web Service**
3. Connect your GitHub repo (or use "Public Git repository")
4. Settings:

   - **Name**: solecomfort (or anything)
   - **Runtime**: Python 3
   - **Build Command**:
     ```
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```
     gunicorn app:app
     ```
   - **Instance Type**: Free

5. Click **Create Web Service**

After it deploys, you will get a free link like:
`https://solecomfort-xxxx.onrender.com`

### Notes
- Free plan sleeps after 15 minutes of inactivity (first load can be slow)
- pinscrape sometimes fails on complex keywords → try simple words like "slippers", "sneakers", "sandals"
- Cache is in-memory (resets when the service sleeps)