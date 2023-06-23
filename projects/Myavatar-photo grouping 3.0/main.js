document.addEventListener("DOMContentLoaded", function() {
  addImageListeners('img');
});

//Select all image in the LoadedImageSection
document.querySelector('.LoadedImageButtonSection .LoadedImageButton').addEventListener('click', function() {
  const images = document.querySelectorAll('#LoadedImagePlaceholder img');
  
  images.forEach((img) => {
    img.classList.add('selected');
  });
});





// run processTextAndDisplayImages when Process text button is clicked
document.getElementById('displayImage').addEventListener('click', processTextAndDisplayImages);

async function processTextAndDisplayImages() {
  // Get the button element
  const button = document.getElementById('displayImage');

  // Add the loading state to the button
  button.classList.add('button-loading');

  const rawImages = document.getElementById('rawImageNames').value;
  const imageUrls = extractImageLinks(rawImages);
  const downloadedImages = await downloadImagesFromLinks(imageUrls);

  const newImages = displayDownloadedImages(downloadedImages, 'LoadedImagePlaceholder');

  // Add event listeners to each new image
  newImages.forEach((img) => {
      img.addEventListener('click', (e) => {
          e.target.classList.toggle('selected');
      });

      // Create a div container for the image and the dimensions
      const imgContainer = document.createElement('div');
      imgContainer.classList.add('img-container');

      // Add the image to the container
      imgContainer.appendChild(img);

      // Create a div for the image dimensions
      const imgDimension = document.createElement('div');
      imgDimension.classList.add('img-dimension');

      // Display the image dimensions (you might want to replace this with actual dimensions)
      imgDimension.textContent = `${img.naturalWidth} x ${img.naturalHeight}`;

      // Add the dimensions to the container
      imgContainer.appendChild(imgDimension);

      // Replace the image in the DOM with the container
      img.parentNode.replaceChild(imgContainer, img);
  });

  // Remove the loading state from the button
  button.classList.remove('button-loading');
}




// Add event listener to every image
function addImageListeners(selector) {
  const images = document.querySelectorAll(selector);

  // Add click event listener for image selection/deselection
  images.forEach((img) => {
    img.addEventListener('click', (e) => {
      e.target.classList.toggle('selected');
    });
  });

  // Add keydown event listener for keys 1-9, 'a', 'd', and arrow keys
  document.addEventListener('keydown', (event) => {
    const selectedImage = document.querySelector('.selected');

    if (selectedImage) {
      handleKeyPress(event.key.toLowerCase());
    }
  });
}


function handleKeyPress(key) {
  console.log(`Key pressed: ${key}`);
  const selectedImages = document.querySelectorAll('.selected');

  if (key >= '1' && key <= '9' && key.length === 1) {

    const targetFolder = document.getElementById(`ImagePlaceholder${key}`);

    if (targetFolder) {
      selectedImages.forEach((image) => {
        targetFolder.appendChild(image);
        image.classList.remove('selected');
      });
    } else {
      console.log(`ImagePlaceholder${key} not found`);
    }
  } else if (key === 'a' || key === 'ArrowLeft') {
    selectedImages.forEach((image) => {
      const previousSibling = image.previousElementSibling;
      const prevPrevSibling = previousSibling ? previousSibling.previousElementSibling : null;
      if (previousSibling && (!previousSibling.classList.contains('selected') || !prevPrevSibling)) {
        previousSibling.parentNode.insertBefore(image, previousSibling);
      }
    });

  } else if (key === 'd' || key === 'ArrowRight') {
    const selectedImagesArray = Array.from(selectedImages);
    const reversedSelectedImages = selectedImagesArray.reverse();

    reversedSelectedImages.forEach((image) => {
      const nextSibling = image.nextElementSibling;
      const nextNextSibling = nextSibling ? nextSibling.nextElementSibling : null;
      if (nextSibling && (!nextSibling.classList.contains('selected') || !nextNextSibling)) {
        nextSibling.parentNode.insertBefore(image, nextSibling.nextElementSibling);
      }
    });

  } else if (key === 'c') {
    selectedImages.forEach((image) => {
      image.classList.remove('selected');
    });

  } else if (key === 'backspace' || key === 'q') {
    selectedImages.forEach((image) => {
      image.remove();
    });
  }
}




// Function to fetch image as ArrayBuffer
async function fetchImageAsArrayBuffer(src) {
  return new Promise((resolve) => {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', src, true);
    xhr.responseType = 'arraybuffer';
    xhr.onload = function (e) {
      if (this.status === 200) {
        resolve(this.response);
      }
    };
    xhr.send();
  });
}

document.getElementById('downloadButton').addEventListener('click', async function () {
  const zip = new JSZip();
  const imageSection = document.getElementById('imageSection');
  const folderElements = imageSection.querySelectorAll('.FolderImagePlaceholder');

  for (const folderElement of folderElements) {
    const images = folderElement.querySelectorAll('img');

    if (images.length > 0) {
      // Get the folder name from the input element
      const folderNameInput = folderElement.parentElement.querySelector('.folder-name-input');
      const folderName = folderNameInput.value || `folder ${Math.random().toString(36).substring(7)}`;

      const folder = zip.folder(folderName);

      for (let i = 0; i < images.length; i++) {
        const img = images[i];
        const imgData = await fetchImageAsArrayBuffer(img.src);
        folder.file(`${folderName}-${i + 1}.png`, imgData, { binary: true });
      }
    }
  }

  const zipBlob = await zip.generateAsync({ type: 'blob' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(zipBlob);
  link.download = 'images.zip';
  link.click();
});

  
var modal = document.getElementById("popUpWindow");
var btn = document.getElementById("InstructionPopUpButton");
var span = document.getElementsByClassName("close")[0];

btn.onclick = function() {
  modal.style.display = "block";
}

span.onclick = function() {
  modal.style.display = "none";
}

window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}



