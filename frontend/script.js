let scanHistory = [];

document.getElementById("analyzeBtn").addEventListener("click", async function () {

  const fileInput = document.getElementById("xrayInput");
  const file = fileInput.files[0];

  if (!file) {
    alert("Please upload an X-ray image first.");
    return;
  }

  const patient = document.getElementById("patientName").value || "--";
  const age = document.getElementById("patientAge").value || "--";
  const gender = document.getElementById("patientGender").value || "--";

  const formData = new FormData();
  formData.append("xray", file);
  formData.append("patient", patient);
  formData.append("age", age);
  formData.append("gender", gender);

  try {

    const response = await fetch("http://127.0.0.1:5000/analyze", {
      method: "POST",
      body: formData
    });

    const result = await response.json();
    console.log("Backend Response:", result);

    // ❌ Handle backend error response safely
    if (result.error) {
      alert(result.error);
      return;
    }

    // =========================
    // DISEASE RESULT
    // =========================
    document.getElementById("diseaseName").innerText = result.disease || "--";

    document.getElementById("confidenceScore").innerText =
      "Confidence: " + (result.confidence || 0).toFixed(2) + "%";

    document.getElementById("progress").style.width =
      (result.confidence || 0) + "%";

    document.getElementById("reportDisease").innerText = result.disease || "--";
    document.getElementById("reportConfidence").innerText =
      (result.confidence || 0) + "%";

    document.getElementById("reportStatus").textContent =
      result.status;

    // =========================
    // EMERGENCY STATUS
    // =========================
    if (result.status === "Critical") {

  document.getElementById("emergencyStatus").innerText =
    "🚨 Critical pneumonia detected. Immediate medical attention required.";

}
else if (result.status === "High Risk") {

  document.getElementById("emergencyStatus").innerText =
    "⚠️ High risk pneumonia symptoms detected. Consult doctor immediately.";

}
else if (result.status === "Moderate Risk") {

  document.getElementById("emergencyStatus").innerText =
    "🩺 Moderate infection signs detected. Medical review recommended.";

}
else if (result.status === "Mild Risk") {

  document.getElementById("emergencyStatus").innerText =
    "ℹ️ Mild symptoms detected. Monitor health conditions.";

}
else {

  document.getElementById("emergencyStatus").innerText =
    "✅ Lungs appear normal. No emergency detected.";

}

    // =========================
    // RECOMMENDATIONS (SAFE)
    // =========================
    const recList = document.getElementById("recommendations");
    recList.innerHTML = "";

    if (result.recommendations && Array.isArray(result.recommendations)) {
      result.recommendations.forEach(rec => {
        const li = document.createElement("li");
        li.textContent = rec;
        recList.appendChild(li);
      });
    } else {
      const li = document.createElement("li");
      li.textContent = "No recommendations available.";
      recList.appendChild(li);
    }

    // =========================
    // REPORT TEXT
    // =========================
    document.getElementById("reportRecommendations").innerText =
      (result.recommendations || []).join(", ");

    // =========================
    // ANALYTICS (SAFE)
    // =========================
    // =========================
// ANALYTICS (UPDATED)
// =========================
if (result.analytics) {

  console.log("Analytics Data:", result.analytics);

  document.getElementById("totalScans").innerText =
    result.analytics.total_scans ?? 0;

  document.getElementById("criticalCases").innerText =
    result.analytics.critical_cases ?? 0;

  document.getElementById("aiAccuracy").innerText =
    (result.analytics.accuracy ?? 0) + "%";

}
    // =========================
    // SCAN HISTORY
    // =========================
    scanHistory.push({
      file: file.name,
      patient: patient,
      age: age,
      gender: gender,
      disease: result.disease || "--",
      confidence: result.confidence || 0,
      status: result.status || "--"
    });

    updateScanHistory();

  } catch (error) {
    console.error(error);
    alert("Error analyzing image. Check backend connection.");
  }
});


// =========================
// UPDATE HISTORY TABLE
// =========================
function updateScanHistory() {
  const list = document.getElementById("scanHistoryList");
  list.innerHTML = "";

  if (scanHistory.length === 0) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 8;
    cell.textContent = "No scans yet.";
    row.appendChild(cell);
    list.appendChild(row);
    return;
  }

  scanHistory.forEach((scan, index) => {
    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${index + 1}</td>
      <td>${scan.file}</td>
      <td>${scan.patient}</td>
      <td>${scan.age}</td>
      <td>${scan.gender}</td>
      <td>${scan.disease}</td>
      <td>${scan.confidence}%</td>
      <td>${scan.status}</td>
    `;

    list.appendChild(row);
  });
}


// =========================
// SAVE BUTTON
// =========================
document.getElementById("saveBtn").addEventListener("click", function () {

  const name = document.getElementById("patientName").value || "--";
  const age = document.getElementById("patientAge").value || "--";
  const gender = document.getElementById("patientGender").value || "--";

  document.getElementById("reportPatient").innerText = name;
  document.getElementById("reportAge").innerText = age;
  document.getElementById("reportGender").innerText = gender;

  alert(`Patient Saved:\nName: ${name}\nAge: ${age}\nGender: ${gender}`);
});


// =========================
// DOWNLOAD REPORT
// =========================
document.querySelector(".download-btn").addEventListener("click", function () {
  window.open("http://127.0.0.1:5000/download_report", "_blank");
});