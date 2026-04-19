import os
import sys

# We ensure the pipeline is loaded dynamically
pipeline = None

def init_pipeline():
    global pipeline
    if pipeline is None:
        # Import data_clean which contains the Pipeline code
        from data_clean import AnimeRecommendationPipeline
        pipeline = AnimeRecommendationPipeline()
        
        # Load the artifacts from the root directory
        # The data_clean expects it next to data_clean.py
        pipeline.load()
