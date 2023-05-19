
// This function takes raw image names (in a single string) and a base URL,
// removes the "Image" prefix from each image name,
// and returns an array of full image URLs.
const baseUrl = 'https://cdn.customily.com/product-images/';
function extractImageLinks(rawImageNames) {
    const imageNames = rawImageNames.split('\t').map((imageName) => imageName.replace(/^Image/, ''));
    return imageNames.map((imageName) => `${baseUrl}${imageName}`);
}
// extractImageLinks snippet ends

// This function takes an array of image URLs,
// downloads each image, and returns an array of downloaded image objects,
// each with a filename and object URL.
async function downloadImagesFromLinks(imageUrls) {
    const downloadedImages = [];

    for (let i = 0; i < imageUrls.length; i++) {
        const imageUrl = imageUrls[i];
        const filename = `image-${i}.png`;

        try {
            const response = await fetch(imageUrl);
            const blob = await response.blob();
            const objectURL = URL.createObjectURL(blob);
            downloadedImages.push({ filename: filename, objectURL: objectURL });
        } catch (error) {
            console.error('Error downloading image:', error);
        }
    }

    return downloadedImages;
}

// downloadImagesFromLinks ends



// This function takes an array of downloaded image objects and a target div element,
// creates a new DOM element for each image,
// and appends the image elements to the target div inside the <main> element.
function displayDownloadedImages(downloadedImages, targetDivId, callback) {
    const container = document.getElementById(targetDivId);
    const newImages = []; // Array to store the new image elements

    downloadedImages.forEach((image) => {
        const img = document.createElement('img');
        img.src = image.objectURL;
        img.alt = image.filename;
        img.style.maxWidth = '100px';
        img.classList.add('image-item');
        container.appendChild(img);

        newImages.push(img); // Add the new img element to the array
    });

    return newImages; // Return the array of new image elements
}


// displayDownloadedImages ends
