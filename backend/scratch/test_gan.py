import sys
import os
import numpy as np
import torch

sys.path.append(os.path.abspath('.'))

try:
    from app.ai.gan_engine import gan_engine
    
    # Test state
    dummy_state = np.array([0.5, 0.4, 0.7, 0.8, 0.6, 0.1], dtype=np.float32)
    
    # Generate activity
    activity = gan_engine.generate_activity(dummy_state)
    
    print("SUCCESS: GAN Generated Activity")
    print(f"Type: {activity['type']}")
    print(f"Difficulty: {activity['difficulty']}")
    print(f"Description: {activity['description']}")
    print(f"Embedding size: {len(activity['embedding'])}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
