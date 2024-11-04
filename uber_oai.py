import os
import base64
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from anthropic import Anthropic
import re
import json
from io import BytesIO
import numpy as np

class UberReceiptProcessor:
    def __init__(self, api_key, output_path="expense_report.pdf"):
        self.output_path = output_path
        self.receipts = []
        self.total_amount = 0
        self.client = Anthropic(api_key=api_key)
        
        # A4纸张尺寸（单位：点）
        self.page_width, self.page_height = A4
        
        # 设置图片在PDF中的大小（宽度为A4纸张宽度的一半）
        self.image_width = self.page_width / 2 - 40
        self.image_height = self.page_height / 3 - 40

    def image_to_base64(self, image_path):
        """将图片转换为base64编码"""
        with Image.open(image_path) as img:
            # 转换为RGB模式（如果是RGBA）
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # 将图片保存到内存中的BytesIO对象
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            
            # 获取base64编码
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return img_str

    def extract_info_from_image_oai(self, image_path):
        """使用Claude Vision API从图片中提取信息"""
        try:
            # 将图片转换为base64
            base64_image = self.image_to_base64(image_path)
            
            # 构造提示词
            prompt = """请分析这张Uber收据截图, 并以JSON格式返回以下信息:
            1. 日期 (date)
            2. 金额 (amount) - 只需要数字，不需要货币符号
            3. 类型 (type) - "打车"或"外卖"
            请返回格式如下：
            {
                "date": "YYYY-MM-DD",
                "amount": XX.XX,
                "type": "Trip/Meal"
            }
            只返回JSON, 不需要其他解释。"""
            
            # 调用Claude API
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": base64_image
                                }
                            }
                        ]
                    }
                ]
            )
            
            # 解析返回的JSON
            result = json.loads(message.content[0].text)
            result['path'] = image_path
            return result
            
        except Exception as e:
            print(f"处理图片时发生错误: {str(e)}")
            return {
                'date': "未知日期",
                'amount': 0.0,
                'type': "未知",
                'path': image_path
            }

    def add_receipt(self, image_path):
        """添加收据图片及其信息"""
        receipt_info = self.extract_info_from_image(image_path)
        self.receipts.append(receipt_info)
        self.total_amount += receipt_info['amount']

    def create_pdf(self):
        """生成PDF报告"""
        c = canvas.Canvas(self.output_path, pagesize=A4)
        
        # 添加标题
        c.setFont("Helvetica-Bold", 16)
        c.drawString(30, self.page_height - 30, "Uber费用报告")
        
        current_y = self.page_height - 60
        images_per_page = 4
        current_image = 0
        
        for receipt in self.receipts:
            if current_image > 0 and current_image % images_per_page == 0:
                c.showPage()
                current_y = self.page_height - 60
            
            # 添加图片
            img = Image.open(receipt['path'])
            aspect = img.width / img.height
            img_height = self.image_height
            img_width = img_height * aspect
            if img_width > self.image_width:
                img_width = self.image_width
                img_height = img_width / aspect
            
            c.drawImage(receipt['path'], 
                       30 + (current_image % 2) * (self.page_width/2), 
                       current_y - img_height,
                       width=img_width, 
                       height=img_height)
            
            # 添加收据信息
            c.setFont("Helvetica", 10)
            info_y = current_y - img_height - 15
            c.drawString(30 + (current_image % 2) * (self.page_width/2),
                        info_y,
                        f"日期: {receipt['date']} | 金额: ${receipt['amount']:.2f} | 类型: {receipt['type']}")
            
            current_image += 1
            if current_image % 2 == 0:
                current_y -= (img_height + 40)
        
        # 添加总结页
        c.showPage()
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, self.page_height - 30, "费用总结")
        
        c.setFont("Helvetica", 12)
        y = self.page_height - 60
        
        # 按类型汇总
        type_summary = {}
        for receipt in self.receipts:
            type_summary[receipt['type']] = type_summary.get(receipt['type'], 0) + receipt['amount']
        
        for receipt_type, amount in type_summary.items():
            c.drawString(30, y, f"{receipt_type}总额: ${amount:.2f}")
            y -= 20
        
        c.drawString(30, y - 20, f"总计: ${self.total_amount:.2f}")
        c.save()

def process_receipts(api_key, receipt_folder, output_path="expense_report.pdf"):
    """处理指定文件夹中的所有收据图片"""
    processor = UberReceiptProcessor(api_key, output_path)
    
    # 处理文件夹中的所有图片
    for filename in os.listdir(receipt_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(receipt_folder, filename)
            processor.add_receipt(image_path)
    
    processor.create_pdf()
    return processor.total_amount

# 使用示例
if __name__ == "__main__":
    # 设置你的Anthropic API密钥
    api_key = "your-api-key-here"
    
    # 指定包含收据图片的文件夹路径
    receipt_folder = "receipts"
    total = process_receipts(api_key, receipt_folder, "uber_expense_report.pdf")
    print(f"报告已生成，总金额: ${total:.2f}")