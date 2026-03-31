async function processImage() {
  const fileInput = document.getElementById("fileInput");
  const file = fileInput.files[0];
  const statusEl = document.getElementById("status");

  if (!file) {
    statusEl.innerText = "Please select an image or PDF first.";
    statusEl.classList.add("visible");
    statusEl.style.color = "#dc2626"; // red-600
    return;
  }

  const loadingMessages = [
    "Uploading secure image...",
    "Scanning handwriting...",
    "Extracting clinical details...",
    "Organizing medication list..."
  ];
  let messageIndex = 0;
  
  statusEl.innerText = loadingMessages[0];
  statusEl.classList.add("visible");
  statusEl.style.color = ""; // reset color

  const messageInterval = setInterval(() => {
    messageIndex++;
    if (messageIndex >= loadingMessages.length) {
      clearInterval(messageInterval);
      return;
    }
    statusEl.innerText = loadingMessages[messageIndex];
  }, 3000);

  const formData = new FormData();
  formData.append("file", file);
  
  const languageSelect = document.getElementById("languageSelect");
  if (languageSelect) {
    formData.append("language", languageSelect.value);
  }

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || err.details || "Failed to analyze");
    }

    const data = await response.json();

    // Store in session storage to use in result.html
    clearInterval(messageInterval);
    sessionStorage.setItem("prescriptionData", JSON.stringify(data));
    window.location.href = "result.html";

  } catch (error) {
    clearInterval(messageInterval);
    console.error(error);
    statusEl.innerText = "Error: " + error.message;
    statusEl.style.color = "#dc2626";
  }
}