import sys
import os
import numpy as np

# Mocking DB and models for a dry run
sys.path.append(os.path.abspath('.'))

try:
    from app.ai.rl_engine import rl_engine
    
    # Test state
    dummy_state = np.zeros(6, dtype=np.float32)
    dummy_state[0] = 0.5 # medium anxiety
    
    prediction = rl_engine.predict_difficulty(dummy_state)
    print(f"SUCCESS: Predicted {prediction['difficulty']} with {prediction['confidence']:.2f} confidence")
    print(f"Probabilities: {prediction['action_probs']}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
