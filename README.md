# 🌌 Ethereal Anime Recommender

A high-performance, full-stack anime discovery platform featuring a **hybrid vector search engine** (Semantic + Categorical) and a modern **React 19** frontend with glassmorphic design.

![Anime Recommender Hero](https://placehold.co/1200x400/191f2f/78d6cf?text=Anime+Recommender+System+v2)

## ✨ Core Features
- **🧠 Hybrid Vector Engine:** Combines deep semantic understanding (Sentence Transformers) with categorical precision (Genres/Studios) for results that "feel" right.
- **⚡ Real-time Autocomplete:** Ultra-fast search suggestions with live metadata as you type.
- **🎭 Genre Intelligence:** Dynamic sidebar featuring top-frequency genre filters and immersive content exploration.
- **📺 Netflix-Style UI:** Premium hover experiences with pop-out detail windows and high-resolution poster optimization.
- **🚀 Scalable Architecture:** Decoupled Flask REST API and Vite-powered React 19 frontend.

---

## 🛠️ Technology Stack

### **Frontend**
- **Framework:** React 19 + Vite
- **Styling:** Tailwind CSS v4
- **Icons:** Lucide React
- **HTTP Client:** Axios

### **Backend**
- **Framework:** Flask (Python 3.11+)
- **Vector Search:** FAISS (Facebook AI Similarity Search)
- **Model:** `all-MiniLM-L6-v2` (Sentence-Transformers)
- **Data Engine:** Pandas / NumPy

---

## 🚀 Getting Started

### 1. Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Clean data and generate vector indices
# This will create the 'model_artifacts' directory
python data_clean.py

# Launch the API server
python -m backend.run
```

### 2. Frontend Setup
```bash
cd client

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## 📂 Project Structure
```text
├── backend/            # Flask API implementation
├── client/             # React 19 Frontend
├── model_artifacts/    # (Generated) Vector index & processed data
├── data_clean.py       # ML Pipeline: Deduplication & Vectorization
├── scrape_anime.py     # Production-grade scraper
└── anime_data.csv      # Raw dataset
```

---

## 📊 Recommendation Methodology
The system uses a **Hybrid Indexing** strategy:
1. **Semantic Layer:** Encodes anime synopses into a 384-dimensional vector space using `SentenceTransformer`.
2. **Categorical Layer:** One-hot encodes Genres, Studios, and Producers.
3. **Similarity:** Normalizes and concatenates these layers, then uses **FAISS Inner Product (Cosine Similarity)** matching to find the closest matches in sub-millisecond time.

## 📜 License
Licensed under the [MIT License](LICENSE).
