from typing import Dict, List
import numpy as np

class ActivityDecoder:
    """Convert GAN embedding to human-readable activity"""
    
    def __init__(self):
        # Activity templates organized by type and difficulty
        self.activities = {
            'physical_easy': [
                'Take a {duration}-minute walk',
                'Do {duration} minutes of stretching',
                'Dance to your favorite song for {duration} minutes',
            ],
            'physical_medium': [
                'Go for a {duration}-minute jog',
                'Do {duration} minutes of workout routine',
                'Ride a bike for {duration} minutes',
            ],
            'physical_hard': [
                'Go for an intense {duration}-minute run',
                'Do {duration} minutes of HIIT workout',
            ],
            'social_easy': [
                'Send a message to someone you care about',
                'Call a friend for {duration} minutes',
            ],
            'social_medium': [
                'Invite a friend for coffee for {duration} minutes',
                'Join a group activity or class',
            ],
            'cognitive_easy': [
                'Read a chapter of a book for {duration} minutes',
                'Journal your thoughts for {duration} minutes',
            ]
        }
        
        self.value_keywords = {
            'social': ['with friends', 'with family', 'with someone'],
            'nature': ['in nature', 'in the park', 'outside'],
            'creative': ['creative', 'artistic'],
        }

    def decode(self, gan_embedding: np.ndarray, user_state: Dict, difficulty: str, user_values: List[str] = None) -> Dict:
        """Map GAN embedding to clinical text"""
        # Simplify type selection from embedding for Phase 8
        types = ['physical', 'social', 'cognitive']
        activity_type = types[np.argmax(gan_embedding[:3])] if len(gan_embedding) > 3 else 'physical'
        
        duration = 15 if user_state.get('engagement', 5) < 5 else 30
        
        key = f"{activity_type}_{difficulty}"
        if key not in self.activities:
            key = 'physical_easy'
            
        base_template = np.random.choice(self.activities[key])
        title = base_template.format(duration=duration)
        
        # Personalize if values exist
        if user_values:
            for val in user_values:
                keywords = self.value_keywords.get(val.lower(), [])
                if keywords:
                    title += f" {np.random.choice(keywords)}"
                    break

        return {
            'title': title,
            'description': f"This {activity_type} activity was generated specifically for your current resilience level.",
            'duration_min': duration,
            'difficulty': difficulty,
            'type': activity_type,
            'why_this_activity': f"Based on your {activity_type} preference and target {difficulty} challenge.",
            'gan_embedding': gan_embedding.tolist()
        }

# Global instance
activity_decoder = ActivityDecoder()
