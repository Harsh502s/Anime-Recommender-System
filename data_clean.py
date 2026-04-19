import pandas as pd
import numpy as np
import re
import ast
import pickle
import os
import logging
from typing import List, Dict, Any, Optional

from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
import faiss

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AnimeRecommendationPipeline:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.mlb_genres = MultiLabelBinarizer()
        self.mlb_studios = MultiLabelBinarizer()
        self.mlb_producers = MultiLabelBinarizer()
        self.index = None
        self.df = None

    def _clean_list_col(self, val: Any) -> List[str]:
        """Safely convert string-represented lists to actual lists."""
        if pd.isna(val) or val == "NA":
            return ["Unknown"]
        try:
            parsed = ast.literal_eval(val)
            if isinstance(parsed, list):
                return [str(i) for i in parsed] if parsed else ["Unknown"]
            return [str(parsed)]
        except (ValueError, SyntaxError):
            return [str(val)] if val != "NA" else ["Unknown"]

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean the dataset for recommendation."""
        logger.info("Cleaning data...")

        # 1. Fix list columns
        df['anime_genres'] = df['anime_genres'].apply(self._clean_list_col)
        df['anime_producer'] = df['anime_producer'].apply(self._clean_list_col)

        # 2. Fix Studio (Single value or list)
        df['anime_studio'] = df['anime_studio'].apply(
            lambda x: ["Unknown_Studio"] if pd.isna(x) or x == "NA" else [x] if isinstance(x, str) else x
        )
        # Ensure studio is always a list
        df['anime_studio'] = df['anime_studio'].apply(
            lambda x: [x] if isinstance(x, str) else x
        )

        # 3. Text Cleaning for Overview
        df['anime_overview'] = df['anime_overview'].fillna("No overview available.")
        df['anime_overview'] = df['anime_overview'].apply(
            lambda x: re.sub(r"\[Written by MAL Rewrite\].*$", "", str(x), flags=re.DOTALL).strip()
        )

        # 4. Remove Duplicates based on title (CRITICAL for clean UI)
        df = df.drop_duplicates(subset=['anime_title'], keep='first')
        
        # 5. Column Renaming
        df = df.rename(columns={
            "url": "urls",
            "anime_overview": "overview",
            "anime_genres": "genres",
            "anime_producer": "producer",
            "anime_mal_score": "score",
            "anime_poster": "poster",
            "anime_title": "title",
        })

        # 5. Reset index to create a stable anime_id
        df = df.reset_index(drop=True).reset_index()
        df = df.rename(columns={"index": "anime_id"})

        self.df = df
        return df

    def vectorize(self):
        """Build the hybrid vector representation."""
        if self.df is None:
            raise ValueError("Run clean_data() first.")

        logger.info("Vectorizing data (Semantic + Categorical)...")

        # A. Semantic Overview Embeddings
        overview_embeddings = self.model.encode(self.df['overview'].tolist(), show_progress_bar=True)

        # B. Categorical Binarization
        genre_bin = self.mlb_genres.fit_transform(self.df['genres'])
        studio_bin = self.mlb_studios.fit_transform(self.df['anime_studio'])
        producer_bin = self.mlb_producers.fit_transform(self.df['producer'])

        # C. Hybrid Concatenation
        # Weighting: Overview is dense (384), categorical are sparse.
        # We concatenate them and normalize.
        hybrid_vectors = np.hstack([
            overview_embeddings,
            genre_bin,
            studio_bin,
            producer_bin
        ]).astype('float32')

        # Normalize for Cosine Similarity (Inner Product on normalized = Cosine)
        faiss.normalize_L2(hybrid_vectors)

        # D. Build FAISS Index
        dim = hybrid_vectors.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(hybrid_vectors)

        logger.info(f"Hybrid vectors built. Dimension: {dim}")

    def recommend(self, title: str, k: int = 10) -> List[Dict[str, Any]]:
        """Find top k similar anime."""
        if self.index is None or self.df is None:
            raise ValueError("Pipeline not vectorized.")

        # Find the anime_id for the given title
        try:
            idx = self.df[self.df['title'] == title].index[0]
        except IndexError:
            logger.error(f"Anime '{title}' not found in dataset.")
            return []

        # Get the vector for this anime
        # Ensure the index is an integer for reconstruct
        query_vector = self.index.reconstruct(int(idx)).reshape(1, -1)

        # Search
        D, I = self.index.search(query_vector, k + 10) # Get more to allow filtering

        target_title_lower = title.lower()

        # Exclude the item itself
        recommendations = []
        for i in I[0]:
            row = self.df.iloc[i]
            # Skip if same index or same title (handles potential duplicates and seed anime)
            if i == idx or row['title'].lower() == target_title_lower:
                continue
                
            recommendations.append({
                "title": row['title'],
                "score": float(row['score']) if pd.notna(row['score']) else None,
                "poster": row['poster'],
                "anime_id": int(row['anime_id']),
                "genres": row['genres'],
                "urls": row['urls'],
                "overview": row['overview'],
                "anime_studio": row['anime_studio']
            })
            if len(recommendations) == k:
                break

        return recommendations

    def save(self, folder: str = "model_artifacts"):
        """Save all artifacts."""
        # Use absolute path to ensure consistency across different execution environments
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_folder_path = os.path.join(base_dir, folder)

        if not os.path.exists(full_folder_path):
            os.makedirs(full_folder_path)

        logger.info(f"Saving artifacts to {full_folder_path}...")

        # Save FAISS Index
        faiss.write_index(self.index, os.path.join(full_folder_path, "similarity.index"))

        # Save MLBs and DF
        artifacts = {
            "mlb_genres": self.mlb_genres,
            "mlb_studios": self.mlb_studios,
            "mlb_producers": self.mlb_producers,
            "df": self.df
        }
        with open(os.path.join(full_folder_path, "artifacts.pkl"), "wb") as f:
            pickle.dump(artifacts, f)

        self.df.to_csv(os.path.join(full_folder_path, "rec_data.csv"), index=False)
        logger.info("All artifacts saved successfully.")

    def load(self, folder: str = "model_artifacts"):
        """Load artifacts."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_folder_path = os.path.join(base_dir, folder)

        logger.info(f"Loading artifacts from {full_folder_path}...")

        with open(os.path.join(full_folder_path, "artifacts.pkl"), "rb") as f:
            artifacts = pickle.load(f)

        self.mlb_genres = artifacts["mlb_genres"]
        self.mlb_studios = artifacts["mlb_studios"]
        self.mlb_producers = artifacts["mlb_producers"]
        self.df = artifacts["df"]

        self.index = faiss.read_index(os.path.join(full_folder_path, "similarity.index"))
        logger.info("Pipeline loaded successfully.")

if __name__ == "__main__":
    # Main Execution Flow
    try:
        # Load data
        df_raw = pd.read_csv("anime_data.csv")

        pipeline = AnimeRecommendationPipeline()

        # 1. Clean
        df_cleaned = pipeline.clean_data(df_raw)

        # 2. Vectorize
        pipeline.vectorize()

        # 3. Test
        test_title = "One Piece" # Example from dataset
        recs = pipeline.recommend(test_title)
        print(f"Recommendations for {test_title}:")
        for r in recs:
            print(f"- {r['title']} (Score: {r['score']})")

        # 4. Save
        pipeline.save()

    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
