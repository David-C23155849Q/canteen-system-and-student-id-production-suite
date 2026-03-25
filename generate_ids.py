import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

# Settings
CARD_SIZE = (600, 950)  # Standard Vertical ID Size
BLUE_COLOR = (44, 62, 80)
WHITE_COLOR = (255, 255, 255)

def generate_student_card(student_name, student_id, qr_data):
    # --- CREATE FRONT ---
    front = Image.new('RGB', CARD_SIZE, color=WHITE_COLOR)
    draw = ImageDraw.Draw(front)
    
    # Add Header Background
    draw.rectangle([0, 0, 600, 150], fill=BLUE_COLOR)
    
    # Add Text (You may need to point to a valid .ttf file on your system)
    try:
        font_bold = ImageFont.truetype("arialbd.ttf", 40)
        font_reg = ImageFont.truetype("arial.ttf", 30)
    except:
        font_bold = ImageFont.load_default()
        font_reg = ImageFont.load_default()

    draw.text((300, 75), "MORGENSTER COLLEGE", fill=WHITE_COLOR, font=font_bold, anchor="mm")
    
    # Placeholder for Student Photo
    draw.rectangle([175, 200, 425, 450], outline=BLUE_COLOR, width=3)
    draw.text((300, 325), "STUDENT PHOTO", fill=(200, 200, 200), anchor="mm")

    # Student Info
    draw.text((300, 550), student_name.upper(), fill=BLUE_COLOR, font=font_bold, anchor="mm")
    draw.text((300, 600), f"ID: {student_id}", fill=(100, 100, 100), font=font_reg, anchor="mm")
    draw.text((300, 900), "STUDENT CARD 2026", fill=BLUE_COLOR, font=font_reg, anchor="mm")

    # --- CREATE BACK ---
    back = Image.new('RGB', CARD_SIZE, color=WHITE_COLOR)
    draw_back = ImageDraw.Draw(back)
    
    # Generate QR Code
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").resize((400, 400))
    
    # Paste QR onto back
    back.paste(qr_img, (100, 275))
    draw_back.text((300, 750), "SCAN FOR MEALS", fill=BLUE_COLOR, font=font_bold, anchor="mm")

    # Save both sides
    front.save(f"output_ids/{student_id}_front.png")
    back.save(f"output_ids/{student_id}_back.png")
    print(f"Generated card for {student_name}")

# Example Usage
if __name__ == "__main__":
    if not os.path.exists('output_ids'): os.makedirs('output_ids')
    generate_student_card("John Doe", "MC2026-001", "STUDENT_XYZ_123")