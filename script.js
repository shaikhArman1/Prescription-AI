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

  statusEl.innerText = "Analyzing document with AI...";
  statusEl.classList.add("visible");
  statusEl.style.color = ""; // reset color

  const formData = new FormData();
  formData.append("file", file);

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
    sessionStorage.setItem("prescriptionData", JSON.stringify(data));
    window.location.href = "result.html";

  } catch (error) {
    console.error(error);
    statusEl.innerText = "Error: " + error.message;
    statusEl.style.color = "#dc2626";
  }
}