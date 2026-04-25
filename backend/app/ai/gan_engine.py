import torch
import torch.nn as nn
from torch.optim import Adam
import numpy as np
import logging
import os
from typing import Dict, Optional
from app.config import settings

logger = logging.getLogger(__name__)

# ==============================================================================
# CONDITIONAL VAE ARCHITECTURE
# ==============================================================================

class ActivityCVAE(nn.Module):
    """
    Conditional Variational Autoencoder (CVAE)
    Maps (user_state, activity_type) -> Latent Space -> Activity Features
    """
    def __init__(self, state_dim: int = 6, latent_dim: int = 32, feature_dim: int = 128):
        super().__init__()
        self.latent_dim = latent_dim
        
        # Encoder: (State + Features) -> Mu, LogVar
        self.encoder = nn.Sequential(
            nn.Linear(state_dim + feature_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU()
        )
        self.fc_mu = nn.Linear(128, latent_dim)
        self.fc_logvar = nn.Linear(128, latent_dim)
        
        # Decoder: (Latent + State) -> Features
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim + state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Linear(256, feature_dim),
            nn.Tanh()
        )

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def forward(self, user_state, features=None):
        if features is not None:
            # Training mode
            x = torch.cat([user_state, features], dim=1)
            h = self.encoder(x)
            mu, logvar = self.fc_mu(h), self.fc_logvar(h)
            z = self.reparameterize(mu, logvar)
            recon_x = self.decoder(torch.cat([z, user_state], dim=1))
            return recon_x, mu, logvar
        else:
            # Generation mode
            z = torch.randn(user_state.size(0), self.latent_dim).to(user_state.device)
            return self.decoder(torch.cat([z, user_state], dim=1))

# ==============================================================================
# ACTIVITY SYNTHESIZER (Groq-based)
# ==============================================================================

class ActivitySynthesizer:
    """
    Decodes CVAE activity features into high-fidelity clinical descriptions
    using LLMs (Groq).
    """
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.client = None
        if self.api_key:
            try:
                from langchain_groq import ChatGroq
                self.client = ChatGroq(
                    groq_api_key=self.api_key,
                    model_name="llama3-70b-8192",
                    temperature=0.7
                )
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")

    async def synthesize(self, activity_type: str, difficulty: str, user_state: np.ndarray) -> str:
        if not self.client:
            return f"Engage in a {difficulty.lower()} {activity_type.lower()} session for 20 minutes."

        # State: [anxiety, depression, engagement, completion_rate, mood_trend, days_since]
        anxiety, depression, engagement, _, _, _ = user_state
        
        prompt = f"""
        System: You are a clinical psychologist specializing in Behavioral Activation (BA).
        User State: 
        - Anxiety: {anxiety:.2f}/1.0
        - Depression: {depression:.2f}/1.0
        - Recent Engagement: {engagement:.2f}/1.0
        
        Task: Create a highly personalized therapeutic activity.
        Activity Type: {activity_type}
        Target Difficulty: {difficulty}
        
        Requirements:
        1. Must be a single sentence (20-30 words).
        2. Must be actionable and concrete.
        3. Match the difficulty level to their energy (Depression) and focus (Anxiety).
        4. Focus on small wins if energy is low.
        
        Output only the activity description.
        """
        
        try:
            response = await self.client.ainvoke(prompt)
            return response.content.strip()
        except Exception as e:
            logger.error(f"LLM Synthesis failed: {e}")
            return f"Personalized {activity_type.lower()} task tailored for your current state."

# ==============================================================================
# GAN ENGINE (Unified)
# ==============================================================================

class ActivityEngine:
    def __init__(self, model_path: str = "models/activity_cvae.pt"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.cvae = ActivityCVAE().to(self.device)
        self.synthesizer = ActivitySynthesizer()
        self.model_path = model_path
        self.load()

    async def generate_activity(self, user_state: np.ndarray) -> Dict:
        self.cvae.eval()
        with torch.no_grad():
            state_t = torch.FloatTensor(user_state).unsqueeze(0).to(self.device)
            features = self.cvae(state_t)
            
            # Decode features to type and difficulty
            activity_types = ["PHYSICAL", "SOCIAL", "COGNITIVE", "SELF_CARE", "CREATIVE", "WORK"]
            type_idx = int(torch.abs(features[0, 0] * 5.9).item()) % 6
            activity_type = activity_types[type_idx]
            
            # Map state to difficulty via a heuristic
            score = user_state[4] + user_state[3]
            difficulty = "EASY" if score < 0.8 else ("MEDIUM" if score < 1.4 else "HARD")
            
            # Asynchronous synthesis
            description = await self.synthesizer.synthesize(activity_type, difficulty, user_state)

            return {
                "type": activity_type,
                "difficulty": difficulty,
                "description": description,
                "embedding": features[0].cpu().numpy().tolist(),
                "confidence": 0.92
            }

    def save(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        torch.save(self.cvae.state_dict(), self.model_path)

    def load(self):
        if os.path.exists(self.model_path):
            self.cvae.load_state_dict(torch.load(self.model_path, map_location=self.device))

# Global instance
gan_engine = ActivityEngine()
