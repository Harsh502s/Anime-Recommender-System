from flask import Blueprint, jsonify, request
from backend.app.extensions import pipeline

bp = Blueprint("api", __name__)

@bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "model_loaded": pipeline.df is not None}), 200

@bp.route("/genres", methods=["GET"])
def get_genres():
    """Get all unique genres."""
    if pipeline.df is None:
        return jsonify({"type": "https://api.example.com/errors/server-error", "title": "Model Error", "status": 500, "detail": "Model not loaded"}), 500
    
    # Calculate genre frequencies
    genre_counts = pipeline.df['genres'].explode().value_counts()
    
    # Get sorted list of genres (most frequent first)
    genres = genre_counts.index.tolist()
    
    # Filter out Unknown
    genres = [g for g in genres if g != "Unknown"]
    
    return jsonify({"data": genres}), 200

@bp.route("/anime", methods=["GET"])
def get_anime():
    """List anime with optional pagination, search and genre filtering."""
    if pipeline.df is None:
        return jsonify({"type": "https://api.example.com/errors/server-error", "status": 500, "detail": "Model not loaded"}), 500

    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
    except (ValueError, TypeError):
        return jsonify({"type": "https://api.example.com/errors/validation-error", "status": 400, "detail": "page and limit must be integers"}), 400

    search = request.args.get("search", "").lower()
    genre = request.args.get("genre", "")

    df = pipeline.df

    # Filtering
    if search:
        df = df[df['title'].str.lower().str.contains(search, na=False)]
    if genre:
        # Check if the genre exists in the anime_genres list
        # Since 'genres' is a list of strings, we use apply to check membership
        df = df[df['genres'].apply(lambda genres_list: genre in genres_list)]

    total = len(df)
    
    # Pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_df = df.iloc[start_idx:end_idx]

    # Convert NaNs to 'NA' explicitly to avoid invalid JSON output like "NaN" which crashes frontend
    paginated_df = paginated_df.fillna("NA")
    data = paginated_df.to_dict('records')
    
    return jsonify({
        "data": data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "has_more": end_idx < total
        }
    }), 200

@bp.route("/anime/<int:anime_id>", methods=["GET"])
def get_anime_detail(anime_id):
    """Get details for a single anime by ID."""
    if pipeline.df is None:
        return jsonify({"type": "https://api.example.com/errors/server-error", "status": 500, "detail": "Model not loaded"}), 500

    df = pipeline.df
    result = df[df['anime_id'] == anime_id]
    if result.empty:
        return jsonify({"type": "https://api.example.com/errors/not-found", "status": 404, "detail": f"Anime with id {anime_id} not found"}), 404
        
    return jsonify({"data": result.iloc[0].to_dict()}), 200

@bp.route("/recommend", methods=["POST"])
def get_recommendations():
    """Get recommendations based on seed anime title."""
    if pipeline.df is None:
        return jsonify({"type": "https://api.example.com/errors/server-error", "status": 500, "detail": "Model not loaded"}), 500

    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"type": "https://api.example.com/errors/validation-error", "status": 400, "detail": "Missing 'title' in request body"}), 400

    title = data["title"]
    k = data.get("k", 10)
    
    try:
        k = int(k)
        if not (1 <= k <= 50):
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({"type": "https://api.example.com/errors/validation-error", "status": 400, "detail": "k must be integer between 1 and 50"}), 400

    # Ensure the title exists
    matched = pipeline.df[pipeline.df['title'].str.lower() == title.lower()]
    
    # Fallback to substring matching if exact match fails
    if matched.empty:
        matched = pipeline.df[pipeline.df['title'].str.lower().str.contains(title.lower(), na=False)]

    if matched.empty:
        return jsonify({"type": "https://api.example.com/errors/not-found", "status": 404, "detail": "Seed anime not found in database"}), 404
    
    actual_title = matched.iloc[0]['title']

    try:
        recs = pipeline.recommend(title=actual_title, k=k)
        return jsonify({"data": {"seed": actual_title, "recommendations": recs}}), 200
    except Exception as e:
        return jsonify({"type": "https://api.example.com/errors/server-error", "status": 500, "detail": str(e)}), 500
