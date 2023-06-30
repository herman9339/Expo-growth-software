
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
function displayDownloadedImages(downloadedImages, targetDivId) {
    const container = document.getElementById(targetDivId);
    const newImageDivs = []; // Array to store the new div elements

    downloadedImages.forEach((image) => {
        const div = document.createElement('div'); // Create a new div to contain the image and the text
        const img = document.createElement('img');
        const p = document.createElement('p'); // Create a new p element for the text

        img.onload = function() {
            p.textContent = `${this.naturalWidth} x ${this.naturalHeight}`; // Set the text of the p element
        }

        img.src = image.objectURL;
        img.alt = image.filename;
        img.style.maxWidth = '100px';
        img.classList.add('image-item');

        div.appendChild(img); // Append the image to the div
        div.appendChild(p); // Append the text to the div
        container.appendChild(div); // Append the div to the container

        newImageDivs.push(div); // Add the new div element to the array
    });

    return newImageDivs; // Return the array of new div elements
}




// displayDownloadedImages ends