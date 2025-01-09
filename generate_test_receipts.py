from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime, timedelta

def create_test_receipt(output_path, receipt_type, date, amount):
    # Create a new image with white background
    width = 800
    height = 1200
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Try to load Arial font, fall back to default if not available
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        date_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except:
        font = ImageFont.load_default()
        date_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Draw receipt content
    if receipt_type == "Meal":
        # Uber Eats style receipt
        draw.text((50, 50), "Uber Eats", font=font, fill='black')
        # Format date as "Mon Mar 15 2024" to match OCR pattern
        date_str = f"{date.strftime('%a %b %d %Y').upper()}"
        draw.text((50, 150), date_str, font=date_font, fill='black')
        draw.text((50, 200), "Your Order", font=small_font, fill='black')
        draw.text((50, 250), "Test Restaurant", font=small_font, fill='black')
        draw.text((50, 350), f"Total: ${amount:.2f}", font=small_font, fill='black')
    else:
        # Uber ride style receipt
        draw.text((50, 50), "Uber", font=font, fill='black')
        draw.text((50, 150), "Trip completed", font=small_font, fill='black')
        # Format date as "Mar 15 12:30PM" to match OCR pattern
        date_str = f"{date.strftime('%b %d %I:%M%p')}"
        draw.text((50, 200), date_str, font=date_font, fill='black')
        draw.text((50, 300), "Thanks for riding, Test User", font=small_font, fill='black')
        draw.text((50, 350), f"Total: ${amount:.2f}", font=small_font, fill='black')

    # Save the image
    image.save(output_path)

def generate_test_receipts():
    # Create receipts directory if it doesn't exist
    receipts_dir = "test_receipts"
    os.makedirs(receipts_dir, exist_ok=True)

    # Generate test data
    base_date = datetime.now()
    test_data = [
        # Meals
        ("Meal", base_date - timedelta(days=5), 25.99),
        ("Meal", base_date - timedelta(days=3), 42.50),
        ("Meal", base_date - timedelta(days=1), 18.75),
        # Trips
        ("Trip", base_date - timedelta(days=4), 15.50),
        ("Trip", base_date - timedelta(days=2), 28.75),
        ("Trip", base_date, 35.25),
    ]

    # Generate receipts
    for i, (receipt_type, date, amount) in enumerate(test_data):
        output_path = os.path.join(receipts_dir, f"test_receipt_{i+1}.png")
        create_test_receipt(output_path, receipt_type, date, amount)
        print(f"Generated {receipt_type} receipt for {date} with amount ${amount:.2f}")

if __name__ == "__main__":
    generate_test_receipts()
