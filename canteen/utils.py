# canteen/utils.py
from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings

def generate_single_id(student):
    """
    The exact logic from your BaseCommand, but modified 
    to take a single 'student' object.
    """
    # Use the same paths we set up before
    template_path = os.path.join(settings.BASE_DIR, 'templates', 'id_templates', 'purple_front.png')
    output_dir = os.path.join(settings.BASE_DIR, 'student_ids_purple_final')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Open Template
    img = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    
    # 2. Load Fonts (Ensure these paths are correct for your PC)
    font_bold = ImageFont.truetype("arialbd.ttf", 45)
    font_id = ImageFont.truetype("arial.ttf", 35)

    # 3. Paste Student Photo
    if student.photo:
        photo = Image.open(student.photo.path).convert("RGBA")
        photo = photo.resize((320, 320))
        # Use the same coordinates from your working script
        img.paste(photo, (50, 200), photo)

    # 4. Draw Text
    draw.text((420, 250), student.full_name.upper(), fill="black", font=font_bold)
    draw.text((420, 320), f"REG: {student.student_id}", fill="#5b21b6", font=font_id)

    # 5. Save the PNG
    save_path = os.path.join(output_dir, f"{student.student_id}_FRONT.png")
    img.save(save_path)
    return save_path