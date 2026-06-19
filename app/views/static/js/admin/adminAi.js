// adminAi.js
// Quan ly trang thai, test va retrain AI Model qua /admin/api/ai.

function initAiModule() {
  const btnTestAI = document.getElementById("btnTestAI");
  const btnRetrainAI = document.getElementById("btnRetrainAI");

  if (btnTestAI) {
    btnTestAI.addEventListener("click", testAiClassification);
  }

  if (btnRetrainAI) {
    btnRetrainAI.addEventListener("click", retrainAiModel);
  }

  loadAiStatus();
}

async function loadAiStatus() {
  try {
    const result = await fetchAdminAiApi("/admin/api/ai/status");
    if (!result) return;

    if (!result.success) {
      showHtmlModal("Lỗi", `<p class="mb-0">${escapeAiHtml(result.message || "Không lấy được trạng thái AI")}</p>`);
      return;
    }

    renderAiStatus(result.data);
  } catch (error) {
    showHtmlModal("Lỗi", `<p class="mb-0">${escapeAiHtml(error.message || "Không lấy được trạng thái AI")}</p>`);
  }
}

async function testAiClassification() {
  const aiTestInput = document.getElementById("aiTestInput");
  const btnTestAI = document.getElementById("btnTestAI");
  const text = aiTestInput?.value.trim() || "";

  if (!text) {
    showHtmlModal("Thiếu dữ liệu", "<p class=\"mb-0\">Vui lòng nhập nội dung giao dịch mẫu.</p>");
    return;
  }

  setAiButtonLoading(btnTestAI, true, "Đang xử lý...");

  try {
    const result = await fetchAdminAiApi("/admin/api/ai/test", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    if (!result) return;

    if (!result.success) {
      showHtmlModal("Lỗi", `<p class="mb-0">${escapeAiHtml(result.message || "Không phân loại được giao dịch")}</p>`);
      return;
    }

    renderAiTestResult(result.data);
  } catch (error) {
    showHtmlModal("Lỗi", `<p class="mb-0">${escapeAiHtml(error.message || "Không phân loại được giao dịch")}</p>`);
  } finally {
    setAiButtonLoading(btnTestAI, false, "Phân loại ngay");
  }
}

async function retrainAiModel() {
  const btnRetrainAI = document.getElementById("btnRetrainAI");
  const retrainProgressBox = document.getElementById("retrainProgressBox");
  const retrainProgressBar = document.getElementById("retrainProgressBar");
  const retrainStatusText = document.getElementById("retrainStatusText");
  const retrainPercentText = document.getElementById("retrainPercentText");

  setAiButtonLoading(btnRetrainAI, true, "Đang xử lý...");
  if (retrainProgressBox) retrainProgressBox.classList.remove("d-none");
  if (retrainProgressBar) retrainProgressBar.style.width = "60%";
  if (retrainPercentText) retrainPercentText.innerText = "60%";
  if (retrainStatusText) retrainStatusText.innerText = "Đang xử lý dữ liệu huấn luyện...";

  try {
    const result = await fetchAdminAiApi("/admin/api/ai/retrain", {
      method: "POST",
    });
    if (!result) return;

    if (!result.success) {
      showHtmlModal("Lỗi", `<p class="mb-0">${escapeAiHtml(result.message || "Không huấn luyện lại được AI Model")}</p>`);
      return;
    }

    if (retrainProgressBar) retrainProgressBar.style.width = "100%";
    if (retrainPercentText) retrainPercentText.innerText = "100%";
    if (retrainStatusText) retrainStatusText.innerText = "Hoàn tất huấn luyện AI Model.";

    renderAiStatus(result.data);
    showToast("success", "Huấn luyện thành công", result.message || "AI Model đã được cập nhật.");
  } catch (error) {
    showHtmlModal("Lỗi", `<p class="mb-0">${escapeAiHtml(error.message || "Không huấn luyện lại được AI Model")}</p>`);
  } finally {
    setAiButtonLoading(btnRetrainAI, false, '<i class="bi bi-arrow-repeat me-2"></i>Huấn luyện lại AI Model');
    setTimeout(() => {
      if (retrainProgressBox) retrainProgressBox.classList.add("d-none");
      if (retrainProgressBar) retrainProgressBar.style.width = "0%";
      if (retrainPercentText) retrainPercentText.innerText = "0%";
    }, 600);
  }
}

function renderAiStatus(data) {
  setAiText("aiAccuracyText", formatAiPercent(data?.accuracy));
  setAiText("aiActiveModel", data?.modelName || "-");
  setAiText("aiTotalTrained", `${Number(data?.totalTrainingSamples || 0).toLocaleString("vi-VN")} mẫu`);
  setAiText("aiLastTrained", formatAiDate(data?.lastTrainedAt));
}

function renderAiTestResult(data) {
  const aiTestResultBox = document.getElementById("aiTestResultBox");
  const aiResultCategory = document.getElementById("aiResultCategory");
  const aiResultConfidence = document.getElementById("aiResultConfidence");
  const aiResultType = document.getElementById("aiResultType");

  if (aiResultCategory) aiResultCategory.innerText = data?.categoryName || "-";
  if (aiResultConfidence) aiResultConfidence.innerText = formatAiPercent(data?.confidence);

  if (aiResultType) {
    const type = data?.type || "-";
    aiResultType.innerText = type;
    aiResultType.className = type === "THU" ? "badge bg-success" : "badge bg-danger";
  }

  if (aiTestResultBox) aiTestResultBox.classList.remove("d-none");
}

async function fetchAdminAiApi(url, options = {}) {
  const token = localStorage.getItem("adminAccessToken");
  const headers = options.headers || {};

  const response = await fetch(url, {
    ...options,
    headers: {
      ...headers,
      Authorization: "Bearer " + token,
    },
  });
  const result = await response.json();

  if (response.status === 401) {
    localStorage.removeItem("adminAccessToken");
    localStorage.removeItem("adminInfo");
    window.location.href = "/admin/login";
    return null;
  }

  return result;
}

function setAiButtonLoading(button, isLoading, content) {
  if (!button) return;

  button.disabled = isLoading;
  button.innerHTML = isLoading
    ? '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Đang xử lý...'
    : content;
}

function setAiText(id, value) {
  const element = document.getElementById(id);
  if (element) element.innerText = value;
}

function formatAiPercent(value) {
  const numberValue = Number(value || 0);
  return `${numberValue.toLocaleString("vi-VN", { maximumFractionDigits: 1 })}%`;
}

function formatAiDate(value) {
  if (!value) return "-";

  const date = new Date(String(value).replace(" ", "T"));
  if (Number.isNaN(date.getTime())) return value;

  return date.toLocaleDateString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

function escapeAiHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
