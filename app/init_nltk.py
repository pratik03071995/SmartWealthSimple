#!/usr/bin/env python3
"""
Initialize NLTK data for deployment
"""

import nltk
import os
import sys

def download_nltk_data():
    """Download required NLTK data"""
    try:
        # Create NLTK data directory
        nltk_data_dir = os.path.join(os.getcwd(), 'nltk_data')
        os.makedirs(nltk_data_dir, exist_ok=True)
        
        # Set NLTK data path
        nltk.data.path.append(nltk_data_dir)
        
        # Download required NLTK data
        required_packages = [
            'punkt',
            'averaged_perceptron_tagger',
            'maxent_ne_chunker',
            'words',
            'stopwords',
            'wordnet',
            'omw-1.4'  # Open Multilingual Wordnet
        ]
        
        print("Downloading NLTK data...")
        for package in required_packages:
            try:
                nltk.download(package, download_dir=nltk_data_dir, quiet=True)
                print(f"✅ Downloaded {package}")
            except Exception as e:
                print(f"⚠️  Warning: Could not download {package}: {e}")
        
        print("NLTK data initialization complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing NLTK data: {e}")
        return False

if __name__ == "__main__":
    download_nltk_data()
