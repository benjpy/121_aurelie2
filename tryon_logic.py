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
        # Try finding key in Streamlit secrets first, then environment
        self.api_key = None
        try:
            import streamlit as st
            if "RAPIDAPI_KEY" in st.secrets:
                self.api_key = st.secrets["RAPIDAPI_KEY"]
        except (ImportError, FileNotFoundError):
            pass
        
        if not self.api_key:
            self.api_key = os.environ.get("RAPIDAPI_KEY")

        self.api_host = "try-on-diffusion.p.rapidapi.com"
        self.api_url = f"https://{self.api_host}/try-on-file"
        
        # Asset configuration: Category -> { Setting Name: Image Path }
        # Using pre-set scenes where the character is already in the background
        self.assets = {
            "femme": {
                "Living Room": "woman_living_room.png",
                "Bedroom": "woman_bedroom.png"
            },
            "homme": {
                "Living Room": "man_living_room.png",
                "Bedroom": "man_bedroom.png"
            },
            "enceinte": {
                "Living Room": "pregnant_living_room.png",
                "Bedroom": "pregnant_bedroom.png"
            },
            "enfant": {
                "Living Room": "child_living_room.png",
                "Bedroom": "child_bedroom.png"
            },
            "bebe": {
                "Carpet": "baby_carpet.png",
                "Bed Cover": "baby_bedcover.png"
            }
        }
        
    def get_background_options(self, category):
        """Return available setting names for a category."""
        if category in self.assets:
            return list(self.assets[category].keys())
        return []

    def generate_tryon(self, garment_path, category, background_name=None):
        """
        Main entry point for generating the try-on image.
        category: 'femme', 'homme', 'enfant', 'bebe', 'enceinte'
        """
        print(f"--- Processing {category.upper()} with {garment_path} ---")
        
        # Determine scene image
        options = self.assets.get(category, {})
            
        if background_name and background_name in options:
            scene_path = options[background_name]
        elif options:
            scene_path = random.choice(list(options.values()))
        else:
            return None, f"No assets found for category: {category}"

        # Unified processing for all categories
        return self._process_rapidapi(garment_path, category, scene_path)

    def _process_rapidapi(self, garment_path, category, scene_path):
        """Handle All Categories using RapidAPI with pre-set scenes."""
        if not self.api_key:
            return None, "Error: RAPIDAPI_KEY not found."

        # The 'scene_path' contains the character in the setting.
        # We pass this as the 'avatar_image'.
        avatar_image = scene_path
            
        print(f"Config: Avatar/Scene={avatar_image}")
        
        try:
            files = {
                'clothing_image': (garment_path, open(garment_path, 'rb'), 'image/jpeg'),
                'avatar_image': (avatar_image, open(avatar_image, 'rb'), 'image/png'),
                # 'background_image':  We no longer send a separate background
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
