from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import os

def verify_pdf_formatting():
    """Verify the formatting in the generated PDF report"""
    image_path = 'report/test_output.pdf'
    
    try:
        # Convert first page of PDF to image
        pages = convert_from_path(image_path, first_page=1, last_page=1)
        if pages:
            # Save first page as image
            output_image = 'report/first_page.png'
            pages[0].save(output_image, 'PNG')
            
            # Extract text from image
            text = pytesseract.image_to_string(output_image)
            
            print('=== PDF First Page Content ===')
            print(text)
            print('=== End PDF Content ===')
            
            # Clean up temporary image
            if os.path.exists(output_image):
                os.remove(output_image)
            
            return text
    except Exception as e:
        print(f'Error reading PDF: {e}')
        return None

if __name__ == '__main__':
    verify_pdf_formatting()
