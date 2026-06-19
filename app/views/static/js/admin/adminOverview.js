// adminOverview.js
// Dashboard stats, widget tổng quan và Chart.js

async function fetchDashboardStats() {
  try {
    const apiResult = await apiRequest("/admin/api/stats");
    if (!apiResult) return;

    const { result } = apiResult;

    if (result.success) {
      AdminState.dashboardData = result.data;
      updateStatsUI();
    } else {
      console.error("Lỗi lấy dữ liệu dashboard:", result.message);
    }
  } catch (error) {
    console.error("Lỗi kết nối API stats:", error);
  }
}

function updateStatsUI() {
  const dashboardData = AdminState.dashboardData;
  if (!dashboardData) return;

  document.getElementById("stat-total-users").innerText =
    dashboardData.stats.totalUsers.toLocaleString();
  document.getElementById("stat-total-transactions").innerText =
    dashboardData.stats.totalTransactions.toLocaleString();
  document.getElementById("stat-premium-users").innerText =
    dashboardData.stats.premiumUsers.toLocaleString();
  document.getElementById("stat-total-revenue").innerText =
    dashboardData.stats.revenue.toLocaleString() + "đ";

  document.getElementById("trend-users").innerHTML =
    `<i class="bi bi-arrow-up-right me-1"></i>${dashboardData.stats.usersTrend}`;
  document.getElementById("trend-transactions").innerHTML =
    `<i class="bi bi-arrow-up-right me-1"></i>${dashboardData.stats.transactionsTrend}`;
  document.getElementById("trend-premium").innerHTML =
    `<i class="bi bi-arrow-up-right me-1"></i>${dashboardData.stats.premiumTrend}`;
  document.getElementById("trend-revenue").innerHTML =
    `<i class="bi bi-arrow-up-right me-1"></i>${dashboardData.stats.revenueTrend}`;

  const dashAiModel = document.getElementById("dashAiModel");
  const dashAiAccuracy = document.getElementById("dashAiAccuracy");
  const dashAiSamples = document.getElementById("dashAiSamples");
  const dashAiLastTrained = document.getElementById("dashAiLastTrained");
  const dashAiConfidence = document.getElementById("dashAiConfidence");
  const progressAccuracy = document.getElementById("progressAccuracy");
  const progressConfidence = document.getElementById("progressConfidence");
  const dashAiClassifiedToday = document.getElementById("dashAiClassifiedToday");

  if (dashAiModel)
    dashAiModel.innerText = dashboardData.aiModelStats.activeModel;
  if (dashAiAccuracy)
    dashAiAccuracy.innerText =
      dashboardData.aiModelStats.accuracy.toFixed(1) + "%";
  if (dashAiSamples)
    dashAiSamples.innerText =
      dashboardData.aiModelStats.totalTrained.toLocaleString() + " mẫu";
  if (dashAiLastTrained)
    dashAiLastTrained.innerText = dashboardData.aiModelStats.lastTrained;

  if (dashAiConfidence && dashboardData.aiModelStats.averageConfidence) {
    dashAiConfidence.innerText =
      dashboardData.aiModelStats.averageConfidence.toFixed(0) + "%";
  }
  if (progressAccuracy) {
    progressAccuracy.style.width = dashboardData.aiModelStats.accuracy + "%";
  }
  if (progressConfidence && dashboardData.aiModelStats.averageConfidence) {
    progressConfidence.style.width =
      dashboardData.aiModelStats.averageConfidence + "%";
  }
  if (dashAiClassifiedToday && dashboardData.aiModelStats.totalClassifiedToday) {
    dashAiClassifiedToday.innerText =
      dashboardData.aiModelStats.totalClassifiedToday.toLocaleString();
  }

  const activeModel = document.getElementById("aiActiveModel");
  const totalTrained = document.getElementById("aiTotalTrained");
  const lastTrained = document.getElementById("aiLastTrained");
  const accuracyText = document.getElementById("aiAccuracyText");
  const accuracyCircle = document.getElementById("aiAccuracyCircle");

  if (activeModel)
    activeModel.innerText = dashboardData.aiModelStats.activeModel;
  if (totalTrained)
    totalTrained.innerText =
      dashboardData.aiModelStats.totalTrained.toLocaleString() + " mẫu";
  if (lastTrained)
    lastTrained.innerText = dashboardData.aiModelStats.lastTrained;
  if (accuracyText)
    accuracyText.innerText =
      dashboardData.aiModelStats.accuracy.toFixed(1) + "%";

  if (accuracyCircle) {
    const acc = dashboardData.aiModelStats.accuracy;
    const offset = 251.2 - (251.2 * acc) / 100;
    accuracyCircle.style.strokeDashoffset = offset;
  }
}

function populateDashboardWidgets() {
  const dashboardData = AdminState.dashboardData;
  if (!dashboardData) return;

  populateRecentTransactionsWidget(dashboardData);
  populateNewUsersWidget(dashboardData);
  populateSystemAlertsWidget(dashboardData);
  populateChatbotLogsWidget(dashboardData);
}

function populateRecentTransactionsWidget(dashboardData) {
  const txnBody = document.getElementById("dashRecentTxnBody");
  if (!txnBody || !dashboardData.recentTransactions) return;

  txnBody.innerHTML = "";
  const recentTxns = dashboardData.recentTransactions.slice(0, 5);

  if (recentTxns.length === 0) {
    txnBody.innerHTML = `<tr><td colspan="6" class="text-center text-muted py-4">Chưa có giao dịch nào.</td></tr>`;
    return;
  }

  recentTxns.forEach((txn) => {
    const tr = document.createElement("tr");
    const typeBadge =
      txn.loai === "THU"
        ? `<span class="badge bg-success-soft text-success fw-bold">THU</span>`
        : `<span class="badge bg-danger-soft text-danger fw-bold">CHI</span>`;
    const amountClass = txn.loai === "THU" ? "plus" : "minus";
    const amountPrefix = txn.loai === "THU" ? "+" : "-";
    const statusBadge = `<span class="badge bg-success-soft text-success"><i class="bi bi-check-circle me-1"></i>${txn.trangThai}</span>`;

    tr.innerHTML = `
      <td class="fw-semibold">${txn.ten}</td>
      <td>${typeBadge}</td>
      <td class="fw-bold">${txn.danhMuc}</td>
      <td><span class="txn-amount ${amountClass}">${amountPrefix}${txn.soTien.toLocaleString()}đ</span></td>
      <td class="text-muted small">${txn.ngay}</td>
      <td>${statusBadge}</td>
    `;

    txnBody.appendChild(tr);
  });
}

function populateNewUsersWidget(dashboardData) {
  const newUsersList = document.getElementById("dashNewUsersList");
  if (!newUsersList || !dashboardData.newUsersList) return;

  newUsersList.innerHTML = "";
  const sortedUsers = dashboardData.newUsersList.slice(0, 5);

  const avatarColors = [
    "var(--grad-blue)",
    "var(--grad-emerald)",
    "var(--grad-purple)",
    "var(--grad-orange)",
    "linear-gradient(135deg, #ec4899 0%, #be185d 100%)",
  ];

  if (sortedUsers.length === 0) {
    newUsersList.innerHTML = `<div class="text-center py-4 text-muted">Chưa có người dùng mới.</div>`;
    return;
  }

  sortedUsers.forEach((user, idx) => {
    const initial = user.ten
      ? user.ten.charAt(0).toUpperCase()
      : user.email.charAt(0).toUpperCase();
    const color = avatarColors[idx % avatarColors.length];

    let roleBadgeClass = "bg-primary-soft text-primary";
    if (user.vaiTro === "PREMIUM")
      roleBadgeClass = "bg-success-soft text-success";
    if (user.vaiTro === "ADMIN")
      roleBadgeClass = "bg-warning-soft text-warning";

    const el = document.createElement("div");
    el.className = "new-user-item";
    el.innerHTML = `
      <div class="new-user-avatar" style="background: ${color}">${initial}</div>
      <div class="new-user-info">
        <p class="new-user-email fw-bold text-truncate">${user.ten || user.email}</p>
        <p class="new-user-date"><i class="bi bi-clock me-1"></i>${user.time || "Vừa xong"}</p>
      </div>
      <span class="badge new-user-badge ${roleBadgeClass}">${user.vaiTro}</span>
    `;

    newUsersList.appendChild(el);
  });
}

function populateSystemAlertsWidget(dashboardData) {
  const alertsList = document.getElementById("dashSystemAlertsList");
  const alertCountBadge = document.getElementById("alertCountBadge");
  if (!alertsList || !dashboardData.systemAlerts) return;

  alertsList.innerHTML = "";
  const alerts = dashboardData.systemAlerts;

  if (alertCountBadge) {
    alertCountBadge.innerHTML = `<i class="bi bi-exclamation-triangle me-1"></i>${alerts.length} cảnh báo`;
  }

  if (alerts.length === 0) {
    alertsList.innerHTML = `<div class="text-center py-4 text-muted">Không có cảnh báo nào.</div>`;
    return;
  }

  const iconMap = {
    danger: "bi-exclamation-circle-fill",
    warning: "bi-exclamation-triangle-fill",
    info: "bi-info-circle-fill",
    success: "bi-check-circle-fill",
  };

  alerts.forEach((alert) => {
    const level = alert.level || "info";
    const iconClass = iconMap[level] || iconMap.info;

    let detail = alert.detail;
    let time = alert.time;

    if (!detail) {
      if (alert.title.includes("giao dịch")) {
        detail =
          "Phát hiện một số giao dịch tự động phân loại bằng AI nhưng có độ tin cậy thấp.";
        time = "10 phút trước";
      } else if (alert.title.includes("Premium")) {
        detail = "Thời hạn còn lại dưới 3 ngày, cần nhắc nhở gia hạn.";
        time = "1 giờ trước";
      } else if (alert.title.includes("chatbot")) {
        detail =
          "Phát hiện lỗi ngoại lệ khi hệ thống trả lời câu hỏi của người dùng.";
        time = "2 giờ trước";
      } else {
        detail = "Cần kiểm tra trạng thái hoạt động hệ thống.";
        time = "Vừa xong";
      }
    }

    const el = document.createElement("div");
    el.className = `system-alert-item alert-${level}`;
    el.innerHTML = `
      <i class="bi ${iconClass} system-alert-icon text-${level}"></i>
      <div class="system-alert-content">
        <h6 class="system-alert-title">${alert.title}</h6>
        <p class="system-alert-desc">${detail}</p>
        <span class="system-alert-time">${time}</span>
      </div>
    `;

    alertsList.appendChild(el);
  });
}

function populateChatbotLogsWidget(dashboardData) {
  const chatbotBody = document.getElementById("dashChatbotLogsBody");
  if (!chatbotBody || !dashboardData.chatbotLogs) return;

  chatbotBody.innerHTML = "";
  const logs = dashboardData.chatbotLogs.slice(0, 5);

  if (logs.length === 0) {
    chatbotBody.innerHTML = `<tr><td colspan="4" class="text-center text-muted py-4">Chưa có hoạt động chatbot nào.</td></tr>`;
    return;
  }

  logs.forEach((log) => {
    const tr = document.createElement("tr");
    const statusBadge = `<span class="badge bg-success-soft text-success"><i class="bi bi-chat-left-check me-1"></i>${log.trangThai}</span>`;

    tr.innerHTML = `
      <td class="fw-semibold">${log.email}</td>
      <td class="text-truncate" style="max-width: 300px;">"${log.cauHoi}"</td>
      <td class="text-muted small">${log.time}</td>
      <td>${statusBadge}</td>
    `;

    chatbotBody.appendChild(tr);
  });
}

function initDashboardCharts() {
  const dashboardData = AdminState.dashboardData;
  if (!dashboardData) return;

  const isDark =
    document.documentElement.getAttribute("data-theme") === "dark";
  const textColour = isDark ? "#94a3b8" : "#475569";
  const gridColour = isDark
    ? "rgba(51, 65, 85, 0.3)"
    : "rgba(226, 232, 240, 0.7)";

  initUserGrowthChart(dashboardData, textColour, gridColour);
  initUserPremiumRatioChart(dashboardData, textColour, isDark);
}

function initUserGrowthChart(dashboardData, textColour, gridColour) {
  const growthCtx = document.getElementById("userGrowthChart");
  if (!growthCtx || !dashboardData.charts.userGrowth) return;

  if (AdminState.charts.userGrowth) AdminState.charts.userGrowth.destroy();

  AdminState.charts.userGrowth = new Chart(growthCtx, {
    type: "line",
    data: {
      labels: dashboardData.charts.userGrowth.labels,
      datasets: [
        {
          label: "Tổng người dùng",
          data: dashboardData.charts.userGrowth.users,
          borderColor: "#3b82f6",
          backgroundColor: "rgba(59, 130, 246, 0.04)",
          tension: 0.4,
          fill: true,
          borderWidth: 3,
          pointBackgroundColor: "#3b82f6",
          pointRadius: 4,
          pointHoverRadius: 6,
        },
        {
          label: "Người dùng Premium",
          data: dashboardData.charts.userGrowth.premiumUsers || [],
          borderColor: "#10b981",
          backgroundColor: "rgba(16, 185, 129, 0.04)",
          tension: 0.4,
          fill: true,
          borderWidth: 3,
          pointBackgroundColor: "#10b981",
          pointRadius: 4,
          pointHoverRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: textColour,
            font: { family: "Be Vietnam Pro", weight: 600 },
          },
        },
      },
      scales: {
        x: {
          grid: { color: "transparent" },
          ticks: { color: textColour, font: { family: "Be Vietnam Pro" } },
        },
        y: {
          grid: { color: gridColour },
          ticks: { color: textColour, font: { family: "Be Vietnam Pro" } },
        },
      },
    },
  });
}

function initUserPremiumRatioChart(dashboardData, textColour, isDark) {
  const ratioCtx = document.getElementById("userPremiumRatioChart");
  if (!ratioCtx || !dashboardData.charts.userPremiumRatio) return;

  if (AdminState.charts.userPremiumRatio) {
    AdminState.charts.userPremiumRatio.destroy();
  }

  AdminState.charts.userPremiumRatio = new Chart(ratioCtx, {
    type: "doughnut",
    data: {
      labels: dashboardData.charts.userPremiumRatio.labels,
      datasets: [
        {
          data: dashboardData.charts.userPremiumRatio.values,
          backgroundColor: ["#64748b", "#10b981"],
          borderWidth: 3,
          borderColor: isDark ? "#151f32" : "#ffffff",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            color: textColour,
            font: { family: "Be Vietnam Pro", size: 12, weight: 600 },
            padding: 16,
          },
        },
      },
      cutout: "70%",
    },
  });
}

function initOverviewModule() {
  return fetchDashboardStats().then(() => {
    initDashboardCharts();
    populateDashboardWidgets();
  });
}


// Alias để homeAdmin.js cũ vẫn gọi được.
function initDashboardModule() {
  initOverviewModule();
}
