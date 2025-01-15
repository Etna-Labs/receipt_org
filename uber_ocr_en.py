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
    def __init__(self, output_path, images_per_page=4):
        self.output_path = output_path
        self.images_per_page = images_per_page
        self.receipts = []
        self.total_amount = 0

        # 使用横向A4纸张
        self.page_width, self.page_height = A4[::-1]  # 交换宽高以获得横向布局

        # 调整图片尺寸以适应1x4布局
        self.image_width = (self.page_width - 150) / 4  # 左右总边距120，图片间距30
        self.image_height = self.page_height - 120  # 上下留边距

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

    def add_receipt(self, image_path):
        """添加收据图片及其信息"""
        print("=====" * 20)
        print(f"Processing: {image_path}")
        receipt_info = self.extract_info_from_image(image_path)
        self.receipts.append(receipt_info)
        self.total_amount += receipt_info['amount']

    def create_pdf(self):
        """生成PDF报告"""
        print(f"Creating PDF to:{self.output_path}")
        c = canvas.Canvas(self.output_path, pagesize=A4[::-1])  # 使用横向A4

        # 第一页：总结页
        c.setFont("Helvetica-Bold", 16)
        c.drawString(30, self.page_height - 30, "Uber expense report - Summary")

        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, self.page_height - 60, "Amount summary:")

        c.setFont("Helvetica", 12)
        y = self.page_height - 80

        # 按类型汇总
        type_summary = {}
        for receipt in self.receipts:
            type_summary[receipt['type']] = type_summary.get(receipt['type'], 0) + receipt['amount']

        print(type_summary)

        for receipt_type, amount in type_summary.items():
            c.drawString(30, y, f"{receipt_type} Total: ${amount:.2f}")
            y -= 20

        c.drawString(30, y - 20, f"Total: ${self.total_amount:.2f}")

        # 结束第一页
        c.showPage()

        # 后续页面：收据图片
        current_page = 1
        images_per_row = self.images_per_page
        rows_per_page = 1

        for i, receipt in enumerate(self.receipts):
            if i % self.images_per_page == 0:
                if i > 0:
                    c.showPage()
                current_page += 1
                c.setFont("Helvetica-Bold", 16)
                c.drawString(30, self.page_height - 30, f"Uber expense report - Page {current_page}")

            # 计算当前图片在页面上的位置
            col = i % images_per_row

            # 计算x和y坐标（每列之间间距30）
            x = 30 + col * (self.image_width + 30)
            y = self.page_height - 60  # 固定y坐标，因为只有一行

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

    def create_pdf_enhanced(self, orientation: str = "horizontal", images_per_page: int = 4):
        """
        Creates a PDF report with user-picked orientation and configurable images per page.
        
        Args:
            orientation (str): Either "horizontal" or "vertical"
            images_per_page (int): Number of images per page (3-5)
            
        The PDF includes:
        1. A summary page with time-ordered receipt details
        2. Configurable layout with 3-5 receipts per page
        3. User-selected page orientation
        """
        print(f"Creating enhanced PDF to: {self.output_path}")
        
        # Set page orientation
        if orientation.lower() == "horizontal":
            pagesize = A4[::-1]  # Swap width/height for horizontal
        else:
            pagesize = A4  # Regular A4 for vertical
            
        c = canvas.Canvas(self.output_path, pagesize=pagesize)
        page_width, page_height = pagesize
        
        # Sort receipts by date
        sorted_receipts = sorted(
            self.receipts,
            key=lambda x: x['date'] if isinstance(x['date'], datetime) else datetime.max
        )
        
        # Create summary page
        self.create_pdf_enhanced_summary_page(c, page_width, page_height)
        
        # Add receipt pages
        self.create_pdf_enhanced_finish(c, sorted_receipts, page_width, page_height, orientation, images_per_page)

    def create_pdf_enhanced_summary_page(self, canvas, page_width, page_height):
        """Creates an enhanced summary page with a time-ordered receipt table"""
        canvas.setFont("Helvetica-Bold", 16)
        canvas.drawString(30, page_height - 30, "Uber Expense Report - Detailed Summary")
        
        # Sort receipts by date if possible
        sorted_receipts = sorted(
            self.receipts,
            key=lambda x: x['date'] if isinstance(x['date'], datetime) else datetime.max
        )
        
        # Draw table headers
        canvas.setFont("Helvetica-Bold", 12)
        y = page_height - 80
        headers = ["Date", "Type", "Amount"]
        col_widths = [200, 100, 100]
        x_positions = [30]  # Start position
        for width in col_widths[:-1]:
            x_positions.append(x_positions[-1] + width)
            
        for header, x in zip(headers, x_positions):
            canvas.drawString(x, y, header)
            
        # Draw horizontal line under headers
        y -= 5
        canvas.line(30, y, sum(col_widths) + 30, y)
        y -= 15
        
        # Draw receipt rows
        canvas.setFont("Helvetica", 12)
        for receipt in sorted_receipts:
            date_str = receipt['date'] if isinstance(receipt['date'], str) else receipt['date'].strftime("%b %d, %Y %I:%M %p")
            canvas.drawString(x_positions[0], y, date_str)
            canvas.drawString(x_positions[1], y, receipt['type'])
            canvas.drawString(x_positions[2], y, f"${receipt['amount']:.2f}")
            y -= 20
            
        # Draw summary section
        y -= 20
        canvas.setFont("Helvetica-Bold", 14)
        canvas.drawString(30, y, "Amount Summary by Type:")
        y -= 25
        
        # Calculate and display type summaries
        type_summary = {}
        for receipt in self.receipts:
            type_summary[receipt['type']] = type_summary.get(receipt['type'], 0) + receipt['amount']
            
        canvas.setFont("Helvetica", 12)
        for receipt_type, amount in type_summary.items():
            canvas.drawString(30, y, f"{receipt_type}: ${amount:.2f}")
            y -= 20
            
        # Display total
        y -= 10
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(30, y, f"Total Amount: ${self.total_amount:.2f}")
        
        canvas.showPage()

    def create_pdf_enhanced_finish(self, canvas, sorted_receipts, page_width, page_height, orientation, images_per_page):
        """Adds receipt images to the PDF with the specified layout"""
        margin = 30
        spacing = 30
        current_page = 1
        
        if orientation.lower() == "horizontal":
            image_width = (page_width - (margin * 2) - (spacing * (images_per_page - 1))) / images_per_page
            image_height = page_height - (margin * 2)
            images_per_row = images_per_page
            rows_per_page = 1
        else:
            image_width = page_width - (margin * 2)
            image_height = (page_height - (margin * 2) - (spacing * (images_per_page - 1))) / images_per_page
            images_per_row = 1
            rows_per_page = images_per_page
            
        for i, receipt in enumerate(sorted_receipts):
            if i % (images_per_row * rows_per_page) == 0:
                if i > 0:
                    canvas.showPage()
                current_page += 1
                canvas.setFont("Helvetica-Bold", 16)
                canvas.drawString(margin, page_height - 30, f"Uber Expense Report - Page {current_page}")
                
            # Calculate position
            pos_in_page = i % (images_per_row * rows_per_page)
            if orientation.lower() == "horizontal":
                col = pos_in_page % images_per_row
                row = 0
            else:
                col = 0
                row = pos_in_page % rows_per_page
                
            # Calculate x and y coordinates
            x = margin + col * (image_width + spacing)
            y = page_height - margin - row * (image_height + spacing)
            
            # Add image
            img = Image.open(receipt['path'])
            aspect = img.width / img.height
            
            if orientation.lower() == "horizontal":
                img_height = image_height
                img_width = img_height * aspect
                if img_width > image_width:
                    img_width = image_width
                    img_height = img_width / aspect
            else:
                img_width = image_width
                img_height = img_width / aspect
                if img_height > image_height:
                    img_height = image_height
                    img_width = img_height * aspect
                    
            # Center image in its space
            x_centered = x + (image_width - img_width) / 2
            y_centered = y - (image_height + img_height) / 2
            
            canvas.drawImage(receipt['path'],
                           x_centered,
                           y_centered,
                           width=img_width,
                           height=img_height)
                           
            # Add receipt information
            info_y = y - image_height - 15 if orientation.lower() == "horizontal" else y_centered - img_height/2 - 45
            canvas.setFont("Helvetica", 12)
            
            canvas.drawString(x, info_y, f"Type: {receipt['type']}")
            canvas.drawString(x, info_y - 15, f"Time: {receipt['date']}")
            canvas.drawString(x, info_y - 30, f"Amount: ${receipt['amount']:.2f}")

# Test the enhanced PDF generation
if __name__ == "__main__":
    # Create output directory if it doesn't exist
    os.makedirs("report", exist_ok=True)
    
    # Test both horizontal and vertical orientations
    orientations = ["horizontal", "vertical"]
    images_per_page_options = [3, 4, 5]
    
    for orientation in orientations:
        for images_per_page in images_per_page_options:
            print(f"\nTesting {orientation} orientation with {images_per_page} images per page")
            output_path = f"report/expense_demo_{orientation}_{images_per_page}.pdf"
            
            processor = UberReceiptProcessor(output_path)
            
            # Process all images in receipts folder
            for filename in sorted(os.listdir("receipts")):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join("receipts", filename)
                    processor.add_receipt(image_path)
            
            print("=" * 50)
            print(f"Creating enhanced PDF with {orientation} orientation")
            print(f"Images per page: {images_per_page}")
            processor.create_pdf_enhanced(
                orientation=orientation,
                images_per_page=images_per_page
            )
            print(f"Total amount: ${processor.total_amount:.2f}")
            print(f"PDF generated: {output_path}")
            print("=" * 50)
