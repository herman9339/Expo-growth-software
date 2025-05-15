
// Helper function to retrieve image dimensions from an element
function getImageDimensionsFromElement(element) {
    const infoTextDiv2 = element.querySelector('.infoTextDiv2');
    return infoTextDiv2.textContent;
}

// Helper function to get unique values from an array
function getUniqueValues(array) {
    return [...new Set(array)];
}

// Function to get a distinct color based on index
// Function to get a color from a preset list based on index
function getColorFromPreset(index) {
    const colorPalette = [
        '#F44336', // Red
        '#FFEB3B', // Yellow
        '#4CAF50', // Green
        '#009688', // Teal
        '#00BCD4', // Cyan
        '#2196F3', // Blue
        '#673AB7', // Deep Purple
        '#9C27B0', // Purple
        '#E91E63', // Pink
        '#795548', // Brown
    ];

    return colorPalette[index % colorPalette.length];
}




// Function to analyze image dimensions and change color accordingly
function checkImageDimensions(target) {
    const images = Array.from(target.children);
    const dimensions = images.map(getImageDimensionsFromElement);
    const uniqueDimensions = getUniqueValues(dimensions);

    const dimensionColorMap = new Map();
    uniqueDimensions.forEach((dimension, index) => {
        const color = getColorFromPreset(index);
        dimensionColorMap.set(dimension, color);
    });

    images.forEach((img, index) => {
        const dimension = dimensions[index];
        const toggleControlDiv = img.querySelector('.toggleControlDiv');
        
        // Check if there is more than one unique dimension
        if (uniqueDimensions.length > 1) {
            const color = dimensionColorMap.get(dimension);
            toggleControlDiv.style.backgroundColor = color;
            toggleControlDiv.style.display = 'flex';  // Make it visible
        } else {
            toggleControlDiv.style.display = 'none';  // Hide it
        }
    });
}


// Function to move images to placeholder
function moveImagesToPlaceholder(target, images) {
    images.forEach(img => {
        if (!img.contains(target)) {
            target.appendChild(img);
            img.classList.remove('selected');
            console.log(`Moved image to ImagePlaceholder${target.id}`);
        } else {
            console.error('Cannot move an image into its own child element.');
        }
    });

    checkImageDimensions(target);
}

// Function to move selected images to folder
function moveSelectedImagesToFolder(key, selectedImages) {
    const target = document.getElementById(`ImagePlaceholder${key}`);
    if (!target) {
        console.log(`ImagePlaceholder${key} not found`);
    } else {
        moveImagesToPlaceholder(target, selectedImages);
    }
}


function handleNavigationAndActionKeys(key, images) {
    if (key === 'a' || key === 'ArrowLeft' || key === 'd' || key === 'ArrowRight') {
        moveImage(images, key === 'a' || key === 'ArrowLeft');
    } else if (key === 'c') {
        deselectImages(images);
    } else if (key === 'backspace' || key === 'q') {
        removeImages(images);
    }
}

function moveImage(images, isLeft) {
    const orderedImages = isLeft ? Array.from(images) : Array.from(images).reverse();
    orderedImages.forEach(img => {
        const sibling = isLeft ? img.previousElementSibling : img.nextElementSibling;
        if (sibling && !sibling.classList.contains('selected')) {
            sibling.parentNode.insertBefore(img, isLeft ? sibling : sibling?.nextElementSibling);
            console.log(`Moved image ${isLeft ? 'left' : 'right'}`);
        }
    });
}


function deselectImages(images) {
    images.forEach(img => {
        img.classList.remove('selected');
        console.log('Deselected an image');
    });
}

function removeImages(images) {
    images.forEach(img => {
        img.remove();
        console.log('Removed an image');
    });
}

