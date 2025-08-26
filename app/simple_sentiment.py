"""
Simple sentiment analysis without NLTK dependency
"""

import re
from typing import Dict

class SimpleSentimentAnalyzer:
    """Simple sentiment analyzer using keyword matching"""
    
    def __init__(self):
        # Positive and negative keywords for financial news
        self.positive_words = {
            'bullish', 'surge', 'jump', 'rise', 'gain', 'profit', 'growth', 'positive',
            'strong', 'beat', 'exceed', 'outperform', 'rally', 'soar', 'climb', 'advance',
            'increase', 'higher', 'up', 'good', 'great', 'excellent', 'outstanding',
            'success', 'win', 'victory', 'breakthrough', 'innovation', 'record', 'high'
        }
        
        self.negative_words = {
            'bearish', 'drop', 'fall', 'decline', 'loss', 'crash', 'plunge', 'negative',
            'weak', 'miss', 'disappoint', 'underperform', 'selloff', 'dip', 'slip', 'retreat',
            'decrease', 'lower', 'down', 'bad', 'terrible', 'awful', 'poor',
            'failure', 'lose', 'defeat', 'problem', 'issue', 'concern', 'risk', 'worry'
        }
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment using simple keyword matching"""
        if not text:
            return {'polarity': 0, 'subjectivity': 0, 'sentiment': 'neutral'}
        
        # Convert to lowercase and split into words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Count positive and negative words
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        # Calculate polarity (-1 to 1)
        total_words = len(words)
        if total_words == 0:
            polarity = 0
        else:
            polarity = (positive_count - negative_count) / total_words
            # Normalize to -1 to 1 range
            polarity = max(-1, min(1, polarity * 10))
        
        # Determine sentiment
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Calculate subjectivity (simplified)
        subjectivity = min(1.0, (positive_count + negative_count) / max(1, total_words))
        
        return {
            'polarity': polarity,
            'subjectivity': subjectivity,
            'sentiment': sentiment
        }
