/* Event Handlers Initialization */
document.addEventListener('DOMContentLoaded', initializeEventListeners);
document.addEventListener('keydown', handleKeyPress);
window.addEventListener('click', closePopUpWindowIfClickedOutside);

document.getElementById('displayImage').addEventListener('click', processAndDisplayImages);
document.getElementById("InstructionPopUpButton").addEventListener('click', displayPopUpWindow);
document.getElementById('downloadButton').addEventListener('click', downloadImagesAsZip);

function initializeEventListeners() {
    addImageListeners();
    addToggleControlListeners();
    addCloseButtonListeners();
}

/* Toggle Functions */
function addToggleControlListeners() {
    document.querySelectorAll('.toggleControlDiv')
        .forEach(div => div.addEventListener('click', toggleControlExpansion));
}

function toggleControlExpansion(e) {
    e.currentTarget.classList.toggle('expanded');
}

/* Key Press Function */
function handleKeyPress(e) {
    const selected = document.querySelectorAll('.selected'),
        key = e.key;
    
    if (key >= '1' && key <= '9') {
        moveSelectedImagesToFolder(key, selected);
    } else {
        handleNavigationAndActionKeys(key, selected);
    }
}

/* Image Selection Functions */
function addImageListeners() {
    document.querySelectorAll('.imageControlContainer')
        .forEach(container => container.addEventListener('click', toggleImageSelection));
}

function toggleImageSelection(e) {
    e.currentTarget.classList.toggle('selected');
}

/* Select All Images in the LoadedImagePlaceholder Functions */
function selectAllImages() {
  document.querySelectorAll('#LoadedImagePlaceholder .imageControlContainer')
      .forEach(container => container.classList.add('selected'));
}


/* Pop-up Functions */
function addCloseButtonListeners() {
    document.querySelectorAll('.LoadedImageButtonSection .LoadedImageButton, .close')
        .forEach(btn => btn.addEventListener('click', btn.className.includes('close') ? closePopUpWindow : selectAllImages));
}

function displayPopUpWindow() {
    document.getElementById("popUpWindow").style.display = "block";
}

function closePopUpWindow() {
    document.getElementById("popUpWindow").style.display = "none";
}

function closePopUpWindowIfClickedOutside(e) {
    if (e.target == document.getElementById("popUpWindow")) closePopUpWindow();
}

/* Image Processing Functions */
function processAndDisplayImages() {
  const baseUrl = 'https://cdn.customily.com/product-images/',
      imageNames = document.getElementById('rawImageNames').value.split('\t').map(name => name.replace(/^Image/, ''));

  imageNames.forEach((name, i) => fetch(`${baseUrl}${name}`)
      .then(response => response.blob())
      .then(blob => {
          const img = createImageElement(blob, i);
          const clone = prepareImageTemplate(img);
          addImageDimensionsToClone(clone, img.src, 'LoadedImagePlaceholder');
      })
      .catch(e => console.error('Error downloading image:', e)));
}

function createImageElement(blob, index) {
  const img = document.createElement('img');
  const imageUrl = URL.createObjectURL(blob);
  img.src = imageUrl;
  img.alt = `image-${index}.png`;
  img.style.maxWidth = '80px';
  img.classList.add('image-item');
  return img;
}

function prepareImageTemplate(img) {
  const template = document.getElementById('imageControlTemplate');
  const clone = document.importNode(template.content, true);

  const infoTextDiv1 = clone.querySelector('.infoTextDiv1');
  // Replacing the text in infoTextDiv1 with the anchor element
  infoTextDiv1.innerHTML = '';
  infoTextDiv1.appendChild(createAnchorElement(img.src));

  clone.querySelector('.imageContainerDiv').appendChild(img);

  // Find imageControlContainer and toggleControlDiv inside the clone and add event listeners to them
  const imageControlContainer = clone.querySelector('.imageControlContainer');
  const toggleControlDiv = clone.querySelector('.toggleControlDiv');
  
  imageControlContainer.addEventListener('click', toggleImageSelection);
  toggleControlDiv.addEventListener('click', toggleControlExpansion);
  
  return clone;
}


function createAnchorElement(imageUrl) {
  // Creating a new anchor element
  const anchor = document.createElement('a');
  anchor.href = imageUrl;
  anchor.target = "_blank"; // Opens the link in a new tab
  anchor.textContent = "Preview";
  return anchor;
}

// Function to add image dimensions to a clone and append it to the specified parent element
function addImageDimensionsToClone(clone, imageUrl, parentElementId) {
  if (!clone || !imageUrl || !parentElementId) {
      console.error('Both clone, imageUrl, and parentElementId must be provided');
      return;
  }

  const tempImg = new Image();
  tempImg.src = imageUrl;

  tempImg.onload = function() {
      const infoTextDiv2 = clone.querySelector('.infoTextDiv2');

      if (!infoTextDiv2) {
          console.error('Element with class "infoTextDiv2" not found in clone');
          return;
      }

      infoTextDiv2.textContent = `${this.width}x${this.height}`;

      // Get the toggleControlDiv and make it invisible
      const toggleControlDiv = clone.querySelector('.toggleControlDiv');
      toggleControlDiv.style.display = 'none';

      // Append the clone after the image has loaded and we have the dimensions
      const parentElement = document.getElementById(parentElementId);
      if (!parentElement) {
          console.error('Parent element not found: ', parentElementId);
          return;
      }

      parentElement.appendChild(clone);
  };

  tempImg.onerror = function() {
      console.error('Failed to load image at url: ', imageUrl);
  };
}



