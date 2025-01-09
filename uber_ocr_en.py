from PIL import Image
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import pytesseract
import re

class UberReceiptProcessor:
    def __init__(self, output_path, images_per_page=4, orientation="horizontal"):
        self.output_path = output_path
        self.images_per_page = images_per_page
        self.orientation = orientation
        self.receipts = []
        self.total_amount = 0
        
        # Set initial page orientation
        self.set_page_orientation()
        
        # Adjust image dimensions based on layout
        self.image_width = (self.page_width - 150) / self.images_per_page  # Left/right margins 120, spacing 30
        self.image_height = self.page_height - 120  # Top/bottom margins
        
    def set_page_orientation(self):
        """Set page dimensions based on orientation"""
        if self.orientation == "horizontal":
            self.page_width, self.page_height = A4[::-1]  # Swap for landscape
        else:
            self.page_width, self.page_height = A4  # Portrait orientation

    def extract_info_from_image(self, image_path):
        """从图片中提取日期、金额和类型信息"""
        # 使用OCR提取文本
        # custom_config = r'--oem 3 --psm 6'
        # raw_text = pytesseract.image_to_string(Image.open(image_path),lang='eng+chi_sim')
        raw_text = pytesseract.image_to_string(Image.open(image_path),lang='eng')
        clean_text = raw_text.strip().lower()

        # 使用正则表达式提取信息
        if "eats" in clean_text:
            receipt_type = "Meal"
            date_pattern = r'(\w{3} \w{3} \d{1,2} \d{4})' # for meal
            date = re.search(date_pattern, clean_text)
            date_eng = date.group(1)
            print(date_eng)
        else:
            receipt_type = "Trip"
            # date_pattern = r"(\d{1,2}月\d{1,2}日\s*\d{1,2}:\d{2}[ap]m)" # for Chinese + English
            date_pattern = r"(\w{3}\s+\d{1,2}\s+\d{1,2}:\d{2}+[AP]M)" # for English
            date = re.search(date_pattern, clean_text, re.IGNORECASE)
            try:
                if date:
                    date_text = date.group(1).strip().lower()
                    date_text = "2024 " + date_text
                    print(date_text)
                    date_eng = datetime.strptime(date_text,"%Y %b %d %I:%M%p")
                    # date_eng = date_obj.strftime("%b %d, %Y %I:%M %p")
                    print(date_eng)
                else:
                    print(f"no date matched:{image_path}")
                    date_eng = "not recognized"
                    # print("==== clean text ====")
                    # print(clean_text)
            except:
                    print("==== clean text ====")
                    print(clean_text)

        amount_pattern = r'(\$?\d+\.\d{2})'
        amount = re.search(amount_pattern, clean_text)

        return {
            'date': date_eng,
            'amount': float(amount.group().replace('$', '')) if amount else 0.0,
            'type': receipt_type,
            'path': image_path
        }

    def sort_receipts_by_time(self, descending=False):
        """
        Sort receipts by time, with invalid dates pushed to the end.
        
        Args:
            descending (bool): If True, sort newest to oldest. If False, oldest to newest.
        """
        def get_sort_key(receipt):
            date = receipt['date']
            if isinstance(date, datetime):
                return (0, date)  # Valid dates first, sorted by date
            elif isinstance(date, str) and date != "not recognized":
                try:
                    # Try to parse string dates
                    parsed_date = datetime.strptime(date, "%b %d, %Y")
                    return (0, parsed_date)
                except (ValueError, TypeError):
                    return (1, datetime.min)  # Invalid dates to end
            return (1, datetime.min)  # Unknown dates to end
        
        self.receipts.sort(key=get_sort_key, reverse=descending)

    def add_receipt(self, image_path):
        """添加收据图片及其信息"""
        print("=====" * 20)
        print(f"Processing: {image_path}")
        receipt_info = self.extract_info_from_image(image_path)
        self.receipts.append(receipt_info)
        self.total_amount += receipt_info['amount']

    def draw_detailed_summary_table(self, canvas_instance, start_y):
        """
        Draws each receipt's type, amount, and date in a table-style layout.
        
        Args:
            canvas_instance: ReportLab canvas to draw on
            start_y: Starting Y coordinate for the table
            
        Returns:
            float: Updated Y position after drawing the table
        """
        # Initialize position and styling
        y_position = start_y
        canvas_instance.setFont("Helvetica-Bold", 12)
        canvas_instance.drawString(30, y_position, "Receipt Details:")
        y_position -= 25
        
        # Draw table header
        canvas_instance.setFont("Helvetica-Bold", 10)
        canvas_instance.drawString(30, y_position, "Type")
        canvas_instance.drawString(130, y_position, "Amount")
        canvas_instance.drawString(230, y_position, "Date")
        y_position -= 20
        
        # Draw horizontal line under header
        canvas_instance.line(30, y_position + 5, 530, y_position + 5)
        
        # Draw table content
        canvas_instance.setFont("Helvetica", 10)
        for receipt in self.receipts:
            # Check if we need a new page
            if y_position < 50:
                canvas_instance.showPage()
                canvas_instance.setFont("Helvetica", 10)
                y_position = self.page_height - 50
            
            # Format date string
            date_str = str(receipt['date'])
            if isinstance(receipt['date'], datetime):
                date_str = receipt['date'].strftime("%b %d, %Y")
            
            # Draw row content
            canvas_instance.drawString(30, y_position, str(receipt['type']))
            canvas_instance.drawString(130, y_position, f"${receipt['amount']:.2f}")
            canvas_instance.drawString(230, y_position, date_str)
            
            # Update position for next row
            y_position -= 20
        
        return y_position

    def create_pdf(self):
        """Generate PDF report with summary and receipt details"""
        print(f"Creating PDF to: {self.output_path}")
        
        # Sort receipts by time before generating PDF
        self.sort_receipts_by_time()
        
        # Set page orientation and create canvas
        self.set_page_orientation()  # Update page dimensions based on orientation
        if self.orientation == "horizontal":
            c = canvas.Canvas(self.output_path, pagesize=A4[::-1])
        else:
            c = canvas.Canvas(self.output_path, pagesize=A4)

        # First page: Summary
        c.setFont("Helvetica-Bold", 16)
        c.drawString(30, self.page_height - 30, "Uber expense report - Summary")

        # Amount summary section
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, self.page_height - 60, "Amount summary:")

        c.setFont("Helvetica", 12)
        y = self.page_height - 80

        # Calculate type summary
        type_summary = {}
        for receipt in self.receipts:
            type_summary[receipt['type']] = type_summary.get(receipt['type'], 0) + receipt['amount']

        # Draw type summary
        for receipt_type, amount in type_summary.items():
            c.drawString(30, y, f"{receipt_type} Total: ${amount:.2f}")
            y -= 20

        # Draw total amount
        c.drawString(30, y - 20, f"Total: ${self.total_amount:.2f}")
        
        # Add detailed receipt table
        y = self.draw_detailed_summary_table(c, y - 60)
        
        # End first page
        c.showPage()

        # Subsequent pages: Receipt images
        current_page = 1
        images_per_row = min(self.images_per_page, 5)  # Limit to max 5 receipts per page
        spacing = (self.page_width - 60) / images_per_row  # Distribute space evenly
        
        for i, receipt in enumerate(self.receipts):
            if i % images_per_row == 0:
                if i > 0:
                    c.showPage()
                current_page += 1
                c.setFont("Helvetica-Bold", 16)
                c.drawString(30, self.page_height - 30, f"Uber expense report - Page {current_page}")
            
            # Calculate image position
            col = i % images_per_row
            
            # Calculate x and y coordinates with even spacing
            x = 30 + col * spacing
            y = self.page_height - 60  # Fixed y-coordinate for single row layout

            # 添加图片
            img = Image.open(receipt['path'])
            aspect = img.width / img.height
            img_height = self.image_height
            img_width = img_height * aspect
            if img_width > self.image_width:
                img_width = self.image_width
                img_height = img_width / aspect

            # 居中显示图片
            x_centered = x + (self.image_width - img_width) / 2

            c.drawImage(receipt['path'],
                       x_centered,
                       y - img_height,
                       width=img_width,
                       height=img_height)

            # 添加收据信息
            c.setFont("Helvetica", 12)
            info_y = y - img_height - 15

            c.drawString(x, info_y,
                        f"Type: {receipt['type']}")

            c.drawString(x, info_y - 15,
                        f"Time: {receipt['date']}")

            c.drawString(x, info_y - 30,
                        f"Amount: ${receipt['amount']:.2f}")

        print("PDF report generated....")
        c.save()

# 使用示例
if __name__ == "__main__":
    # 指定包含收据图片的文件夹路径
    receipt_folder = "receipts"
    output_path = "report/expense_demo.pdf"

    processor = UberReceiptProcessor(output_path)
    for filename in os.listdir(receipt_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(receipt_folder, filename)
            processor.add_receipt(image_path)

    print("=====" * 20)
    print(f"Creating PDF and summarize")
    processor.create_pdf()
    total = processor.total_amount
    print("===== report generated =====")
    print(f"total amount$: ${total:.2f}")
    # total = process_receipts(receipt_folder, output_path)
    # print(f"报告已生成，总金额: ${total:.2f}")
