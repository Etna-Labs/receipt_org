import streamlit as st
from pathlib import Path
import tempfile
from uber_ocr import UberReceiptProcessor
import os

st.set_page_config(
    page_title="Uber Receipt Processor",
    page_icon="🧾",
    layout="wide"
)

def main():
    st.title("🧾 Uber Receipt Processor")
    st.write("Upload your Uber receipts and get an organized PDF report")

    # File upload section with drag & drop
    uploaded_files = st.file_uploader(
        "Drop your Uber receipts here",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        help="You can upload multiple receipt images at once"
    )

    # Sidebar for options
    with st.sidebar:
        st.header("Settings")
        images_per_page = st.number_input(
            "Images per page",
            min_value=1,
            max_value=6,
            value=4,
            help="Number of receipt images to display per page in the PDF"
        )

    # Preview section
    if uploaded_files:
        st.subheader(f"Preview ({len(uploaded_files)} files)")

        # Create a grid layout for previews
        cols = st.columns(3)
        for idx, file in enumerate(uploaded_files):
            with cols[idx % 3]:
                st.image(file, caption=file.name, use_column_width=True)

        # Process button
        if st.button("Process Receipts", type="primary"):
            with st.spinner("Processing receipts..."):
                try:
                    # Create temporary directory for processing
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_dir = Path(temp_dir)

                        # Progress bar
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        # Save uploaded files
                        saved_files = []
                        for idx, file in enumerate(uploaded_files):
                            temp_file = temp_dir / file.name
                            temp_file.write_bytes(file.getvalue())
                            saved_files.append(temp_file)

                            # Update progress
                            progress = (idx + 1) / (len(uploaded_files) * 2)  # First half for saving
                            progress_bar.progress(progress)
                            status_text.text(f"Saving file {idx + 1} of {len(uploaded_files)}...")

                        # Process receipts
                        output_pdf = temp_dir / "output.pdf"
                        processor = UberReceiptProcessor(
                            str(output_pdf),
                            images_per_page=images_per_page
                        )

                        # Process each receipt
                        receipt_info = []
                        for idx, file in enumerate(saved_files):
                            info = processor.extract_info_from_image(str(file))
                            receipt_info.append((file.name, info))

                            # Update progress
                            progress = 0.5 + (idx + 1) / (len(uploaded_files) * 2)  # Second half for processing
                            progress_bar.progress(progress)
                            status_text.text(f"Processing receipt {idx + 1} of {len(uploaded_files)}...")

                        # Generate PDF
                        processor.create_pdf()
                        progress_bar.progress(1.0)
                        status_text.text("Processing complete!")

                        # Show results
                        st.success("✅ All receipts processed successfully!")

                        # Display receipt information in a table
                        if receipt_info:
                            st.subheader("Receipt Details")
                            for name, info in receipt_info:
                                st.write(f"**{name}**: {info}")

                        # Offer PDF download
                        with open(output_pdf, "rb") as pdf_file:
                            st.download_button(
                                "📥 Download Report",
                                pdf_file,
                                "uber_receipts_report.pdf",
                                "application/pdf",
                                use_container_width=True
                            )

                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
                    st.write("Please make sure all files are valid receipt images and try again.")
    else:
        # Show instructions when no files are uploaded
        st.info("👆 Upload your Uber receipt images to get started!")

        # Example section
        with st.expander("See example usage"):
            st.write("""
            1. Click the upload area above or drag and drop your receipt images
            2. Adjust the number of images per page in the sidebar if needed
            3. Click 'Process Receipts' to generate your report
            4. Download the organized PDF report
            """)

if __name__ == "__main__":
    main()
