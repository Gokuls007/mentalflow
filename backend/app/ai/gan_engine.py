import torch
import torch.nn as nn
from torch.optim import Adam
import numpy as np
import logging
import os

logger = logging.getLogger(__name__)

# ==============================================================================
# GAN ARCHITECTURE
# ==============================================================================

class ActivityGenerator(nn.Module):
    """
    Generator Network
    """
    def __init__(self, latent_dim: int = 100, state_dim: int = 6, output_dim: int = 256):
        super().__init__()
        self.latent_dim = latent_dim
        self.state_dim = state_dim
        
        self.fc = nn.Sequential(
            nn.Linear(latent_dim + state_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            nn.Linear(256, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            nn.Linear(512, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            
            nn.Linear(512, output_dim),
            nn.Tanh()
        )
    
    def forward(self, z: torch.Tensor, user_state: torch.Tensor) -> torch.Tensor:
        combined = torch.cat([z, user_state], dim=1)
        return self.fc(combined)


class ActivityDiscriminator(nn.Module):
    """
    Discriminator Network
    """
    def __init__(self, input_dim: int = 256):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            
            nn.Linear(256, 128),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            
            nn.Linear(128, 64),
            nn.LeakyReLU(0.2),
            
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
    
    def forward(self, activity_embedding: torch.Tensor) -> torch.Tensor:
        return self.fc(activity_embedding)


class ActivityDecoder(nn.Module):
    """
    Decoder Network
    """
    def __init__(self, embedding_dim: int = 256):
        super().__init__()
        self.activity_type_decoder = nn.Sequential(
            nn.Linear(embedding_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 6)
        )
        self.difficulty_decoder = nn.Sequential(
            nn.Linear(embedding_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 3)
        )
        self.description_decoder = nn.Sequential(
            nn.Linear(embedding_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64)
        )
    
    def forward(self, embedding: torch.Tensor) -> dict:
        activity_type_logits = self.activity_type_decoder(embedding)
        difficulty_logits = self.difficulty_decoder(embedding)
        description_features = self.description_decoder(embedding)
        
        activity_type = torch.argmax(activity_type_logits, dim=1)
        difficulty = torch.argmax(difficulty_logits, dim=1)
        
        return {
            "activity_type": activity_type,
            "difficulty": difficulty,
            "description_features": description_features
        }

# ==============================================================================
# GAN ENGINE
# ==============================================================================

class ActivityGAN:
    def __init__(self, latent_dim: int = 100, embedding_dim: int = 256, device: str = "cpu"):
        self.latent_dim = latent_dim
        self.embedding_dim = embedding_dim
        self.device = torch.device(device if torch.cuda.is_available() and device == "cuda" else "cpu")
        
        self.generator = ActivityGenerator(latent_dim, 6, embedding_dim).to(self.device)
        self.discriminator = ActivityDiscriminator(embedding_dim).to(self.device)
        self.decoder = ActivityDecoder(embedding_dim).to(self.device)
        
        self.gen_optimizer = Adam(self.generator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        self.disc_optimizer = Adam(self.discriminator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        self.criterion = nn.BCELoss()
    
    def generate_activity(self, user_state: np.ndarray) -> dict:
        self.generator.eval()
        self.decoder.eval()
        
        with torch.no_grad():
            user_state_tensor = torch.FloatTensor(user_state).unsqueeze(0).to(self.device)
            z = torch.randn((1, self.latent_dim)).to(self.device)
            embedding = self.generator(z, user_state_tensor)
            decoded = self.decoder(embedding)
            
            type_idx = decoded["activity_type"][0].item()
            diff_idx = decoded["difficulty"][0].item()
            
            activity_types = ["PHYSICAL", "SOCIAL", "COGNITIVE", "SELF_CARE", "CREATIVE", "WORK"]
            difficulties = ["EASY", "MEDIUM", "HARD"]
            
            activity_type = activity_types[type_idx]
            difficulty = difficulties[diff_idx]
            
            description = self._generate_description(
                activity_type, 
                difficulty, 
                user_state, 
                decoded["description_features"][0].cpu().numpy()
            )
            
            return {
                "type": activity_type,
                "difficulty": difficulty,
                "description": description,
                "embedding": embedding[0].cpu().numpy().tolist(),
                "confidence": 0.85
            }
    
    def _generate_description(self, activity_type: str, difficulty: str, user_state: np.ndarray, features: np.ndarray) -> str:
        # State: [anxiety, depression, engagement, completion_rate, mood_trend, days_since]
        anxiety, depression, engagement, completion_rate, mood_trend, days_since = user_state
        
        templates = {
            "PHYSICAL": {
                "EASY": ["Short {duration} min walk in fresh air", "Gentle stretching ({duration} min)"],
                "MEDIUM": ["{duration} min jog in the {location}", "Strength training ({duration} min)"],
                "HARD": ["Intense {duration} min workout session", "Challenge: {duration} min run/cycle"]
            },
            "SOCIAL": {
                "EASY": ["Text {person} about {topic}", "Video call with {person} ({duration} min)"],
                "MEDIUM": ["Coffee with {person} ({duration} min)", "Meet for a {activity} ({duration} min)"],
                "HARD": ["Attend a social event", "Host a gathering for {count} people"]
            },
            "COGNITIVE": {
                "EASY": ["Read {topic} article ({duration} min)", "Brain game session ({duration} min)"],
                "MEDIUM": ["Learn {skill} basics ({duration} min)", "Journaling session ({duration} min)"],
                "HARD": ["Deep study on {topic} ({duration} min)", "Complex problem solving ({duration} min)"]
            },
            "SELF_CARE": {
                "EASY": ["Short {duration} min meditation", "Quick skincare routine"],
                "MEDIUM": ["Full relaxation routine ({duration} min)", "Mindfulness session ({duration} min)"],
                "HARD": ["Plan wellness goals ({duration} min)", "Deep meditation session ({duration} min)"]
            },
            "CREATIVE": {
                "EASY": ["Quick sketch ({duration} min)", "Listen to a {topic} podcast"],
                "MEDIUM": ["Work on art project ({duration} min)", "Try a new recipe"],
                "HARD": ["Deep creative flow: {topic} ({duration} min)", "Complete a creative project"]
            },
            "WORK": {
                "EASY": ["Organize workspace", "Plan tomorrow's tasks"],
                "MEDIUM": ["Complete task: {topic} ({duration} min)", "Collaboration session"],
                "HARD": ["Deep work on project ({duration} min)", "Strategic planning session"]
            }
        }
        
        type_templates = templates.get(activity_type, {}).get(difficulty, ["Personalized Activity"])
        template = type_templates[int(features[0] * 100) % len(type_templates)]
        
        duration = 15 if difficulty == "EASY" else (30 if difficulty == "MEDIUM" else 45)
        duration += int(engagement * 10)
        
        return template.format(
            duration=duration,
            location="park" if mood_trend > 0.5 else "gym",
            person="a friend" if anxiety < 0.5 else "family member",
            topic="psychology" if depression > 0.5 else "technology",
            skill="Python" if engagement > 0.5 else "digital art",
            activity="walk" if mood_trend > 0.5 else "movie",
            count=3 + int(engagement * 5)
        )

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save({
            "generator": self.generator.state_dict(),
            "discriminator": self.discriminator.state_dict(),
            "decoder": self.decoder.state_dict()
        }, path)

    def load(self, path: str):
        if os.path.exists(path):
            checkpoint = torch.load(path, map_location=self.device)
            self.generator.load_state_dict(checkpoint["generator"])
            self.discriminator.load_state_dict(checkpoint["discriminator"])
            self.decoder.load_state_dict(checkpoint["decoder"])

gan_engine = ActivityGAN()
