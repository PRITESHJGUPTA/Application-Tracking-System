const uploadForm = document.getElementById("uploadForm");
const uploadStatus = document.getElementById("uploadStatus");

uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData();

  // Gather input values
  const name = document.getElementById("name").value;
  const email = document.getElementById("email").value;
  const phone = document.getElementById("phone").value;
  const qualification = document.getElementById("qualification").value;
  const gender = document.getElementById("gender").value;
  const state = document.getElementById("state").value;
  const city = document.getElementById("city").value;
  const employee = document.getElementById("employee").checked;
  const resume = document.getElementById("resumeFile").files[0];

  if (!resume) {
    uploadStatus.textContent = "❌ Please select a resume file.";
    return;
  }

  // Append form fields
  formData.append("file", resume);
  formData.append("name", name);
  formData.append("email", email);
  formData.append("phone", phone);
  formData.append("qualification", qualification);
  formData.append("gender", gender);
  formData.append("location_state", state);
  formData.append("location_city", city);
  formData.append("kanaka_employee", employee);

  try {
    uploadStatus.textContent = "Submitting application...";

    const response = await fetch("/upload_resume", {
      method: "POST",
      body: formData,
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.detail || "Upload failed");
    }

    uploadStatus.textContent = `✅ Application submitted for ${result.name}`;
    uploadForm.reset();
  } catch (error) {
    uploadStatus.textContent = `❌ Error: ${error.message}`;
  }
});
