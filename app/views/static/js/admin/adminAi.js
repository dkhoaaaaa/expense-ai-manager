// adminAi.js
// Quản lý trạng thái, kiểm thử và huấn luyện lại mô hình AI trên Admin Dashboard

let aiPerformanceChartInstance = null;

function initAiModule() {
  const btnPlaygroundAnalyze = document.getElementById("btnPlaygroundAnalyze");
  const btnPlaygroundRetrain = document.getElementById("btnPlaygroundRetrain");

  if (btnPlaygroundAnalyze) {
    btnPlaygroundAnalyze.addEventListener("click", analyzePlaygroundTransaction);
  }

  if (btnPlaygroundRetrain) {
    btnPlaygroundRetrain.addEventListener("click", retrainPlaygroundModel);
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

async function analyzePlaygroundTransaction() {
  const aiPlaygroundInput = document.getElementById("aiPlaygroundInput");
  const btnPlaygroundAnalyze = document.getElementById("btnPlaygroundAnalyze");
  const text = aiPlaygroundInput?.value.trim() || "";

  if (!text) {
    showHtmlModal("Thiếu dữ liệu", "<p class=\"mb-0\">Vui lòng nhập nội dung giao dịch mẫu để phân tích.</p>");
    return;
  }

  setAiButtonLoading(btnPlaygroundAnalyze, true, "Đang phân tích...");

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

    renderPlaygroundResult(result.data);
  } catch (error) {
    showHtmlModal("Lỗi", `<p class="mb-0">${escapeAiHtml(error.message || "Không phân loại được giao dịch")}</p>`);
  } finally {
    setAiButtonLoading(btnPlaygroundAnalyze, false, '<i class="bi bi-cpu me-2"></i>Phân tích giao dịch');
  }
}

async function retrainPlaygroundModel() {
  const btnPlaygroundRetrain = document.getElementById("btnPlaygroundRetrain");
  const progressBox = document.getElementById("playgroundRetrainProgressBox");
  const progressBar = document.getElementById("playgroundRetrainProgressBar");
  const statusText = document.getElementById("playgroundRetrainStatusText");
  const percentText = document.getElementById("playgroundRetrainPercentText");

  setAiButtonLoading(btnPlaygroundRetrain, true, "Đang huấn luyện...");
  if (progressBox) progressBox.classList.remove("d-none");
  
  // Mô phỏng tiến trình chuẩn bị dữ liệu
  updateProgress(20, "Đang trích xuất dữ liệu mẫu từ cơ sở dữ liệu...");
  
  setTimeout(() => {
    updateProgress(50, "Đang xử lý chuẩn hóa và tách từ văn bản...");
  }, 400);

  function updateProgress(percent, status) {
    if (progressBar) progressBar.style.width = `${percent}%`;
    if (percentText) percentText.innerText = `${percent}%`;
    if (statusText) statusText.innerText = status;
  }

  try {
    const result = await fetchAdminAiApi("/admin/api/ai/retrain", {
      method: "POST",
    });
    if (!result) return;

    if (!result.success) {
      showHtmlModal("Lỗi", `<p class="mb-0">${escapeAiHtml(result.message || "Không huấn luyện lại được AI Model")}</p>`);
      return;
    }

    updateProgress(90, "Đang tối ưu hóa mô hình Logistic Regression...");
    
    setTimeout(() => {
      updateProgress(100, "Hoàn tất huấn luyện AI Model thực tế!");
      renderAiStatus(result.data);
      showToast("success", "Huấn luyện thành công", result.message || "Mô hình AI mới đã được cập nhật vào hệ thống.");
      
      setTimeout(() => {
        if (progressBox) progressBox.classList.add("d-none");
        updateProgress(0, "");
      }, 1000);
    }, 500);

  } catch (error) {
    showHtmlModal("Lỗi", `<p class="mb-0">${escapeAiHtml(error.message || "Không huấn luyện lại được AI Model")}</p>`);
    if (progressBox) progressBox.classList.add("d-none");
  } finally {
    setAiButtonLoading(btnPlaygroundRetrain, false, '<i class="bi bi-arrow-repeat me-2"></i>Huấn luyện lại Model');
  }
}

function renderAiStatus(data) {
  // Hàng 1 - AI Overview Cards
  setAiText("aiEngineText", data?.modelName || "Rule-based Keyword Classifier");
  setAiText("aiAccuracyOverviewText", formatAiPercent(data?.accuracy));
  setAiText("aiAccuracyTrendText", data?.accuracyTrend || "+2.3% tháng này");
  setAiText("aiTransactionsClassifiedText", Number(data?.transactionsClassified || 0).toLocaleString("vi-VN"));
  setAiText("aiRequestsText", Number(data?.aiRequests || 0).toLocaleString("vi-VN"));

  // Hàng 2 - Health Check & Performance Chart
  setAiText("aiHealthTrainingData", `${Number(data?.modelHealth?.trainingData || 0).toLocaleString("vi-VN")} mẫu`);
  setAiText("aiHealthLastTraining", data?.modelHealth?.lastTraining || "-");
  setAiText("aiHealthVersion", data?.modelHealth?.version || "v1.0");
  
  const statusEl = document.getElementById("aiHealthStatus");
  if (statusEl) {
    statusEl.innerText = data?.modelHealth?.status || "Online";
    statusEl.className = `badge bg-success-soft text-success px-2 py-1`;
  }

  if (data?.accuracyHistory) {
    renderAiPerformanceChart(data.accuracyHistory);
  }

  // Hàng 4 - Dataset Statistics & Top Keywords
  renderDatasetStatsTable(data?.datasetStats);
  renderTopKeywords(data?.topKeywords);

  // Hàng 5 - Training Management Meta info
  setAiText("aiLastTrainMeta", data?.modelHealth?.lastTraining || "-");
  setAiText("aiLastTrainSamples", `${Number(data?.modelHealth?.trainingData || 0).toLocaleString("vi-VN")} mẫu`);
}

function renderPlaygroundResult(data) {
  const emptyBox = document.getElementById("aiPlaygroundResultEmpty");
  const contentBox = document.getElementById("aiPlaygroundResultContent");
  const categoryEl = document.getElementById("aiPlaygroundCategory");
  const confidenceEl = document.getElementById("aiPlaygroundConfidence");
  const keywordsEl = document.getElementById("aiPlaygroundKeywords");

  if (emptyBox) emptyBox.classList.add("d-none");
  if (contentBox) contentBox.classList.remove("d-none");

  if (categoryEl) categoryEl.innerText = data?.categoryName || "-";
  if (confidenceEl) confidenceEl.innerText = formatAiPercent(data?.confidence);

  if (keywordsEl) {
    keywordsEl.innerHTML = "";
    const kws = data?.matchedKeywords || [];
    if (kws.length === 0) {
      keywordsEl.innerHTML = '<span class="text-muted small italic">Không có từ khóa nhận diện</span>';
    } else {
      kws.forEach(kw => {
        const badge = document.createElement("span");
        badge.className = "badge bg-info-soft text-info me-1 mb-1";
        badge.style.fontSize = "0.75rem";
        badge.style.fontWeight = "normal";
        badge.innerText = kw;
        keywordsEl.appendChild(badge);
      });
    }
  }
}

function renderDatasetStatsTable(stats) {
  const tableBody = document.getElementById("aiDatasetStatsTable");
  if (!tableBody) return;

  tableBody.innerHTML = "";
  const statsList = stats || [];

  if (statsList.length === 0) {
    tableBody.innerHTML = '<tr><td colspan="2" class="text-center text-muted py-3">Không có dữ liệu mẫu huấn luyện nào.</td></tr>';
    return;
  }

  statsList.forEach(item => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td class="fw-medium">${escapeAiHtml(item.category)}</td>
      <td><span class="badge bg-secondary-soft text-light px-2 py-1">${Number(item.count).toLocaleString("vi-VN")} mẫu</span></td>
    `;
    tableBody.appendChild(row);
  });
}

function renderTopKeywords(keywords) {
  const container = document.getElementById("aiTopKeywordsContainer");
  if (!container) return;

  container.innerHTML = "";
  const kwList = keywords || [];

  if (kwList.length === 0) {
    container.innerHTML = '<span class="text-muted small">Không có từ khóa nào được thiết lập.</span>';
    return;
  }

  kwList.forEach(kw => {
    const badge = document.createElement("span");
    badge.className = "badge bg-primary-soft text-primary p-2";
    badge.style.fontSize = "0.8rem";
    badge.style.fontWeight = "500";
    badge.innerText = kw;
    container.appendChild(badge);
  });
}

function renderAiPerformanceChart(historyData) {
  const canvas = document.getElementById("aiPerformanceChart");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  const labels = historyData.map(item => item.month);
  const data = historyData.map(item => item.accuracy);

  if (aiPerformanceChartInstance) {
    aiPerformanceChartInstance.destroy();
  }

  aiPerformanceChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Độ chính xác",
          data: data,
          borderColor: "#0d6efd",
          backgroundColor: "rgba(13, 110, 253, 0.08)",
          borderWidth: 3,
          tension: 0.35,
          fill: true,
          pointBackgroundColor: "#0d6efd",
          pointBorderColor: "#fff",
          pointHoverRadius: 6,
          pointRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: "#1e1e2d",
          titleColor: "#fff",
          bodyColor: "#fff",
          borderColor: "rgba(255,255,255,0.1)",
          borderWidth: 1,
          displayColors: false,
          callbacks: {
            label: function(context) {
              return ` Accuracy: ${context.parsed.y}%`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            display: false
          },
          ticks: {
            color: "rgba(255, 255, 255, 0.5)",
            font: {
              size: 11
            }
          }
        },
        y: {
          min: 60,
          max: 100,
          grid: {
            color: "rgba(255, 255, 255, 0.05)"
          },
          ticks: {
            color: "rgba(255, 255, 255, 0.5)",
            stepSize: 10,
            font: {
              size: 11
            },
            callback: function(value) {
              return value + "%";
            }
          }
        }
      }
    }
  });
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
  
  if (response.status === 401) {
    localStorage.removeItem("adminAccessToken");
    localStorage.removeItem("adminInfo");
    window.location.href = "/admin/login";
    return null;
  }

  const result = await response.json();
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

function escapeAiHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
