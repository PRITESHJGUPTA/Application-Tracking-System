const loadBtn = document.getElementById("loadBtn");
const tableBody = document.querySelector("#candidatesTable tbody");

loadBtn.addEventListener("click", async () => {
  const skill = document.getElementById("filterSkill").value;
  const qualification = document.getElementById("filterQualification").value;
  const minExperience = document.getElementById("filterExperience").value;
  const aptitude = document.getElementById("filterAptitude").value;
  const interview1 = document.getElementById("filterInterview1").value;
  const interview2 = document.getElementById("filterInterview2").value;

  let queryParams = [];
  if (skill) queryParams.push(`skill=${encodeURIComponent(skill)}`);
  if (qualification) queryParams.push(`qualification=${encodeURIComponent(qualification)}`);
  if (minExperience) queryParams.push(`min_experience=${minExperience}`);
  if (aptitude) queryParams.push(`aptitude_status=${encodeURIComponent(aptitude)}`);
  if (interview1) queryParams.push(`interview_round_1=${encodeURIComponent(interview1)}`);
  if (interview2) queryParams.push(`interview_round_2=${encodeURIComponent(interview2)}`);

  const url = `/candidates${queryParams.length ? "?" + queryParams.join("&") : ""}`;

  try {
    const res = await fetch(url);
    const candidates = await res.json();

    tableBody.innerHTML = ""; // Clear old rows

    if (candidates.length === 0) {
      const row = tableBody.insertRow();
      row.innerHTML = `<td colspan="9">No candidates found.</td>`;
      return;
    }

    candidates.forEach((c) => {
      const row = tableBody.insertRow();
      row.innerHTML = `
        <td>${c.name}</td>
        <td>${c.qualification}</td>
        <td>${c.gender}</td>
        <td>${c.skills.join(", ")}</td>
        <td>${c.experience.length}</td>
        <td>
          <select class="status-dropdown" data-id="${c.id}" data-field="aptitude_status">
            ${["Not Started", "Performing Test", "Cleared", "Not Cleared"].map(status =>
              `<option value="${status}" ${c.aptitude_status === status ? "selected" : ""}>${status}</option>`
            ).join("")}
          </select>
        </td>
        <td>
          <select class="status-dropdown" data-id="${c.id}" data-field="interview_round_1">
            ${["Not Started", "Undergoing", "Cleared", "Not Cleared"].map(status =>
              `<option value="${status}" ${c.interview_round_1 === status ? "selected" : ""}>${status}</option>`
            ).join("")}
          </select>
        </td>
        <td>
          <select class="status-dropdown" data-id="${c.id}" data-field="interview_round_2">
            ${["Not Started", "Undergoing", "Cleared", "Not Cleared"].map(status =>
              `<option value="${status}" ${c.interview_round_2 === status ? "selected" : ""}>${status}</option>`
            ).join("")}
          </select>
        </td>
        <td>
          <input type="checkbox" class="select-toggle" data-id="${c.id}" ${c.is_selected ? "checked" : ""} />
        </td>
      `;
    });

    // Handle dropdown changes
    document.querySelectorAll(".status-dropdown").forEach((dropdown) => {
      dropdown.addEventListener("change", async (e) => {
        const id = e.target.dataset.id;
        const field = e.target.dataset.field;
        const value = e.target.value;

        await fetch(`/candidates/${id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ [field]: value })
        });
      });
    });

    // Handle "selected" checkbox changes
    document.querySelectorAll(".select-toggle").forEach((checkbox) => {
      checkbox.addEventListener("change", async (e) => {
        const id = e.target.dataset.id;
        const isSelected = e.target.checked;

        await fetch(`/candidates/${id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ is_selected: isSelected })
        });
      });
    });

  } catch (err) {
    console.error("Failed to load candidates", err);
    alert("Error loading candidates.");
  }
});
const csvForm = document.getElementById("csvUploadForm");
const csvFile = document.getElementById("csvFile");
const csvStatus = document.getElementById("csvStatus");

csvForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  if (!csvFile.files.length) {
    csvStatus.textContent = "❌ Please choose a CSV file.";
    return;
  }

  const formData = new FormData();
  formData.append("file", csvFile.files[0]);

  try {
    csvStatus.textContent = "Uploading...";
    const res = await fetch("/upload-aptitude-results", {
      method: "POST",
      body: formData
    });

    const result = await res.json();
    if (!res.ok) throw new Error(result.detail || "Upload failed");

    csvStatus.textContent = `✅ ${result.updated} candidates updated successfully.`;
    csvFile.value = ""; // Clear input
  } catch (err) {
    csvStatus.textContent = `❌ Error: ${err.message}`;
  }
});

window.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("toggleSubmission");

  fetch("/submission-status")
    .then(res => res.json())
    .then(data => {
      toggle.checked = data.enabled;
    });

  toggle.addEventListener("change", () => {
    fetch("/toggle-submission", { method: "POST" })
      .then(res => res.json())
      .then(data => {
        alert(`Student submission is now ${data.enabled ? "ENABLED ✅" : "DISABLED 🚫"}`);
      });
  });
});
