# 🚀 Education Bot Deployment Guide - Render.com

## Quick Deploy to Render.com (Free Hosting)

### Step 1: Prepare Your Repository

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Environment Variables Needed:**
   - `TELEGRAM_BOT_TOKEN` - Get from @BotFather on Telegram
   - `GEMINI_API_KEY` - Get from Google AI Studio
   - `PORT` - Automatically set by Render (default: 10000)

### Step 2: Deploy on Render.com

1. **Sign up/Login to Render.com:**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub account

2. **Create New Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your education bot repository

3. **Configure Deployment:**
   - **Name:** `education-bot` (or your preferred name)
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
   - **Plan:** `Free` (0$/month with limitations)

4. **Set Environment Variables:**
   In the Environment Variables section, add:
   ```
   TELEGRAM_BOT_TOKEN = your_actual_bot_token_here
   GEMINI_API_KEY = your_actual_gemini_key_here
   ```

5. **Advanced Settings (Optional):**
   - **Python Version:** `3.9`
   - **Health Check Path:** `/health`
   - **Region:** Choose closest to your users

### Step 3: Deploy!

1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Your bot will be live at: `https://your-app-name.onrender.com`

## 🔧 Key Features Added for Deployment

### ✅ Health Check Endpoint
- **URL:** `/health`
- **Response:** `{"status": "healthy", "service": "Education Bot", "version": "1.0"}`
- **Purpose:** Render.com uses this to verify your service is running

### ✅ Environment Variables
- Secure configuration using `.env` files
- Production-ready with fallback values
- Easy to manage across different environments

### ✅ Web Server Integration
- Flask server runs alongside Telegram bot
- Handles health checks and status monitoring
- Required for Render.com's web service model

## 🚨 Free Tier Limitations

### Render.com Free Plan:
- ✅ **750 hours/month** (enough for 24/7 if you have only 1 service)
- ✅ **512 MB RAM** (sufficient for this bot)
- ✅ **Custom domains** supported
- ⚠️ **Sleeps after 15 minutes** of inactivity
- ⚠️ **Cold start delay** when waking up (30-60 seconds)
- ⚠️ **Build time limit:** 20 minutes

### Wake-Up Solutions:
1. **UptimeRobot** (free) - ping your health endpoint every 5 minutes
2. **Cron-job.org** (free) - scheduled HTTP requests
3. **Manual:** Users will wake it up when they message the bot

## 🔍 Monitoring Your Bot

### Check Bot Status:
- **Health Check:** `https://your-app-name.onrender.com/health`
- **Status:** `https://your-app-name.onrender.com/`
- **Render Dashboard:** Monitor logs, metrics, and deployments

### Logs Access:
- Render Dashboard → Your Service → Logs
- Real-time logs for debugging
- Error tracking and performance monitoring

## 🛠️ Troubleshooting

### Common Issues:

1. **Build Failed:**
   - Check `requirements.txt` format
   - Ensure Python version compatibility
   - Review build logs in Render dashboard

2. **Bot Not Responding:**
   - Verify `TELEGRAM_BOT_TOKEN` in environment variables
   - Check if service wake up from sleep
   - Review application logs

3. **Gemini API Errors:**
   - Verify `GEMINI_API_KEY` is correct
   - Check Google AI Studio quota
   - Ensure API key has proper permissions

4. **Service Sleeping:**
   - Set up monitoring with UptimeRobot
   - Consider upgrading to paid plan for always-on
   - Users can wake it by messaging the bot

## 🎯 Next Steps

### Optional Improvements:
1. **Custom Domain:** Connect your own domain
2. **Monitoring:** Set up UptimeRobot for keep-alive
3. **Database:** Add PostgreSQL for persistent user data
4. **CDN:** Use Render's CDN for static files
5. **Scaling:** Upgrade to paid plan for better performance

## 📞 Support

### If you need help:
1. **Render.com Docs:** [render.com/docs](https://render.com/docs)
2. **Community:** [community.render.com](https://community.render.com)
3. **Status Page:** [status.render.com](https://status.render.com)

---

## 🎉 Your Bot is Now Live!

Once deployed, your Education Bot with the amazing Mini App will be accessible 24/7 to users worldwide! 

**Features Available:**
- ✍️ Writing assistance
- 🗣️ Speaking practice  
- 📖 Digital library with 200+ books
- 👂 Listening resources (podcasts, movies, news)
- 🎮 **Mini App with 6 interactive games**
- 📊 Progress tracking and achievements

Share your bot with friends and start learning English together! 🌟