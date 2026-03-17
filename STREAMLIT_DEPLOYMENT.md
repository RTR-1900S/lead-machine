# 🚀 Deploy to Streamlit Cloud (5 Minutes)

## What You'll Get
- **Live URL**: `https://lead-machine-xxxxx.streamlit.app`
- **Accessible from anywhere**: Any device, any browser
- **Free tier**: $0/month for this app
- **No installation needed**: Your wife just opens the URL

---

## ✅ STEP-BY-STEP DEPLOYMENT

### STEP 1: Create GitHub Repository
```bash
cd C:\Users\b0yra\Desktop\Apps\lead-machine

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Lead Machine app - ready for deployment"

# Create repo on GitHub:
# 1. Go to https://github.com/new
# 2. Name it "lead-machine"
# 3. Keep it PRIVATE
# 4. Click Create

# Add remote and push (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/lead-machine.git
git branch -M main
git push -u origin main
```

---

### STEP 2: Deploy to Streamlit Cloud
1. **Go to**: https://share.streamlit.io/
2. **Click**: "New app" (top right button)
3. **Fill in**:
   - Repository: `YOUR_USERNAME/lead-machine`
   - Branch: `main`
   - Main file path: `app.py`
4. **Click**: "Deploy"

**Status**: Yellow → Deploying → Green ✅ (2-3 minutes)

---

### STEP 3: Add Gemini API Key to Secrets
1. **After deployment succeeds**, click the **⚙️ Settings** icon (top right)
2. **Click**: "Secrets"
3. **Paste this exactly**:
```
GEMINI_API_KEY=YOUR_ACTUAL_API_KEY_HERE
```
Replace `YOUR_ACTUAL_API_KEY_HERE` with your real key from `config/.env`

4. **Save** and app will restart automatically

---

### STEP 4: Done! ✅
**Your app is now LIVE**

- Share this URL with your wife: `https://lead-machine-xxxxx.streamlit.app`
- She can use it from any device
- No installation needed
- Works on phone, tablet, desktop

---

## 🎯 How Your Wife Uses It

1. Open the URL in her browser
2. See your MOMENTIV MEDIA logo
3. Click a business type or enter custom
4. Select "Top Paying" filter
5. Enter city
6. Click "Run Search"
7. Go to "Score Leads" tab
8. Click "Start Scoring"
9. Download Excel results
10. Done!

---

## 🔧 Troubleshooting

**"Scraper failed" error:**
- Google Maps scraper needs to be installed on your Windows machine (already done)
- Streamlit Cloud runs in the cloud, but uses YOUR machine to scrape
- This only works if your Windows machine stays running
- Consider running scraper locally, uploading CSVs to Streamlit instead

**Better approach for Always-On:**
- Run scraper locally on your Windows machine
- Upload CSVs to a folder
- Have Streamlit Cloud read those files
- This way it works 24/7 without your machine running

**"GEMINI_API_KEY not found":**
- Make sure you added it in Streamlit Secrets (Step 3)
- Restart the app after adding

---

## 📋 What Each File Does

- `app.py` - Main Streamlit app (web interface)
- `scraper_runner.py` - Runs Google Maps scraper
- `lead_scorer.py` - Scores with Gemini API
- `requirements.txt` - Python dependencies
- `.streamlit/config.toml` - Streamlit configuration
- `.gitignore` - Tells Git what NOT to upload
- `logo.png` - Your MOMENTIV MEDIA logo

---

## 🎓 Advanced: Run Scraper 24/7

For production use where she needs search to work anytime:

**Option 1: Use Windows Task Scheduler**
- Schedule scraper to run daily
- Upload results to a shared folder
- App reads from that folder

**Option 2: Use cloud scraper**
- Use a service like Heroku to run scraper on schedule
- Upload results to cloud storage (AWS S3, Google Cloud)
- Streamlit reads from cloud

For now, test with the free tier and we can optimize later!

---

## ✨ SUMMARY

| What | Where | Cost |
|------|-------|------|
| Web App | Streamlit Cloud | FREE |
| Domain | `lead-machine-xxxxx.streamlit.app` | FREE |
| Uptime | 24/7 (Streamlit handles) | FREE |
| Total | - | **$0/month** |

Your wife gets a professional SaaS app with ZERO setup or installation! 🚀
