// ============================================================
// CONFIGURATION
// ============================================================

const API_URL = "http://127.0.0.1:5000";

console.log("====================================");
console.log("PoleVision AI frontend loaded");
console.log("API URL:", API_URL);
console.log("====================================");


// ============================================================
// ELEMENTS
// ============================================================

const imageInput = document.getElementById("imageInput");
const dropZone = document.getElementById("dropZone");
const previewSection = document.getElementById("previewSection");
const previewImage = document.getElementById("previewImage");
const fileName = document.getElementById("fileName");
const removeButton = document.getElementById("removeButton");
const detectButton = document.getElementById("detectButton");

const loadingSection = document.getElementById("loadingSection");
const resultsSection = document.getElementById("resultsSection");

const newButton = document.getElementById("newButton");

const originalResult = document.getElementById("originalResult");
const resultImage = document.getElementById("resultImage");

const totalCount = document.getElementById("totalCount");
const electricCount = document.getElementById("electricCount");
const kvCount = document.getElementById("kvCount");

const detectionList = document.getElementById("detectionList");

const downloadButton = document.getElementById("downloadButton");

const errorMessage = document.getElementById("errorMessage");
const errorText = document.getElementById("errorText");


console.log("DOM elements loaded");


let selectedFile = null;
let resultImageData = null;


// ============================================================
// CHECK BACKEND
// ============================================================

async function checkBackend() {

    console.log("Checking backend...");

    try {

        const response = await fetch(
            `${API_URL}/api/health`
        );

        console.log(
            "Backend response status:",
            response.status
        );

        const data = await response.json();

        console.log(
            "Backend response:",
            data
        );

        if (data.status === "success") {

            console.log(
                "✅ Backend is connected!"
            );

        }

    } catch (error) {

        console.error(
            "❌ Backend connection failed:",
            error
        );

        console.error(
            "Make sure Flask is running on http://127.0.0.1:5000"
        );

    }
}


// Run backend check when page loads

checkBackend();


// ============================================================
// FILE INPUT
// ============================================================

imageInput.addEventListener(
    "change",
    function (event) {

        console.log("File input changed");

        const file = event.target.files[0];

        if (!file) {

            console.log("No file selected");

            return;

        }

        console.log("Selected file:", file.name);
        console.log("File type:", file.type);
        console.log("File size:", file.size);

        handleFile(file);

    }
);


// ============================================================
// HANDLE FILE
// ============================================================

function handleFile(file) {

    console.log(
        "Handling file:",
        file.name
    );


    if (!file.type.startsWith("image/")) {

        showError(
            "Please select a valid image file."
        );

        return;

    }


    selectedFile = file;


    fileName.textContent =
        file.name;


    const reader = new FileReader();


    reader.onload = function (event) {

        console.log(
            "Image preview loaded"
        );

        previewImage.src =
            event.target.result;

    };


    reader.readAsDataURL(file);


    dropZone.style.display =
        "none";

    previewSection.style.display =
        "block";


    hideError();


    console.log(
        "Preview section displayed"
    );
}


// ============================================================
// DRAG AND DROP
// ============================================================

dropZone.addEventListener(
    "dragover",
    function (event) {

        event.preventDefault();

        dropZone.classList.add(
            "dragover"
        );

    }
);


dropZone.addEventListener(
    "dragleave",
    function () {

        dropZone.classList.remove(
            "dragover"
        );

    }
);


dropZone.addEventListener(
    "drop",
    function (event) {

        event.preventDefault();

        dropZone.classList.remove(
            "dragover"
        );


        const file =
            event.dataTransfer.files[0];


        if (file) {

            console.log(
                "Dropped file:",
                file.name
            );

            handleFile(file);

        }

    }
);


// ============================================================
// REMOVE
// ============================================================

removeButton.addEventListener(
    "click",
    function () {

        console.log(
            "Remove button clicked"
        );

        resetPage();

    }
);


// ============================================================
// NEW IMAGE
// ============================================================

newButton.addEventListener(
    "click",
    function () {

        console.log(
            "New image button clicked"
        );

        resetPage();

    }
);


// ============================================================
// RESET
// ============================================================

function resetPage() {

    console.log(
        "Resetting page"
    );


    selectedFile = null;
    resultImageData = null;

    imageInput.value = "";

    previewImage.src = "";

    originalResult.src = "";

    resultImage.src = "";

    detectionList.innerHTML = "";


    previewSection.style.display =
        "none";

    resultsSection.style.display =
        "none";

    loadingSection.style.display =
        "none";

    dropZone.style.display =
        "flex";


    hideError();


    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });

}


// ============================================================
// DETECT BUTTON
// ============================================================

detectButton.addEventListener(
    "click",
    function () {

        console.log(
            "===================================="
        );

        console.log(
            "DETECT BUTTON CLICKED"
        );

        console.log(
            "===================================="
        );

        detectPoles();

    }
);


// ============================================================
// DETECT POLES
// ============================================================

async function detectPoles() {

    console.log(
        "Starting prediction..."
    );


    if (!selectedFile) {

        console.error(
            "No selected file"
        );

        showError(
            "Please select an image first."
        );

        return;

    }


    console.log(
        "File to send:",
        selectedFile.name
    );


    // --------------------------------------------------------
    // Create FormData
    // --------------------------------------------------------

    const formData = new FormData();


    formData.append(
        "image",
        selectedFile
    );


    console.log(
        "FormData created"
    );

    console.log(
        "Sending request to:",
        `${API_URL}/api/predict`
    );


    // --------------------------------------------------------
    // Show loading
    // --------------------------------------------------------

    previewSection.style.display =
        "none";

    resultsSection.style.display =
        "none";

    loadingSection.style.display =
        "block";

    hideError();


    try {

        console.log(
            "Calling fetch..."
        );


        const response = await fetch(
            `${API_URL}/api/predict`,
            {
                method: "POST",
                body: formData
            }
        );


        console.log(
            "Fetch completed"
        );


        console.log(
            "HTTP status:",
            response.status
        );


        console.log(
            "HTTP status text:",
            response.statusText
        );


        const data =
            await response.json();


        console.log(
            "Backend data:",
            data
        );


        if (!response.ok) {

            throw new Error(
                data.message ||
                `Server error: ${response.status}`
            );

        }


        if (data.status !== "success") {

            throw new Error(
                data.message ||
                "Prediction failed"
            );

        }


        console.log(
            "✅ Prediction successful"
        );


        displayResults(data);

    }
    catch (error) {

        console.error(
            "===================================="
        );

        console.error(
            "❌ PREDICTION ERROR"
        );

        console.error(
            error
        );

        console.error(
            "===================================="
        );


        loadingSection.style.display =
            "none";


        previewSection.style.display =
            "block";


        showError(
            error.message ||
            "Unable to connect to the detection server."
        );

    }

}


// ============================================================
// DISPLAY RESULTS
// ============================================================

function displayResults(data) {

    console.log(
        "Displaying results..."
    );


    loadingSection.style.display =
        "none";


    resultsSection.style.display =
        "block";


    // --------------------------------------------------------
    // Statistics
    // --------------------------------------------------------

    totalCount.textContent =
        data.total_detections;

    electricCount.textContent =
        data.electric_poles;

    kvCount.textContent =
        data.eleven_kv_poles;


    // --------------------------------------------------------
    // Original image
    // --------------------------------------------------------

    const reader =
        new FileReader();


    reader.onload =
        function (event) {

            originalResult.src =
                event.target.result;

        };


    reader.readAsDataURL(
        selectedFile
    );


    // --------------------------------------------------------
    // Result image
    // --------------------------------------------------------

    resultImage.src =
        data.result_image;


    resultImageData =
        data.result_image;


    // --------------------------------------------------------
    // Detection list
    // --------------------------------------------------------

    detectionList.innerHTML = "";


    if (
        !data.detections ||
        data.detections.length === 0
    ) {

        detectionList.innerHTML = `

            <div class="detection-item">

                <div class="detection-left">

                    <div class="detection-number">
                        !
                    </div>

                    <div>

                        <div class="detection-name">
                            No poles detected
                        </div>

                        <div class="detection-type">
                            Try another image
                        </div>

                    </div>

                </div>

            </div>

        `;

    }
    else {

        data.detections.forEach(
            function (detection, index) {

                const item =
                    document.createElement(
                        "div"
                    );


                item.className =
                    "detection-item";


                item.innerHTML = `

                    <div class="detection-left">

                        <div class="detection-number">
                            ${index + 1}
                        </div>

                        <div>

                            <div class="detection-name">
                                ${formatClassName(
                                    detection.class_name
                                )}
                            </div>

                            <div class="detection-type">
                                Detection ${index + 1}
                            </div>

                        </div>

                    </div>


                    <div class="confidence">
                        ${detection.confidence.toFixed(1)}%
                    </div>

                `;


                detectionList.appendChild(
                    item
                );

            }
        );

    }


    console.log(
        "Results displayed successfully"
    );


    resultsSection.scrollIntoView({
        behavior: "smooth"
    });

}


// ============================================================
// FORMAT CLASS NAME
// ============================================================

function formatClassName(name) {

    if (!name) {

        return "Unknown";

    }


    return name
        .replaceAll("_", " ")
        .replace(
            /\b\w/g,
            char => char.toUpperCase()
        );

}


// ============================================================
// DOWNLOAD
// ============================================================

downloadButton.addEventListener(
    "click",
    function () {

        if (!resultImageData) {

            return;

        }


        const link =
            document.createElement("a");


        link.href =
            resultImageData;


        link.download =
            "pole-detection-result.jpg";


        document.body.appendChild(
            link
        );


        link.click();


        document.body.removeChild(
            link
        );

    }
);


// ============================================================
// ERROR
// ============================================================

function showError(message) {

    console.error(
        "Showing error:",
        message
    );


    errorText.textContent =
        message;


    errorMessage.style.display =
        "block";

}


function hideError() {

    errorMessage.style.display =
        "none";

}