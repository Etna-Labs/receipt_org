"""
FastAPI web application for processing Uber receipts.

This application provides a web interface for uploading Uber receipt images,
processes them using OCR or LLM-based extraction, and generates a consolidated PDF report.
Key features:
- File upload interface
- Receipt information extraction
- PDF report generation
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import logging
import shutil
import os
from typing import List
# from uber_ocr_en import UberReceiptProcessor # using ocr
from uber_llm_ocr import UberReceiptProcessor # using llm
from tempfile import NamedTemporaryFile

app = FastAPI()

# 设置静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 创建上传目录
# UPLOAD_DIR = Path("receipts")
# UPLOAD_DIR.mkdir(exist_ok=True)
# OUTPUT_DIR = Path("report")
# OUTPUT_DIR.mkdir(exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def process_receipts(
    files: List[UploadFile],
    background_tasks: BackgroundTasks,
    images_per_page: int = Form(4)
    ):

    # Validate input files
    if not files:
        raise HTTPException(status_code=400, detail="No files were uploaded")

    # Using temp files to handle uploaded images and pdf
    with NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        temp_path = tmp_file.name

        # Save uploaded files to temporary location
        temp_files = []
        for file in files:
            if file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                with NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as f:
                    shutil.copyfileobj(file.file, f)
                    temp_files.append(f.name)

        # Process receipts
        processor = UberReceiptProcessor(
            output_path=temp_path,
            images_per_page=images_per_page
        )

        for file_path in temp_files:
            processor.add_receipt(file_path)
        processor.create_pdf()

        # Clean up temporary image files
        for file_path in temp_files:
            try:
                os.unlink(file_path)
            except Exception as e:
                logging.error(f"Error deleting temporary file {file_path}: {e}")

        # Return the PDF file
        try:
            response = FileResponse(
                temp_path,
                headers={
                    'Content-Type': 'application/pdf',
                    'Content-Disposition': f'inline; filename="expense_report.pdf"'
                }
            )
            # Delete the temporary PDF file after it's been sent
            background_tasks.add_task(os.unlink, temp_path)
            return response
        except Exception as e:
            logging.error(f"Error sending PDF file: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # 处理收据
    # output_path = str(OUTPUT_DIR / "expense_report.pdf")

    # processor = UberReceiptProcessor(
    #     output_path=output_path,
    #     images_per_page=images_per_page
    # )

    # for file in files:
    #     if file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
    #         file_path = UPLOAD_DIR / file.filename
    #         processor.add_receipt(str(file_path))
    # processor.create_pdf()

    # filename = os.path.basename(output_path)
    # return FileResponse(
    #     output_path,
    #     # media_type='application/pdf',
    #     headers={
    #         'Content-Type': 'application/pdf',
    #         'Content-Disposition': f'inline; filename="{filename}"'
    #     }
    # )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
