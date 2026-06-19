// homeAdmin.js
// Layout chung của trang home: theme, sidebar, tab, logout và khởi động module.

function applyTheme(theme) {
  const themeIcon = document.getElementById("themeIcon");

  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("adminTheme", theme);
  AdminState.currentTheme = theme;

  if (!themeIcon) return;

  if (theme === "dark") {
    themeIcon.className = "bi bi-sun";
  } else {
    themeIcon.className = "bi bi-moon-stars";
  }
}

function initThemeController() {
  const themeToggle = document.getElementById("themeToggle");

  applyTheme(AdminState.currentTheme);

  if (!themeToggle) return;

  themeToggle.addEventListener("click", function () {
    const newTheme = AdminState.currentTheme === "light" ? "dark" : "light";
    applyTheme(newTheme);

    if (AdminState.dashboardData) {
      initDashboardCharts();
    }
  });
}

function initSidebarController() {
  const sidebar = document.getElementById("sidebar");
  const sidebarToggle = document.getElementById("sidebarToggle");
  const sidebarClose = document.getElementById("sidebarClose");

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener("click", () => {
      sidebar.classList.add("show-mobile");
    });
  }

  if (sidebarClose && sidebar) {
    sidebarClose.addEventListener("click", () => {
      sidebar.classList.remove("show-mobile");
    });
  }
}

function initTabController() {
  const menuItems = document.querySelectorAll(".menu-item");
  const sidebar = document.getElementById("sidebar");

  menuItems.forEach((item) => {
    item.addEventListener("click", function (e) {
      e.preventDefault();

      const tabId = this.getAttribute("data-tab");
      switchTab(tabId);

      if (sidebar) {
        sidebar.classList.remove("show-mobile");
      }
    });
  });
}

function switchTab(tabId) {
  const menuItems = document.querySelectorAll(".menu-item");
  const tabPanes = document.querySelectorAll(".tab-pane");
  const currentTabLabel = document.getElementById("currentTabLabel");
  const tabPaneMap = {
    overview: "tab-overview",
    users: "tab-users",
    transactions: "tab-transactions",
    categories: "tab-categories",
    premium: "tab-premium",
    payments: "tab-payments",
    ai: "tab-ai",
    chatbot: "tab-chatbot",
    reports: "tab-reports",
    settings: "tab-settings",
  };

  menuItems.forEach((i) => i.classList.remove("active"));

  tabPanes.forEach((pane) => {
    pane.classList.add("d-none");
    pane.classList.remove("active-pane");
  });

  const targetNav = document.getElementById("nav-" + tabId);
  if (targetNav) {
    targetNav.classList.add("active");

    if (currentTabLabel) {
      currentTabLabel.innerText = targetNav.querySelector("span").innerText;
    }
  } else if (currentTabLabel) {
    currentTabLabel.innerText = "Tổng quan";
  }

  const targetPane = document.getElementById(tabPaneMap[tabId]);
  if (targetPane) {
    targetPane.classList.remove("d-none");
    targetPane.classList.add("active-pane");
  }

  handleTabLoad(tabId);
}

function handleTabLoad(tabId) {
  if (!AdminState.dashboardData) {
    fetchDashboardStats().then(() => {
      triggerTabAction(tabId);
    });
  } else {
    triggerTabAction(tabId);
  }
}

function triggerTabAction(tabId) {
  if (tabId === "overview") {
    initDashboardCharts();
    populateDashboardWidgets();
  } else if (tabId === "users") {
    populateUsersTable();
  } else if (tabId === "transactions") {
    populateTransactionsTable();
  } else if (tabId === "categories" && typeof populateCategoriesTable === "function") {
    populateCategoriesTable();
  } else if (tabId === "premium") {
    populatePremiumTable();
  } else if (tabId === "payments") {
    populatePaymentsTable();
  } else if (tabId === "chatbot" && typeof populateChatbotLogsTable === "function") {
    populateChatbotLogsTable();
  } else if (tabId === "ai" && typeof loadAiStatus === "function") {
    loadAiStatus();
  }
}

function performLogout(e) {
  e.preventDefault();

  if (confirm("Bạn có chắc chắn muốn đăng xuất khỏi tài khoản admin?")) {
    clearAdminSession();
    window.location.href = "/admin/login";
  }
}

function initLogoutController() {
  const logoutBtn = document.getElementById("logoutBtn");
  const dropLogout = document.getElementById("drop-logout");

  if (logoutBtn) logoutBtn.addEventListener("click", performLogout);
  if (dropLogout) dropLogout.addEventListener("click", performLogout);
}

function initDropdownActions() {
  const dropProfile = document.getElementById("drop-profile");
  const dropPassword = document.getElementById("drop-password");

  if (dropProfile) {
    dropProfile.addEventListener("click", function (e) {
      e.preventDefault();
      switchTab("settings");
    });
  }

  if (dropPassword) {
    dropPassword.addEventListener("click", function (e) {
      e.preventDefault();
      switchTab("settings");
    });
  }
}

function initLayoutModule() {
  initThemeController();
  initSidebarController();
  initTabController();
  initLogoutController();
  initDropdownActions();
}

// homeAdmin.js
// File chạy chính, gọi các module đã tách

document.addEventListener("DOMContentLoaded", function () {
  if (!requireAdminToken()) return;

  initLayoutModule();
  initProfileModule();
  initUsersModule();
  initTransactionsModule();
  if (typeof initCategoriesModule === "function") initCategoriesModule();
  if (typeof initChatbotModule === "function") initChatbotModule();
  initPremiumModule();
  initPaymentsModule();
  initAiModule();
  initReportSection();

  initDashboardModule();
});
