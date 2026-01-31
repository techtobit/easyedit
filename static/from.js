const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileUpload");
const uploadContent = document.getElementById("uploadContent");
const previewContainer = document.getElementById("previewContainer");
const previewImage = document.getElementById("previewImage");
const form = document.getElementById("uploadForm");

/* ------------------------------
   DRAG & DROP / FILE SELECT
--------------------------------*/

["dragenter", "dragover", "dragleave", "drop"].forEach(evt => {
  dropZone.addEventListener(evt, e => e.preventDefault());
});

uploadContent.addEventListener("click", e => {
  e.stopPropagation();
  fileInput.click();
});

dropZone.addEventListener("drop", e => {
  const file = e.dataTransfer.files[0];
  if (file) setFile(file);
});

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (file) setFile(file);
});

function setFile(file) {
  if (!file.type.startsWith("image/")) return;

  const dt = new DataTransfer();
  dt.items.add(file);
  fileInput.files = dt.files;

  const reader = new FileReader();
  reader.onload = () => {
    previewImage.src = reader.result;
    uploadContent.classList.add("d-none");
    previewContainer.classList.remove("d-none");
  };
  reader.readAsDataURL(file);
}

/* ------------------------------
   FORM SUBMIT LOGIC
--------------------------------*/

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  if (!fileInput.files.length) {
    alert("Please upload an image");
    return;
  }

  /* -------- SIZE LOGIC -------- */
  let width = 0;
  let height = 0;

  const selectedSize = document.querySelector('input[name="size"]:checked');

  if (selectedSize && selectedSize.value !== "0") {
    // From radio button
    const label = document.querySelector(`label[for="${selectedSize.id}"]`);
    width = label.dataset.width;
    height = label.dataset.height;
  } else {
    // Custom input
    width = document.getElementById("custom_width").value || 0;
    height = document.getElementById("custom_height").value || 0;
  }

  /* -------- COLOR LOGIC -------- */
  let colorType = "original";
  let colorValue = "";

  const selectedColor = document.querySelector('input[name="color"]:checked');

  if (selectedColor) {
    if (selectedColor.id === "color_original") {
      colorType = "original";
    } else if (selectedColor.id === "color_transparent") {
      colorType = "transparent";
    }
  }

  // Custom color picker overrides
  const colorPicker = document.getElementById("colors_custom");
  if (colorPicker && colorPicker.value) {
    colorType = "custom";
    colorValue = colorPicker.value;
  }

  /* -------- FORM DATA -------- */
  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  formData.append("input_width", width);
  formData.append("input_height", height);
  formData.append("color_type", colorType);
  formData.append("color_value", colorValue);

  // Debug (remove later)
  for (let pair of formData.entries()) {
    console.log(pair[0], pair[1]);
  }

  /* -------- SUBMIT -------- */
  try {
    const res = await fetch("http://127.0.0.1:8000/upload/", {
      method: "POST",
      body: formData
    });

    if (!res.ok) {
      throw new Error(`Server error: ${res.status}`);
    }

    const result = await res.json();

    // If backend returns processed PNG URL
    if (result.url) {
      previewImage.src = result.url;
    }

    console.log("Upload success:", result);

  } catch (err) {
    console.error("Upload failed:", err);
    alert("Upload failed. Check console & backend logs.");
  }
});
