import streamlit as st
from pathlib import Path
import tempfile
from uber_ocr_en import UberReceiptProcessor
import os
import base64
import pandas as pd
import datetime


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

        # Page orientation control
        orientation = st.selectbox(
            "Page Orientation",
            ["horizontal", "vertical"],
            index=0,
            help="Choose between horizontal (landscape) or vertical (portrait) layout"
        )

        # Images per page control (3-5 range)
        images_per_page = st.number_input(
            "Receipts per page (2-5)",
            min_value=2,
            max_value=5,
            value=4,
            help="Number of receipt images to display per page (3-5)"
        )

        # Sort direction control
        sort_descending = st.checkbox(
            "Newest receipts first",
            value=True,
            help="Sort receipts by date (newest to oldest when checked)"
        )

    # Preview section
    if uploaded_files:
        st.subheader(f"Preview ({len(uploaded_files)} files)")

        # Create a grid layout for previews
        cols = st.columns(5)
        for idx, file in enumerate(uploaded_files):
            with cols[idx % 4]:
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
                        output_pdf = Path(__file__).parent / "report"/"streamlit_output.pdf"
                        processor = UberReceiptProcessor(
                            str(output_pdf),
                            images_per_page=images_per_page,
                            orientation=orientation
                        )

                        # Sort receipts based on user preference
                        processor.sort_receipts_by_time(descending=sort_descending)

                        # Process each receipt
                        receipt_info = []
                        for idx, file in enumerate(saved_files):
                            processor.add_receipt(str(file))
                            receipt_info.append(processor.receipts[-1])
                            # info = processor.extract_info_from_image(str(file))
                            # receipt_info.append((file.name, info))

                            # Update progress
                            progress = 0.5 + (idx + 1) / (len(uploaded_files) * 2)  # Second half for processing
                            progress_bar.progress(progress)
                            status_text.text(f"Processing receipt {idx + 1} of {len(uploaded_files)}...")

                        # Generate PDF
                        processor.create_pdf()
                        progress_bar.progress(1.0)
                        status_text.text("Processing complete...")

                        # Show results
                        st.success("✅ All receipts processed successfully!")

                       # Display receipt information in a table
                        if receipt_info:
                            st.subheader("Receipt Details")
                            # Create a list of dictionaries for the table
                            table_data = []
                            for receipt in receipt_info:
                                # Convert the receipt string to a dictionary
                                receipt_dict = eval(str(receipt))
                                # Format the date to be more readable
                                receipt_dict['date'] = receipt_dict['date'].strftime('%Y-%m-%d %H:%M')
                                # Remove the path as it's not needed in the display
                                receipt_dict.pop('path', None)
                                table_data.append(receipt_dict)

                            # Convert to DataFrame and display
                            import pandas as pd
                            df = pd.DataFrame(table_data)
                            # Reorder columns if needed
                            df = df[['date', 'type', 'amount']]
                            # Rename columns for better display
                            df.columns = ['Date', 'Type', 'Amount ($)']
                            st.dataframe(df, use_container_width=True)

                        # Offer PDF download
                        with open(output_pdf, "rb") as pdf_file:
                            st.download_button(
                                "📥 Download Report",
                                pdf_file,
                                "streamlit_uber_receipts_report.pdf",
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
