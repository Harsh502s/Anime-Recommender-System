# 🚀 Deployment Guide: Ethereal Anime Recommender

This guide covers deploying your full-stack application on the **Free Tier** using **Vercel** (Frontend) and **Render** (Backend).

---

## 📦 1. Prepare for Push

Because the AI model requires about 100MB of pre-calculated vectors (`model_artifacts/`), and free-tier servers are too weak to calculate them on the fly, you should commit these files to your repository.

1.  Open your `.gitignore`.
2.  **Temporarily remove** or comment out these lines:
    ```text
    # model_artifacts/
    # *.pkl
    # *.index
    ```
3.  Ensure your `backend/run.py` is updated to handle the dynamic `$PORT` (I have already done this for you).

---

## 🧠 2. Backend Deployment (Render)

Render is excellent for hosting Flask APIs with ML dependencies.

1.  Go to [dashboard.render.com](https://dashboard.render.com) and create a free account.
2.  Click **New +** → **Web Service**.
3.  Connect your GitHub repository.
4.  **Configure the Service:**
    - **Name:** `anime-recommender-api`
    - **Runtime:** `Python 3`
    - **Build Command:** `pip install -r requirements.txt`
    - **Start Command:** `gunicorn -w 1 -b 0.0.0.0:$PORT backend.run:app`
5.  **Environment Variables:**
    - Click the **Environment** tab.
    - Add `PYTHON_VERSION`: `3.11.0` (or `3.10.0`)
    - Add `FLASK_ENV`: `production`
6.  Click **Deploy Web Service**.
7.  **Copy the URL** (e.g., `https://anime-recommender-api.onrender.com`).

---

## 🎨 3. Frontend Deployment (Vercel)

Vercel is the gold standard for React/Vite deployment.

1.  Go to [vercel.com](https://vercel.com) and sign in with GitHub.
2.  Click **Add New** → **Project**.
3.  Import your repository.
4.  **Configure Project (CRITICAL):**
    - **Root Directory:** Edit this and select the `client` folder.
    - **Framework Preset:** `Vite` (Vercel usually detects this).
    - **Output Directory:** If it asks, ensure it is set to `dist` (NOT `build`).
5.  **Environment Variables:**
    - Add `VITE_API_BASE_URL`: Paste your Render API URL here and append `/api/v1` (e.g., `https://anime-recommender-api.onrender.com/api/v1`)
6.  Click **Deploy**.

> [!NOTE]
> I have added a `client/vercel.json` file which automatically handles React Router "404 on refresh" errors for you.

---

## 🛠️ 4. Handling Deployment Issues

### Cold Starts
Render's free tier "sleeps" after 15 minutes of inactivity. The first request to your frontend might take 30–60 seconds to respond as the backend wakes up and loads the 100MB model into memory.

### Memory Limits
If Render crashes with an "Out of Memory" (OOM) error, try reducing the number of Gunicorn workers from `-w 1` to a lighter configuration, or switch to **Koyeb** (another free tier) which offers slightly more baseline RAM.

---

## ✅ Deployment Summary
| Component | Platform | URL Type |
| :--- | :--- | :--- |
| **API** | Render | `https://your-app.onrender.com` |
| **UI** | Vercel | `https://your-app.vercel.app` |

**Your app is now live! 🌎**
