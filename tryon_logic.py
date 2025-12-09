import os
import sys
import random
import requests
from dotenv import load_dotenv
from PIL import Image, ImageOps

# Load environment variables
load_dotenv()

class VirtualTryOnApp:
    def __init__(self):
        self.api_key = os.environ.get("RAPIDAPI_KEY")
        self.api_host = "try-on-diffusion.p.rapidapi.com"
        self.api_url = f"https://{self.api_host}/try-on-file"
        
        # Asset configuration
        self.assets = {
            "avatar_woman": "woman.png",
            "avatar_man": "man.png",
            "avatar_pregnant": "pregnant.png",
            "bg_indoor": {
                "Bedroom": "bedroom.png", 
                "Living Room": "livingroom.png"
            },
            "bg_baby": {
                "Playmat": "carpet.png", 
                "Duvet": "duvet.png"
            }
        }
        
    def get_background_options(self, category):
        """Return available background names for a category."""
        if category == "bebe":
            return list(self.assets["bg_baby"].keys())
        return list(self.assets["bg_indoor"].keys())

    def generate_tryon(self, garment_path, category, background_name=None):
        """
        Main entry point for generating the try-on image.
        category: 'femme', 'homme', 'child', 'bebe', 'enceinte'
        """
        print(f"--- Processing {category.upper()} with {garment_path} ---")
        
        # Determine background file path
        bg_path = None
        if category == "bebe":
            options = self.assets["bg_baby"]
        else:
            options = self.assets["bg_indoor"]
            
        if background_name and background_name in options:
            bg_path = options[background_name]
        else:
            # Fallback to random if not specified or invalid
            import random
            bg_path = random.choice(list(options.values()))

        if category == "bebe":
            return self._process_flat_lay(garment_path, bg_path)
        else:
            return self._process_rapidapi(garment_path, category, bg_path)

    def _process_rapidapi(self, garment_path, category, bg_path):
        """Handle Femme, Homme, Enfant, Enceinte using RapidAPI."""
        if not self.api_key:
            return None, "Error: RAPIDAPI_KEY not found."

        # Determine avatar
        if category == "homme":
            avatar = self.assets["avatar_man"]
        elif category == "enceinte":
            avatar = self.assets["avatar_pregnant"]
        else:
            # Femme and Enfant use woman avatar (Enfant uses adult model as placeholder per logic)
            # Potentially 'Enfant' could use a scaled down version or different model if available,
            # but for now reusing 'woman.png' as per previous plan/availability.
            avatar = self.assets["avatar_woman"]
            
        print(f"Config: Avatar={avatar}, Background={bg_path}")
        
        try:
            files = {
                'clothing_image': (garment_path, open(garment_path, 'rb'), 'image/jpeg'),
                'avatar_image': (avatar, open(avatar, 'rb'), 'image/png'),
                'background_image': (bg_path, open(bg_path, 'rb'), 'image/png')
            }
            headers = {
                "X-RapidAPI-Key": self.api_key,
                "X-RapidAPI-Host": self.api_host
            }
            
            response = requests.post(self.api_url, files=files, headers=headers)
            
            if response.status_code == 200:
                output_filename = f"output_{category}_{os.path.basename(garment_path).split('.')[0]}.png"
                with open(output_filename, "wb") as f:
                    f.write(response.content)
                return output_filename, None
            else:
                return None, f"API Error ({response.status_code}): {response.text}"
                
        except Exception as e:
            return None, f"Exception: {e}"

    def _process_flat_lay(self, garment_path, bg_path):
        """Handle Bebe using local flat lay composition."""
        try:
            from rembg import remove
            
            print(f"Config: Flat Lay, Background={bg_path}")
            
            # Load images
            bg = Image.open(bg_path).convert("RGBA")
            garment = Image.open(garment_path).convert("RGBA")
            
            # Remove background
            try:
                garment_nobg = remove(garment)
            except Exception as e:
                 return None, f"Background removal failed: {e}. Ensure 'rembg' is installed."

            # Resize garment to fit on background (e.g. 60% of background width)
            bg_w, bg_h = bg.size
            target_w = int(bg_w * 0.6)
            aspect_ratio = garment_nobg.height / garment_nobg.width
            target_h = int(target_w * aspect_ratio)
            
            garment_resized = garment_nobg.resize((target_w, target_h), Image.Resampling.LANCZOS)
            
            # Center position logic (add some random rotation for realism?)
            pos_x = (bg_w - target_w) // 2
            pos_y = (bg_h - target_h) // 2
            
            # Composite
            bg.paste(garment_resized, (pos_x, pos_y), garment_resized)
            
            output_filename = f"output_bebe_{os.path.basename(garment_path).split('.')[0]}.png"
            bg.save(output_filename)
            return output_filename, None
            
        except ImportError:
            return None, "Error: 'rembg' or 'Pillow' not installed."
        except Exception as e:
            return None, f"Exception in flat lay: {e}"
