# 🚀 Deployment Guide: Ethereal Anime Recommender

This guide covers deploying your full-stack application on the **Free Tier/Trial** using **Vercel** (Frontend) and **Railway** (Backend).

---

## 📦 1. Prepare for Push

Because the AI model requires about 100MB of pre-calculated vectors (`model_artifacts/`), and most free-tier servers don't have the compute to recreate them on the fly, you must commit these files to your repository.

1.  Open your `.gitignore`.
2.  **Temporarily remove** or comment out these lines so the model files can be pushed:
    ```text
    # model_artifacts/
    # *.pkl
    # *.index
    ```
3.  I have already added a `Procfile` in the root directory to tell Railway exactly how to start your Flask server.

---

## 🧠 2. Backend Deployment (Railway)

Railway is excellent for hosting Python APIs and handles scaling/ports automatically.

1.  Go to [railway.app](https://railway.app) and sign in with GitHub.
2.  Click **+ New Project** → **Deploy from GitHub repo**.
3.  Select your repository.
4.  **Configure the Service:**
    - Railway will detect the `Procfile` and use it automatically.
    - If it asks for a start command, ensure it's set to: `gunicorn -w 1 -b 0.0.0.0:$PORT backend.run:app`
5.  **Variables:**
    - Click the **Variables** tab.
    - Add `PYTHON_VERSION`: `3.11.0`
    - Add `PORT`: `8080` (Railway will provide this automatically, but setting a default is safe).
6.  **Copy the URL**: Once deployed, Railway provides a public domain (e.g., `https://anime-recommender-production.up.railway.app`).

---

## 🎨 3. Frontend Deployment (Vercel)

Vercel is the gold standard for React/Vite deployment.

1.  Go to [vercel.com](https://vercel.com) and import your repository.
2.  **Configure Project (CRITICAL):**
    - **Root Directory:** Edit this and select the `client` folder.
    - **Framework Preset:** `Vite`.
    - **Output Directory:** Ensure it is set to `dist` (NOT `build`).
3.  **Environment Variables:**
    - Add `VITE_API_BASE_URL`: Paste your Railway API URL here and append `/api/v1` (e.g., `https://your-app.up.railway.app/api/v1`)
4.  Click **Deploy**.

> [!NOTE]
> I have added a `client/vercel.json` file which automatically handles React Router "404 on refresh" errors for you.

---

## ✅ Deployment Summary
| Component | Platform | URL Type |
| :--- | :--- | :--- |
| **API** | Railway | `https://your-app.up.railway.app` |
| **UI** | Vercel | `https://your-app.vercel.app` |

**Your app is now ready to be live on Railway! 🌎**
