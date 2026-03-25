import os
import qrcode
from django.core.management.base import BaseCommand
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont, ImageOps

class Command(BaseCommand):
    help = 'Generates Purple Landscape IDs with Circular Photos and Auto-Intake'

    def handle(self, *args, **kwargs):
        output_dir = os.path.join(settings.MEDIA_ROOT, "student_ids_purple_final")

        if not os.path.exists(output_dir):
         os.makedirs(output_dir)

        from canteen.models import Student
        students = Student.objects.filter(is_active=True)
        
        # --- BRAND COLORS ---
        PURPLE = (102, 45, 145)  # Morgenster Purple
        GREEN = (34, 177, 76)    # Official Green
        WHITE = (255, 255, 255)
        DARK_TEXT = (20, 20, 20)
        CARD_SIZE = (950, 600) 
        STATIC_LOGO_PATH = os.path.join(settings.BASE_DIR, 'canteen', 'static', 'logo.png')

        for student in students:
            front = Image.new('RGB', CARD_SIZE, color=WHITE)
            draw = ImageDraw.Draw(front)
            
            # 1. Purple Header/Footer Layout
            draw.rectangle([0, 0, 950, 220], fill=PURPLE)
            draw.rectangle([0, 520, 950, 600], fill=PURPLE)
            
            try:
                font_bold = ImageFont.truetype("arialbd.ttf", 36)
                font_header = ImageFont.truetype("arialbd.ttf", 32)
                font_sub = ImageFont.truetype("arial.ttf", 24)
                font_label = ImageFont.truetype("arialbd.ttf", 30)
                font_details = ImageFont.truetype("arialbd.ttf", 36)
            except:
                font_bold = font_header = font_sub = font_label = font_details = ImageFont.load_default()

                # --- LOGO PATHS ---
            LOGO_LEFT_PATH = os.path.join(settings.BASE_DIR, 'canteen', 'static', 'logo.png')
            LOGO_RIGHT_PATH = os.path.join(settings.BASE_DIR, 'canteen', 'static', 'uzlogo.png')
            LOGO_SIZE = (110, 110) # Slightly smaller to give the text more breathing room

            # 2. Institutional Branding & Logos
            # Top Left Logo
            if os.path.exists(LOGO_LEFT_PATH):
                left_img = Image.open(LOGO_LEFT_PATH).convert("RGBA")
                left_img = left_img.resize(LOGO_SIZE, Image.LANCZOS)
                front.paste(left_img, (40, 45), left_img) # (x=40, y=45)

            # Top Right Logo
            if os.path.exists(LOGO_RIGHT_PATH):
                right_img = Image.open(LOGO_RIGHT_PATH).convert("RGBA")
                right_img = right_img.resize(LOGO_SIZE, Image.LANCZOS)
                front.paste(right_img, (800, 100), right_img) # (x=800, y=45)

            # Center Header Text
            draw.text((475, 40), "MORGENSTER TEACHERS COLLEGE", fill=WHITE, font=font_header, anchor="mm")
            draw.text((475, 75), "A Reformed Church in Zimbabwe Institution", fill=WHITE, font=font_sub, anchor="mm")
            draw.text((475, 110), "Ministry of Higher and Tertiary Education, Innovation,", fill=WHITE, font=font_sub, anchor="mm")
            draw.text((475, 135), "Science and Technology Development", fill=WHITE, font=font_sub, anchor="mm")

            # 3. Dynamic Logic (Intake & Status)
            reg_num = student.student_id.upper()
            
            # Logic: If MTJ34... -> Status: JUNIOR, Intake: 34
            # Logic: If MTE35... -> Status: ECD, Intake: 35
            status_text = "JUNIOR" if reg_num.startswith("MTJ") else "ECD" if reg_num.startswith("MTE") else "STUDENT"
            
            # Extract digits 4 and 5 (index 3 and 4) for the intake number
            try:
                auto_intake = reg_num[3:5] if len(reg_num) >= 5 else student.student_intake
            except:
                auto_intake = student.student_intake

            # 4. "STUDENT ID" Pill
            draw.rounded_rectangle([380, 165, 620, 210], radius=15, fill=GREEN)
            draw.text((500, 188), "STUDENT ID", fill=WHITE, font=font_label, anchor="mm")

            # 5. CIRCULAR PHOTO LOGIC
            photo_size = (260, 260)
            photo_pos = (60, 240)
            img_to_paste = None

            if student.photo and os.path.exists(student.photo.path):
                img_to_paste = Image.open(student.photo.path).convert("RGBA")
            elif os.path.exists(STATIC_LOGO_PATH):
                img_to_paste = Image.open(STATIC_LOGO_PATH).convert("RGBA")

            if img_to_paste:
                img_to_paste = ImageOps.fit(img_to_paste, photo_size, centering=(0.5, 0.5))
                mask = Image.new('L', photo_size, 0)
                ImageDraw.Draw(mask).ellipse((0, 0) + photo_size, fill=255)
                
                round_img = Image.new('RGBA', photo_size, (0, 0, 0, 0))
                round_img.paste(img_to_paste, (0, 0), mask=mask)
                front.paste(round_img, photo_pos, round_img)
                
                # Green Circle Border
                border_rect = [photo_pos[0]-3, photo_pos[1]-3, photo_pos[0]+photo_size[0]+3, photo_pos[1]+photo_size[1]+3]
                draw.ellipse(border_rect, outline=GREEN, width=6)

            # 6. Student Details
            details = [
                ("NAME", f": {student.full_name.upper()}"),
                ("INTAKE", f": {auto_intake}"),
                ("REG NO.", f": {reg_num}"),
            ]

            y_pos = 260
            for label, value in details:
                draw.text((340, y_pos), label, fill=DARK_TEXT, font=font_label)
                draw.text((520, y_pos), value, fill=DARK_TEXT, font=font_details)
                y_pos += 70

            # 7. Dynamic Status Pill (JUNIOR/ECD)
            draw.rounded_rectangle([420, 460, 680, 510], radius=20, fill=GREEN)
            draw.text((550, 485), status_text, fill=WHITE, font=font_label, anchor="mm")

            # 8. Footer Motto
            draw.text((475, 560), "LIGHT OF THE NATION", fill=WHITE, font=font_bold, anchor="mm")

            # --- BACK ---
            back = Image.new('RGB', CARD_SIZE, color=WHITE)
            draw_back = ImageDraw.Draw(back)
            qr = qrcode.QRCode(box_size=12, border=2)
            qr.add_data(student.student_id)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white").resize((300, 300))
            back.paste(qr_img, (325, 50))
            draw_back.text((475, 450), "MORGENSTER TEACHERS COLLEGE", fill=PURPLE, font=font_header, anchor="mm")
            draw_back.text((475, 520), "If lost and found, please return to Admin Office or Security", fill=(100,100,100), font=font_sub, anchor="mm")

            # Save Files
            front.save(f"{output_dir}/{student.student_id}_FRONT.png")
            back.save(f"{output_dir}/{student.student_id}_BACK.png")

        self.stdout.write(self.style.SUCCESS(f'Successfully generated {students.count()} cards with circular photos and auto-intake!'))