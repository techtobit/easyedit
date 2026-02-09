const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileUpload");
const uploadContent = document.getElementById("uploadContent");
const previewContainer = document.getElementById("previewContainer");
const previewImage = document.getElementById("previewImage");
const form = document.getElementById("uploadForm");
const canvas = document.getElementById("previewCanvas");
const ctx = canvas.getContext("2d");

let currentImage = null;   // Image object
let bgColor = null;        // Selected background color

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
  if (file) loadFile(file);
});

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (file) loadFile(file);
});



/* ------------------------------
   Working with CANVAS
--------------------------------*/

function loadFile(file) {
  if (!file.type.startsWith("image/")) return;

  // Keep input synced (for form submit)
  const dt = new DataTransfer();
  dt.items.add(file);
  fileInput.files = dt.files;

  const reader = new FileReader();
  reader.onload = () => {
    loadImageToCanvas(reader.result);
    uploadContent.classList.add("d-none");
    previewContainer.classList.remove("d-none");
  };

  reader.readAsDataURL(file);
}




function loadImageToCanvas(src) {
  const img = new Image();
  img.crossOrigin = "anonymous";
  img.src = src;

  img.onload = () => {
    currentImage = img;
    canvas.width = img.naturalWidth;
    canvas.height = img.naturalHeight;

    redrawCanvas();
    fitCanvasInContainer();
  };
}

// add canvas & image background 
function redrawCanvas() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Background
  if (bgColor) {
    ctx.fillStyle = bgColor;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }

  // Image
  if (currentImage) {
    ctx.drawImage(currentImage, 0, 0);
  }
}

// fit canvas with outer div 

function fitCanvasInContainer() {
  const wrapper = document.getElementById("previewWrapper");

  const maxW = wrapper.clientWidth;
  const maxH = window.innerHeight * 0.8;

  const scale = Math.min(
    maxW / canvas.width,
    maxH / canvas.height,
    1
  );

  canvas.style.width = canvas.width * scale + "px";
  canvas.style.height = canvas.height * scale + "px";
}

// auto resizeing based on input 

function applyOutputSize(type) {
  if (!currentImage) return;

  const size = sizeMap[type];

  if (!size) {
    canvas.width = currentImage.naturalWidth;
    canvas.height = currentImage.naturalHeight;
  } else {
    canvas.width = size.w;
    canvas.height = size.h;
  }

  redrawCanvas();
  fitCanvasInContainer();
}


/* ------------------------------
   FORM SUBMIT LOGIC
--------------------------------*/

let selectedWidth = 0;
let selectedHeight = 0;

const sizeRadios = document.querySelectorAll('input[name="default_size"]');
const customWidthInput = document.getElementById('custom_width');
const customHeightInput = document.getElementById('custom_height');


sizeRadios.forEach(radio => {
  radio.addEventListener('change', () => {
    if (!radio.checked) return;

    const label = document.querySelector(`label[for="${radio.id}"]`);

    selectedWidth = Number(label.dataset.width) || 0;
    selectedHeight = Number(label.dataset.height) || 0;

    customWidthInput.value = '';
    customHeightInput.value = '';
  });
});


/* ----------------------------
  CUSTOM INPUT HANDLING
-----------------------------*/

function handleCustomInput() {
  const inputW = Number(customWidthInput.value)
  const inputH = Number(customHeightInput.value)

  sizeRadios.forEach(radio => radio.checked = false)

  selectedWidth = inputW > 0 ? inputW : 0;
  selectedHeight = inputH > 0 ? inputH : 0;

}

customWidthInput.addEventListener('input', handleCustomInput);
customHeightInput.addEventListener('input', handleCustomInput);


/* -------- COLOR LOGIC -------- */
let bgType = "original";
let colorValue = " ";


// // Custom color picker overrides
const radioBgType = document.querySelectorAll('input[name="bg_type"]');
const colorPicker = document.getElementById('bg_color')

radioBgType.forEach(radio => {
  radio.addEventListener('change', () => {
    if (!radio.checked) return;
    bgType = document.querySelector('input[name="bg_type"]:checked').id;
    if (bgType == 'transparent') {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(currentImage, 0, 0, canvas.width, canvas.height);
    }
  })
})

colorPicker.addEventListener('input', () => {
  radioBgType.forEach(radio => radio.checked = false)
  colorValue = colorPicker.value;
  bgColor = colorPicker.value;
  redrawCanvas()

})

const LoaderAnimation = document.getElementById('magic_loader')
const getProcessBtn = document.getElementById('process_btn');
const getAfterProcessBtn = document.getElementById('success_btns');
const processText = document.getElementById('process_text');
const reload_btn = document.getElementById('reload_btn');
const error_view = document.getElementById('error_view');
let timer = null;
let renamed_image_name = '';


form.addEventListener("submit", async (e) => {
  e.preventDefault();
  LoaderAnimation.classList.remove("d-none");

  if (!fileInput.files.length) {
    alert("Please upload an image");
    return;
  }


  // ⏳ Countdown (max wait)
  let seconds = 0;
  processText.innerText = `Processing... ${seconds}s`;
  reload_btn.classList.add('d-none');
  timer = setInterval(() => {
    seconds++;
    processText.innerText = `Processing... ${seconds}s`;
    //  hide porcess btn and show success btns 
    getProcessBtn.classList.add('opacity-75');
    getAfterProcessBtn.classList.add('opacity-75');
    getProcessBtn.disabled = true;
    getAfterProcessBtn.disabled = true;
    // if (seconds >= 0) {
    //   clearInterval(timer);
    //   processText.innerText = "Still processing...";
    // }
  }, 1000);

  /* -------- FORM DATA -------- */
  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  formData.append("input_width", selectedWidth);
  formData.append("input_height", selectedHeight);
  formData.append("bgtype", bgType);

  console.log(formData)
  for (let pair of formData.entries()) {
    console.log(pair[0], pair[1]);
  }

  try {

    const res = await fetch("/upload/", {
      method: "POST",
      body: formData
    });


    if (!res.ok) {
      LoaderAnimation.classList.add("d-none");
      throw new Error(`Server error: ${res.status}`);
    }

    const result = await res.json();
    clearInterval(timer);
    processText.innerText = 'Process Image'
    LoaderAnimation.classList.add("d-none");
    if (result.image_url !=null) {
      loadImageToCanvas(result.image_url);
      renamed_image_name = result.image_name;
      getAfterProcessBtn.classList.remove('d-none')
      getProcessBtn.classList.remove('opacity-75');
      getAfterProcessBtn.classList.remove('opacity-75');
      getProcessBtn.disabled = false;
      getAfterProcessBtn.disabled = false;
    }


    console.log("Upload success:", result);

  } catch (err) {
    clearInterval(timer);
    processText.innerText = 'Process Image'
    getProcessBtn.disabled = false
    getAfterProcessBtn.classList.add('d-none')
    console.error("Upload failed:", err);
    LoaderAnimation.classList.add("d-none");
    error_view.innerText=(`${err}`)
    error_view.style.padding = '10px'
  }
});


// downlaod image 

const downloadBtn = document.getElementById('downloadBtn');
downloadBtn.addEventListener("click", () => {
  const link = document.createElement("a");
  link.download = renamed_image_name;
  link.href = canvas.toDataURL("image/png");
  link.click();
});
