# 🎵 Connect to Full 81,343 Track Dataset

Your website is now connected to the Python backend with all **81,343 Spotify tracks**!

## Setup Instructions

### Step 1: Install Python API Dependencies

```bash
cd music-recommendation-system
pip install -r requirements-api.txt
```

### Step 2: Start the Python API Server

```bash
# From music-recommendation-system folder
python api.py
```

You should see:
```
✅ Models loaded successfully! Dataset: 81343 tracks  
🎵 API ready at http://localhost:5000
```

### Step 3: Website Automatically Connects

Once the Python API is running, your website will automatically:
1. ✅ Check for the Python API on `http://localhost:5000`
2. ✅ Call it for real recommendations from 81,343 tracks
3. ✅ Fall back to mock data if Python API is unavailable

---

## Testing Locally

1. **Start Python API:**
   ```bash
   cd music-recommendation-system
   python api.py
   ```

2. **In another terminal, start the website:**
   ```bash
   cd music-recommendation-website
   npm run dev
   ```

3. **Visit:** http://localhost:3000

4. **Try searching for any song!** You'll now get real recommendations from the 81,343 track dataset 🎸

---

## Production Deployment

### Option A: Deploy Python API to Railway (Recommended)

1. Go to https://railway.app
2. Create new project → Deploy from GitHub
3. Select your `music-recommendation-system` repo
4. Add environment variable:
   ```
   FLASK_ENV=production
   ```
5. Get your Railway URL: `https://xxxxx.railway.app`
6. Update website environment:
   ```
   NEXT_PUBLIC_PYTHON_API_URL=https://xxxxx.railway.app
   ```

### Option B: Deploy to Heroku

```bash
cd music-recommendation-system
heroku create
heroku config:set FLASK_ENV=production
git push heroku main
```

### Option C: Deploy to Render

1. Go to https://render.com
2. Create new Web Service
3. Connect GitHub repo
4. Build command: `pip install -r requirements-api.txt`
5. Start command: `python api.py`

---

## Environment Variables

Create `.env.local` in website folder:

```env
# For local development (disable to use mock data)
NEXT_PUBLIC_PYTHON_API_URL=http://localhost:5000
USE_PYTHON_API=true

# For production with deployed API
# NEXT_PUBLIC_PYTHON_API_URL=https://your-python-api.herokuapp.com
# USE_PYTHON_API=true
```

---

## API Endpoints

### `/api/recommend` (POST)
Get recommendations for a track
```bash
curl -X POST http://localhost:5000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"trackName": "Shape of You", "recommendations": 5}'
```

### `/api/search` (POST)
Search for tracks
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "shape", "limit": 10}'
```

### `/api/stats` (GET)
Get dataset statistics
```bash
curl http://localhost:5000/api/stats
```

### `/health` (GET)
Health check
```bash
curl http://localhost:5000/health
```

---

## Troubleshooting

### "Python API unavailable" error

**Check:**
1. Is Flask server running? (`python api.py`)
2. Is data file at `data/spotify_tracks.csv`?
3. Try: `curl http://localhost:5000/health`

**Solution:** Website will automatically fall back to mock data

### Server takes too long to start

Data loading takes 30-60 seconds on first run. Check console for progress.

### CORS errors

Flask-CORS is already configured. If issues persist:
- Check Python API is running
- Check URL in environment variable

---

## What's Next?

✅ Local testing with 81K tracks
✅ Deploy Python API to production
✅ Update website environment variables
✅ Go live with real AI recommendations!

**Questions?** Check the Python system README for more details.
