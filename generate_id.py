import qrcode

# CHANGE THIS to match the 'Qr code data' in your Django Admin
student_data = "TEST120" 

# Generate the QR
img = qrcode.make(student_data)

# Save it as an image
img.save("my_student_id.png")

print(f"Success! QR code for '{student_data}' saved as 'my_student_id.png'")