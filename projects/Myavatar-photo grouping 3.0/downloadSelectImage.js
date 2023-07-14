/* Download Functions */
async function downloadImagesAsZip() {
    const zip = new JSZip(), 
        imgSections = document.getElementById('imageSection').querySelectorAll('.FolderImagePlaceholder');

    for (const section of imgSections) {
        const images = section.querySelectorAll('img');
        if (images.length > 0) {
            const folderName = getFolderName(section), 
                folder = zip.folder(folderName);

            for (let i = 0; i < images.length; i++) {
                const imageData = await fetchImageAsArrayBuffer(images[i].src);
                folder.file(`${folderName}-${i + 1}.png`, imageData, { binary: true });
            }
        }
    }
    const zipBlob = await zip.generateAsync({ type: 'blob' });
    downloadBlobAsZip(zipBlob);
}

function getFolderName(section) {
    const folderNameInput = section.parentElement.querySelector('.folder-name-input');
    return folderNameInput.value || `folder_${Math.random().toString(36).substring(7)}`;
}

async function fetchImageAsArrayBuffer(src) {
    const response = await fetch(src);
    const buffer = await response.arrayBuffer();
    return buffer;
}

function downloadBlobAsZip(zipBlob) {
    const link = document.createElement('a');
    link.href = URL.createObjectURL(zipBlob);
    link.download = 'images.zip';
    link.click();
}


