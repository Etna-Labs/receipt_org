import os
from pathlib import Path
from uber_ocr_en import UberReceiptProcessor

def test_pdf_generation():
    # Get test receipt files
    test_dir = Path(__file__).parent / "test_receipts"
    test_files = sorted(list(test_dir.glob("*.png")))
    
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent / "report"
    output_dir.mkdir(exist_ok=True)
    
    # Initialize processor with test configuration
    processor = UberReceiptProcessor(
        str(output_dir / "test_output.pdf"),
        images_per_page=4,
        orientation="horizontal"
    )
    
    # Process each test receipt
    print("\nProcessing test receipts:")
    print("-" * 50)
    for file in test_files:
        print(f"\nProcessing {file.name}:")
        receipt_info = processor.extract_info_from_image(str(file))
        print(f"Type: {receipt_info['type']}")
        print(f"Date: {receipt_info['date']}")
        print(f"Amount: ${receipt_info['amount']:.2f}")
        processor.add_receipt(str(file))
    
    # Sort receipts by time (newest first)
    processor.sort_receipts_by_time(descending=True)
    
    # Generate PDF
    print("\nGenerating PDF report...")
    processor.create_pdf()
    print(f"\nPDF generated at: {processor.output_path}")
    print(f"Total amount: ${processor.total_amount:.2f}")

if __name__ == "__main__":
    test_pdf_generation()
