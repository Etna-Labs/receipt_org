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
        images_per_row = 4
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

        c.save()

def process_receipts(receipt_folder, output_path):
    """处理指定文件夹中的所有收据图片"""
    processor = UberReceiptProcessor(output_path)

    # 处理文件夹中的所有图片
    for filename in os.listdir(receipt_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(receipt_folder, filename)
            processor.add_receipt(image_path)

    print("===" * 20)
    print("Creating PDF and summarize")

    processor.create_pdf()
    total = processor.total_amount
    print(f"total amount$:, ${total:.2f}")
    return total

# 使用示例
if __name__ == "__main__":
    # 指定包含收据图片的文件夹路径
    receipt_folder = "receipts"
    output_path = "report/expense_demo.pdf"
    total = process_receipts(receipt_folder, output_path)
    print(f"报告已生成，总金额: ${total:.2f}")
