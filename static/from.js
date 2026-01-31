const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileUpload");
const uploadContent = document.getElementById("uploadContent");
const previewContainer = document.getElementById("previewContainer");
const previewImage = document.getElementById("previewImage");

// Prevent default drag behavior
["dragenter", "dragover", "dragleave", "drop"].forEach(evt => {
  dropZone.addEventListener(evt, e => e.preventDefault());
});

// CLICK → open file dialog
uploadContent.addEventListener("click", e => {
  e.stopPropagation();
  fileInput.click();
});

// Drop file
dropZone.addEventListener("drop", e => {
  const file = e.dataTransfer.files[0];
  if (file) setFile(file);
});

// Manual select
fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (file) setFile(file);
});

function setFile(file) {
  if (!file.type.startsWith("image/")) return;

  // Sync dropped file with input (form-safe)
  const dt = new DataTransfer();
  dt.items.add(file);
  fileInput.files = dt.files;

  const reader = new FileReader();
  reader.onload = () => {
    previewImage.src = reader.result;

    // Hide upload prompt, show 2-column layout
    uploadContent.classList.add("d-none");
    previewContainer.classList.remove("d-none");
  };
  reader.readAsDataURL(file);
}