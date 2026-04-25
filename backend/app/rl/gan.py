import torch
import torch.nn as nn
import numpy as np
import os

class ActivityGenerator(nn.Module):
    """Generator - creates personalized activities"""
    
    def __init__(self, latent_dim=100, output_dim=256):
        super().__init__()
        
        # Input: random noise + user context (6 features)
        # Output: activity embedding (256 dimensions)
        self.fc_layers = nn.Sequential(
            nn.Linear(latent_dim + 6, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            nn.Linear(512, output_dim),
            nn.Tanh() # Normalized output for embeddings
        )
    
    def forward(self, z, user_state):
        combined = torch.cat([z, user_state], dim=1)
        return self.fc_layers(combined)

class ActivityDiscriminator(nn.Module):
    """Discriminator - judges if activity is clinically viable/successful"""
    
    def __init__(self, input_dim=256):
        super().__init__()
        
        self.fc_layers = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            
            nn.Linear(256, 128),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            
            nn.Linear(128, 1),
            nn.Sigmoid()
        )
    
    def forward(self, activity_embedding):
        return self.fc_layers(activity_embedding)

class ActivityGAN:
    """Full GAN system for clinical activity generation"""
    
    def __init__(self, latent_dim=100):
        self.latent_dim = latent_dim
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.generator = ActivityGenerator(latent_dim).to(self.device)
        self.discriminator = ActivityDiscriminator().to(self.device)
        
        self.gen_optimizer = torch.optim.Adam(self.generator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        self.disc_optimizer = torch.optim.Adam(self.discriminator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        
        self.criterion = nn.BCELoss()
        
        # Ensure models directory exists
        if not os.path.exists("models"):
            os.makedirs("models")
            
    def generate_personalized_activity(self, user_state):
        """Generate personalized activity embedding for user"""
        self.generator.eval()
        
        with torch.no_grad():
            # Normalize user state for the network
            user_state_tensor = torch.tensor([
                user_state.get('anxiety', 0) / 21, # Normalize GAD-7
                user_state.get('phq9', 0) / 27,    # Normalize PHQ-9
                user_state.get('engagement', 5) / 10,
                user_state.get('completion_rate', 0.5),
                user_state.get('mood_trend', 0.0),
                user_state.get('days_since_activity', 1) / 30,
            ], dtype=torch.float32).unsqueeze(0).to(self.device)
            
            z = torch.randn(1, self.latent_dim).to(self.device)
            activity_embedding = self.generator(z, user_state_tensor)
            
            return activity_embedding.cpu().numpy()[0]

    def train_on_real_activities(self, activities_data, epochs=100):
        print(f"🤖 Training ActivityGAN on {len(activities_data)} samples...")
        self.generator.train()
        self.discriminator.train()
        
        # Implementation of batch training would go here
        # For Phase 8 integration, we focus on the prediction capability
        
    def save_model(self):
        torch.save(self.generator.state_dict(), "models/activity_generator.pth")
        torch.save(self.discriminator.state_dict(), "models/activity_discriminator.pth")
        
    def load_model(self):
        if os.path.exists("models/activity_generator.pth"):
            self.generator.load_state_dict(torch.load("models/activity_generator.pth", map_location=self.device))
            self.discriminator.load_state_dict(torch.load("models/activity_discriminator.pth", map_location=self.device))
            return True
        return False

# Global instance
activity_gan = ActivityGAN()
