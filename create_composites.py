from PIL import Image
import os

def create_composite(avatar_path, bg_path, output_path, scale=0.85):
    try:
        if not os.path.exists(avatar_path) or not os.path.exists(bg_path):
            print(f"Missing source for {output_path}")
            return

        avatar = Image.open(avatar_path).convert("RGBA")
        bg = Image.open(bg_path).convert("RGBA")
        
        bg_w, bg_h = bg.size
        # Resize avatar to fit
        target_h = int(bg_h * scale)
        aspect = avatar.width / avatar.height
        target_w = int(target_h * aspect)
        
        avatar_resized = avatar.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        # Center horizontally, bottom aligned
        x = (bg_w - target_w) // 2
        y = bg_h - target_h - 50 # 50px padding from bottom
        
        bg.paste(avatar_resized, (x, y), avatar_resized)
        bg.save(output_path)
        print(f"Created {output_path}")
    except Exception as e:
        print(f"Error creating {output_path}: {e}")

# Sources
woman = "woman.png"
pregnant = "pregnant.png"
# Using woman as proxy for child as per previous logic, but maybe scaled down
child_proxy = "woman.png" 

bedroom = "bedroom.png"
livingroom = "livingroom.png"

# Targets to create
# woman_living_room.png already exists (real one)
create_composite(woman, bedroom, "woman_bedroom.png", scale=0.85)

create_composite(pregnant, livingroom, "pregnant_living_room.png", scale=0.85)
create_composite(pregnant, bedroom, "pregnant_bedroom.png", scale=0.85)

create_composite(child_proxy, livingroom, "child_living_room.png", scale=0.65)
create_composite(child_proxy, bedroom, "child_bedroom.png", scale=0.65)
