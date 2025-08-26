#!/usr/bin/env python3
"""
Startup script for Railway deployment
"""

import os
import sys
import subprocess

def setup_environment():
    """Setup the environment for deployment"""
    print("Setting up environment...")
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'production'
    
    # Try to download NLTK data
    try:
        import nltk
        print("Downloading NLTK data...")
        
        # Create NLTK data directory
        nltk_data_dir = os.path.join(os.getcwd(), 'nltk_data')
        os.makedirs(nltk_data_dir, exist_ok=True)
        
        # Download minimal required data
        nltk.download('punkt', download_dir=nltk_data_dir, quiet=True)
        nltk.download('averaged_perceptron_tagger', download_dir=nltk_data_dir, quiet=True)
        nltk.download('wordnet', download_dir=nltk_data_dir, quiet=True)
        
        print("NLTK data downloaded successfully!")
        
    except Exception as e:
        print(f"Warning: Could not download NLTK data: {e}")
        print("App will run without sentiment analysis features.")

def main():
    """Main startup function"""
    setup_environment()
    
    # Start the Flask app
    from app import app
    
    # Get port from environment
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting Flask app on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    main()
