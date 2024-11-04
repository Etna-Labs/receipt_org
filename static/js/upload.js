document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const previewArea = document.getElementById('previewArea');
    const submitBtn = document.getElementById('submitBtn');

    // 点击上传区域触发文件选择
    dropZone.addEventListener('click', () => fileInput.click());

    // 处理文件选择
    fileInput.addEventListener('change', handleFiles);

    // 处理拖放
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#000';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = '#ccc';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#ccc';
        handleFiles({ target: { files: e.dataTransfer.files } });
    });

    function handleFiles(e) {
        const files = Array.from(e.target.files);
        
        files.forEach(file => {
            if (file.type.startsWith('image/') || file.type === 'application/pdf') {
                const reader = new FileReader();
                const previewContainer = document.createElement('div');
                previewContainer.className = 'preview-container';

                reader.onload = function(e) {
                    if (file.type.startsWith('image/')) {
                        const img = document.createElement('img');
                        img.src = e.target.result;
                        img.className = 'preview-image';
                        previewContainer.appendChild(img);
                    } else {
                        // PDF 预览
                        const pdfIcon = document.createElement('div');
                        pdfIcon.textContent = 'PDF';
                        pdfIcon.style.textAlign = 'center'; 
                        pdfIcon.style.lineHeight = '200px';
                        previewContainer.appendChild(pdfIcon);
                    }

                    // 添加删除按钮
                    const deleteBtn = document.createElement('button');
                    deleteBtn.className = 'delete-btn';
                    deleteBtn.innerHTML = 'x';
                    deleteBtn.onclick = function() {
                        previewContainer.remove();
                        updateSubmitButton();
                    };
                    previewContainer.appendChild(deleteBtn);
                };

                reader.readAsDataURL(file);
                previewArea.appendChild(previewContainer);
                updateSubmitButton();
            }
        });
    }

    // 在 updateSubmitButton 函数前添加以下代码
    submitBtn.addEventListener('click', async function() {
        const formData = new FormData();
        formData.append('images_per_page', '4');

        // Get files from preview containers instead of fileInput
        const previewContainers = previewArea.querySelectorAll('.preview-container');
        const files = Array.from(previewContainers).map(container => {
            const img = container.querySelector('img');
            if (img) {
                // Convert base64 back to file
                return dataURLtoFile(img.src, 'image.jpg');
            }
            return null;
        }).filter(file => file !== null);

        files.forEach(file => {
            formData.append('files', file);
        });

        try {
            submitBtn.disabled = true;
            submitBtn.textContent = '处理中...';

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!response) {
                throw new Error('No response received from server');
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const blob = await response.blob();
            if (!blob) {
                throw new Error('No data received from server');
            }

            const url = window.URL.createObjectURL(blob);
            
            // Create modal for PDF preview
            const modal = document.createElement('div');
            modal.className = 'pdf-modal';
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h2>PDF Preview</h2>
                        <button class="close-btn">&times;</button>
                    </div>
                    <iframe src="${url}" width="100%" height="500px"></iframe>
                    <div class="modal-footer">
                        <button class="download-btn">Download PDF</button>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);

            // Handle close button
            const closeBtn = modal.querySelector('.close-btn');
            closeBtn.onclick = () => {
                modal.remove();
                window.URL.revokeObjectURL(url);
            };

            // Handle download button
            const downloadBtn = modal.querySelector('.download-btn');
            downloadBtn.onclick = () => {
                const now = new Date();
                const dateStr = now
                    .toLocaleString(undefined, { 
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: false
                    })
                    .replace(/[\s\/,:]/g, '')  // 移除所有空格、斜杠、冒号
                    .slice(2)                   // 移除前面的20
                    .replace(/(\d{6})/, '$1_'); // 在日期和时间之间加入下划线
                const filename = `expense_report_${dateStr}.pdf`;
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                modal.remove();
                window.URL.revokeObjectURL(url);
            };

            // Clear preview area
            previewArea.innerHTML = '';
            updateSubmitButton();
        } catch (error) {
            console.error('处理出错:', error);
            alert('处理过程中出现错误，请重试！');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = '处理文件';
        }
    });
    
    function updateSubmitButton() {
        submitBtn.disabled = previewArea.children.length === 0;
    }

    // Add this helper function to convert base64 to File object
    function dataURLtoFile(dataurl, filename) {
        let arr = dataurl.split(','),
            mime = arr[0].match(/:(.*?);/)[1],
            bstr = atob(arr[1]),
            n = bstr.length,
            u8arr = new Uint8Array(n);
        while(n--){
            u8arr[n] = bstr.charCodeAt(n);
        }
        return new File([u8arr], filename, {type:mime});
    }
});