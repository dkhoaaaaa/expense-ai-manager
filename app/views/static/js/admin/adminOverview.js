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

document.getElementById("btnExportReport").addEventListener("click", async function() {
  const btnExport = this;
  btnExport.disabled = true;
  const originalText = btnExport.innerHTML;
  btnExport.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Đang xuất...`;

  try {
    const now = new Date();
    const month = now.getMonth() + 1;
    const year = now.getFullYear();

    const response = await fetch("/admin/api/reports/export", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + AdminState.token,
      },
      body: JSON.stringify({
        report_type: "excel",
        month: month,
        year: year,
      }),
    });

    if (response.status === 401) {
      const result = await response.json();
      handleUnauthorized(result);
      return;
    }

    if (!response.ok) {
      let errMsg = "Vui lòng thử lại sau";
      try {
        const result = await response.json();
        errMsg = result.message || errMsg;
      } catch (e) {}
      
      showToast(
        "error",
        "Không thể xuất báo cáo",
        errMsg
      );
      return;
    }

    const blob = await response.blob();
    const disposition = response.headers.get("Content-Disposition") || "";
    const fileNameMatch = disposition.match(/filename="?([^"]+)"?/);
    const fileName = fileNameMatch ? fileNameMatch[1] : `expense-report-${String(month).padStart(2, '0')}-${year}.xlsx`;
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = downloadUrl;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);

    showToast("success", "Xuất báo cáo", "Tải báo cáo thành công");
  } catch (error) {
    console.error("Export report error:", error);
    showToast("error", "Lỗi", error.message || "Không thể kết nối máy chủ");
  } finally {
    btnExport.innerHTML = originalText;
    btnExport.disabled = false;
  }
});

function updateStatsUI() {
  const dashboardData = AdminState.dashboardData;
  if (!dashboardData) return;

  document.getElementById("stat-total-users").innerText =
    dashboardData.stats.totalUsers.toLocaleString();
  document.getElementById("stat-total-transactions").innerText =
    (dashboardData.stats.currentMonthTransactions || 0).toLocaleString();
  document.getElementById("stat-premium-users").innerText =
    dashboardData.stats.premiumUsers.toLocaleString();
  document.getElementById("stat-total-revenue").innerText =
    (dashboardData.stats.currentMonthRevenue || 0).toLocaleString() + "đ";

  document.getElementById("trend-users").innerHTML =
    `<i class="bi bi-arrow-up-right me-1"></i>${dashboardData.stats.usersTrend}`;
  document.getElementById("trend-transactions").innerHTML =
    `<i class="bi bi-arrow-up-right me-1"></i>${dashboardData.stats.transactionsTrend}`;
  document.getElementById("trend-premium").innerHTML =
    `${dashboardData.stats.premiumTrend}`;
  document.getElementById("trend-revenue").innerHTML =
    `${dashboardData.stats.revenueTrend}`;
}

function populateDashboardWidgets() {
  const dashboardData = AdminState.dashboardData;
  if (!dashboardData) return;

  populateRecentActivitiesTimeline(dashboardData);
}

function populateRecentActivitiesTimeline(dashboardData) {
  const timelineEl = document.getElementById("recentActivitiesTimeline");
  if (!timelineEl || !dashboardData.recentActivities) return;

  timelineEl.innerHTML = "";
  const activities = dashboardData.recentActivities;

  if (activities.length === 0) {
    timelineEl.innerHTML = `<div class="text-center py-4 text-muted">Chưa có hoạt động nào gần đây.</div>`;
    return;
  }

  const iconMap = {
    "USER_SIGNUP": { icon: "bi-person-plus", class: "timeline-icon-signup" },
    "PREMIUM_PURCHASE": { icon: "bi-gem", class: "timeline-icon-premium" },
    "PAYMENT_SUCCESS": { icon: "bi-cash-coin", class: "timeline-icon-payment" },
    "AI_PREDICTION": { icon: "bi-cpu", class: "timeline-icon-ai" },
    "TRANSACTION_CREATED": { icon: "bi-credit-card", class: "timeline-icon-payment" },
    "BUDGET_CREATED": { icon: "bi-pie-chart-fill", class: "timeline-icon-premium" }
  };

  activities.forEach(act => {
    const iconInfo = iconMap[act.type] || { icon: "bi-info-circle", class: "bg-secondary" };
    const itemEl = document.createElement("div");
    itemEl.className = "timeline-item";
    itemEl.innerHTML = `
      <div class="timeline-icon-box ${iconInfo.class}">
        <i class="bi ${iconInfo.icon}"></i>
      </div>
      <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-2">
        <div>
          <h6 class="fw-bold mb-1 text-dark" style="font-size: 14px;">${act.title}</h6>
          <p class="text-muted mb-0" style="font-size: 13px;">${act.description}</p>
        </div>
        <span class="text-muted small font-monospace">${act.time}</span>
      </div>
    `;
    timelineEl.appendChild(itemEl);
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
  const btnRefresh = document.getElementById("btnRefreshStats");
  if (btnRefresh && !btnRefresh.dataset.listenerBound) {
    btnRefresh.addEventListener("click", async () => {
      btnRefresh.disabled = true;
      const originalText = btnRefresh.innerHTML;
      btnRefresh.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Đang tải...`;
      
      await fetchDashboardStats();
      initDashboardCharts();
      populateDashboardWidgets();
      
      btnRefresh.innerHTML = originalText;
      btnRefresh.disabled = false;
      
      if (typeof showToast === "function") {
        showToast("success", "Thành công", "Đã cập nhật dữ liệu mới nhất.");
      }
    });
    btnRefresh.dataset.listenerBound = "true";
  }

  return fetchDashboardStats().then(() => {
    initDashboardCharts();
    populateDashboardWidgets();
  });
}


// Alias để homeAdmin.js cũ vẫn gọi được.
function initDashboardModule() {
  initOverviewModule();
}
