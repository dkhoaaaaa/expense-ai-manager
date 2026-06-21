document.addEventListener("DOMContentLoaded", () => {
  // --- 1. BIẾN TOÀN CỤC ---
  let globalCategories = [];
  let userRole = "USER";
  let activeTab = "overview";
  
  // Instance biểu đồ toàn cục để hủy và vẽ lại khi cần
  let incomeChartInstance = null;
  let expenseChartInstance = null;
  let timeSeriesChartInstance = null;
  let budgetPieChartInstance = null;
  // Lấy các tham số cấu hình
  const urlParams = new URLSearchParams(window.location.search);
  const queryUserId = urlParams.get("user_id") || "2";

  // Định dạng tiền tệ VND
  function formatCurrency(amount) {
    return new Intl.NumberFormat("vi-VN", {
      style: "currency",
      currency: "VND",
    }).format(amount).replace("₫", "đ");
  }

  // Cập nhật xu hướng (trend)
  function updateTrend(elementId, trendText) {
    const el = document.getElementById(elementId);
    if (!el) return;

    const isUp = trendText.includes("+");
    const isDown = trendText.includes("-");
    let icon = "";
    let className = "trend";

    if (isUp) {
      icon = '<i class="bi bi-arrow-up-right"></i>';
      className = "trend up";
    } else if (isDown) {
      icon = '<i class="bi bi-arrow-down-right"></i>';
      className = "trend down";
    }

    el.className = className;
    el.innerHTML = `${icon}${trendText}`;
  }

  // Ánh xạ danh mục sang icon
  function getCategoryIcon(catName) {
    const map = {
      "Ăn uống": "bi-cup-hot",
      "Di chuyển": "bi-car-front",
      "Mua sắm": "bi-bag",
      "Giải trí": "bi-controller",
      "Học tập": "bi-book",
      "Sức khỏe": "bi-heart-pulse",
      "Hóa đơn": "bi-file-earmark-text",
      "Nhà ở": "bi-house",
      "Lương": "bi-briefcase",
      "Thưởng": "bi-award",
      "Đầu tư": "bi-graph-up",
      "Khác": "bi-question-circle",
    };
    return map[catName] || "bi-wallet2";
  }

  // --- 2. QUẢN LÝ TABS (SPA & DYNAMIC CONTENT) ---
  const tabLinks = document.querySelectorAll("[data-tab]");

  // Các template HTML render phía client
  const pageTemplates = {
    overview: `
      <section class="row g-4 mb-4" aria-label="Thống kê tổng quan">
        <div class="col-12 col-md-4">
          <article class="app-card stat-card">
            <div class="stat-icon">
              <i class="bi bi-wallet2"></i>
            </div>
            <div class="stat-content">
              <p>Số dư hiện tại</p>
              <h2 id="balance-amount">0đ</h2>
              <span class="trend" id="balance-trend"><i class="bi bi-arrow-up-right"></i>0% so với tháng trước</span>
            </div>
          </article>
        </div>

        <div class="col-12 col-md-4">
          <article class="app-card stat-card">
            <div class="stat-icon">
              <i class="bi bi-arrow-down-circle"></i>
            </div>
            <div class="stat-content">
              <p>Tổng thu nhập</p>
              <h2 id="income-amount">0đ</h2>
              <span class="trend" id="income-trend"><i class="bi bi-arrow-up-right"></i>0% so với tháng trước</span>
            </div>
          </article>
        </div>

        <div class="col-12 col-md-4">
          <article class="app-card stat-card">
            <div class="stat-icon danger">
              <i class="bi bi-arrow-up-circle"></i>
            </div>
            <div class="stat-content">
              <p>Tổng chi tiêu</p>
              <h2 id="expense-amount">0đ</h2>
              <span class="trend" id="expense-trend"><i class="bi bi-arrow-down-right"></i>0% so với tháng trước</span>
            </div>
          </article>
        </div>
      </section>

      <section class="row g-4 mb-4" aria-label="Biểu đồ tháng">
        <div class="col-12 col-xl-6">
          <article class="app-card chart-card">
            <div class="card-heading">
              <div>
                <h2>Thu nhập trong tháng</h2>
                <p>Biểu đồ thu nhập theo ngày</p>
              </div>
              <span class="soft-badge">Tháng này</span>
            </div>
            <div class="chart-container" style="position: relative; height: 220px; width: 100%">
              <canvas id="incomeChart"></canvas>
            </div>
          </article>
        </div>

        <div class="col-12 col-xl-6">
          <article class="app-card chart-card">
            <div class="card-heading">
              <div>
                <h2>Chi tiêu trong tháng</h2>
                <p>Biểu đồ xu hướng chi tiêu theo ngày</p>
              </div>
              <span class="soft-badge blue">Tháng này</span>
            </div>
            <div class="chart-container" style="position: relative; height: 220px; width: 100%">
              <canvas id="expenseChart"></canvas>
            </div>
          </article>
        </div>
      </section>

      <section class="row g-4 mb-4" aria-label="Giao dịch và danh mục">
        <div class="col-12 col-xl-8">
          <article class="app-card h-100">
            <div class="card-heading">
              <div>
                <h2>Giao dịch gần đây</h2>
                <p>5 giao dịch mới nhất của bạn</p>
              </div>
              <button class="btn btn-ghost btn-sm" type="button" data-tab="transactions">
                Xem tất cả
              </button>
            </div>
            <div class="transaction-list" id="recent-transactions-list">
              <!-- Render động -->
            </div>
          </article>
        </div>

        <div class="col-12 col-xl-4">
          <article class="app-card h-100">
            <div class="card-heading compact">
              <div>
                <h2>Top danh mục chi tiêu</h2>
                <p>Xếp hạng theo tổng tiền</p>
              </div>
            </div>
            <div class="category-ranking" id="top-categories-list">
              <!-- Render động -->
            </div>
          </article>
        </div>
      </section>
    `,
    transactions: `
      <div class="app-card mb-4">
        <div class="card-heading">
          <div>
            <h2>Danh sách giao dịch</h2>
            <p>Tra cứu và quản lý tất cả các khoản chi tiêu/thu nhập</p>
          </div>
        </div>
        
        <div class="filter-bar row g-2">
          <div class="col-12 col-md-3">
            <input type="text" class="form-control" id="tx-search-input" placeholder="Tìm kiếm theo mô tả..." autocomplete="off">
          </div>
          <div class="col-6 col-md-2">
            <select class="form-select" id="tx-filter-type">
              <option value="">-- Tất cả loại --</option>
              <option value="THU">Thu nhập</option>
              <option value="CHI">Chi tiêu</option>
            </select>
          </div>
          <div class="col-6 col-md-2">
            <select class="form-select" id="tx-filter-category">
              <option value="">-- Danh mục --</option>
            </select>
          </div>
          <div class="col-6 col-md-2">
            <select class="form-select" id="tx-filter-month">
              <option value="">-- Tất cả tháng --</option>
              <option value="1">Tháng 1</option>
              <option value="2">Tháng 2</option>
              <option value="3">Tháng 3</option>
              <option value="4">Tháng 4</option>
              <option value="5">Tháng 5</option>
              <option value="6" selected>Tháng 6</option>
              <option value="7">Tháng 7</option>
              <option value="8">Tháng 8</option>
              <option value="9">Tháng 9</option>
              <option value="10">Tháng 10</option>
              <option value="11">Tháng 11</option>
              <option value="12">Tháng 12</option>
            </select>
          </div>
          <div class="col-6 col-md-3">
            <button class="btn btn-main w-100" type="button" id="btn-tx-filter-apply">
              <i class="bi bi-funnel"></i> Áp dụng lọc
            </button>
          </div>
        </div>

        <div class="table-responsive mt-3">
          <table class="table custom-table align-middle">
            <thead>
              <tr>
                <th style="width: 15%">Ngày</th>
                <th style="width: 35%">Mô tả</th>
                <th style="width: 20%">Danh mục</th>
                <th style="width: 15%">Loại</th>
                <th style="width: 15%" class="text-end">Số tiền</th>
                <th style="width: 10%" class="text-center">Thao tác</th>
              </tr>
            </thead>
            <tbody id="transaction-table-body">
              <!-- Dynamic content -->
            </tbody>
          </table>
        </div>
      </div>
    `,
    budgets: `
      <div class="budget-tab-wrapper">
        <!-- 1. Summary Cards: Tổng NS | Đã dùng | Còn lại -->
        <section class="budget-summary-cards" aria-label="Thống kê tổng quan ngân sách">
          <article class="budget-summary-card">
            <div class="budget-summary-icon">
              <i class="bi bi-wallet2"></i>
            </div>
            <div class="budget-summary-info">
              <span class="budget-summary-label">Tổng ngân sách</span>
              <h3 class="budget-summary-value" id="budget-total-amount">0đ</h3>
            </div>
            <div class="budget-summary-decoration"></div>
          </article>
          <article class="budget-summary-card spent">
            <div class="budget-summary-icon spent">
              <i class="bi bi-cart-dash"></i>
            </div>
            <div class="budget-summary-info">
              <span class="budget-summary-label">Đã sử dụng</span>
              <h3 class="budget-summary-value" id="budget-total-spent">0đ</h3>
            </div>
            <div class="budget-summary-decoration spent"></div>
          </article>
          <article class="budget-summary-card remaining">
            <div class="budget-summary-icon remaining">
              <i class="bi bi-piggy-bank"></i>
            </div>
            <div class="budget-summary-info">
              <span class="budget-summary-label">Còn lại</span>
              <h3 class="budget-summary-value" id="budget-total-remaining">0đ</h3>
            </div>
            <div class="budget-summary-decoration remaining"></div>
          </article>
        </section>

        <!-- 2. Form thiết lập ngân sách -->
        <section class="budget-form-section">
          <article class="app-card budget-form-card">
            <div class="budget-form-header">
              <div class="budget-form-icon-wrapper">
                <i class="bi bi-sliders2"></i>
              </div>
              <div>
                <h4 class="fw-bold mb-1">Thiết lập ngân sách</h4>
                <p class="text-muted small mb-0">Đặt hạn mức chi tiêu hàng tháng cho từng danh mục</p>
              </div>
            </div>
            <form id="setBudgetForm" class="budget-form-grid">
              <div class="budget-form-field">
                <label class="form-label fw-semibold"><i class="bi bi-tag me-1 text-muted"></i>Danh mục</label>
                <select class="form-select form-custom-input" id="budget-category-select" required></select>
              </div>
              <div class="budget-form-field">
                <label class="form-label fw-semibold"><i class="bi bi-calendar3 me-1 text-muted"></i>Tháng</label>
                <select class="form-select form-custom-input" id="budget-month" required>
                  <option value="1">Tháng 1</option><option value="2">Tháng 2</option>
                  <option value="3">Tháng 3</option><option value="4">Tháng 4</option>
                  <option value="5">Tháng 5</option><option value="6" selected>Tháng 6</option>
                  <option value="7">Tháng 7</option><option value="8">Tháng 8</option>
                  <option value="9">Tháng 9</option><option value="10">Tháng 10</option>
                  <option value="11">Tháng 11</option><option value="12">Tháng 12</option>
                </select>
              </div>
              <div class="budget-form-field">
                <label class="form-label fw-semibold"><i class="bi bi-calendar-range me-1 text-muted"></i>Năm</label>
                <select class="form-select form-custom-input" id="budget-year" required>
                  <option value="2025">2025</option><option value="2026" selected>2026</option>
                </select>
              </div>
              <div class="budget-form-field">
                <label for="budget-amount" class="form-label fw-semibold"><i class="bi bi-currency-exchange me-1 text-muted"></i>Hạn mức (đ)</label>
                <input type="number" class="form-control form-custom-input" id="budget-amount" placeholder="VD: 5,000,000" required min="1">
              </div>
              <div class="budget-form-submit">
                <button type="submit" class="btn btn-main w-100">
                  <i class="bi bi-check2-circle"></i> Lưu hạn mức
                </button>
              </div>
            </form>
          </article>
        </section>

        <!-- 3. Danh sách ngân sách + progress bar -->
        <section class="budget-list-section">
          <article class="app-card">
            <div class="card-heading">
              <div>
                <h2><i class="bi bi-list-check me-2 text-muted"></i>Chi tiết ngân sách</h2>
                <p>Theo dõi tiến độ chi tiêu theo từng danh mục</p>
              </div>
              <span class="soft-badge" id="budget-month-badge">Tháng 6/2026</span>
            </div>
            <div id="budget-detailed-list" class="budget-items-grid">
              <!-- Dynamic content -->
            </div>
          </article>
        </section>

        <!-- 4. Pie Chart -->
        <section class="budget-chart-section">
          <article class="app-card">
            <div class="card-heading">
              <div>
                <h2><i class="bi bi-pie-chart me-2 text-muted"></i>Tỷ lệ phân bổ ngân sách</h2>
                <p>Cơ cấu hạn mức giữa các danh mục chi tiêu</p>
              </div>
            </div>
            <div class="budget-chart-container">
              <canvas id="budgetPieChart"></canvas>
            </div>
          </article>
        </section>
      </div>
    `,
    ai: `<div class="text-center py-5"><div class="spinner-border text-success"></div><p class="mt-2 text-muted">Đang tải Trợ lý AI...</p></div>`,
    settings: `<div class="text-center py-5"><div class="spinner-border text-success"></div><p class="mt-2 text-muted">Đang tải Cài đặt...</p></div>`
  };

  // Cấu hình nội dung Hero Section cho từng tab
  const heroConfig = {
    overview: {
      badge: "Hệ thống",
      title: "Tổng quan tài chính",
      description: "Xem và phân tích tình hình thu chi, số dư hiện tại của tài khoản của bạn.",
      cta: `
        <button class="btn btn-ghost" type="button" data-tab="ai" id="btn-quick-ai">
          <i class="bi bi-stars text-success"></i>
          <span>Trợ lý AI</span>
        </button>
      `
    },
    transactions: {
      badge: "Sổ thu chi",
      title: "Quản lý giao dịch thu chi",
      description: "Tìm kiếm, lọc danh mục và thực hiện ghi chép các khoản chi tiêu hàng ngày.",
      cta: `
        <button class="btn btn-main" type="button" data-bs-toggle="modal" data-bs-target="#addTransactionModal">
          <i class="bi bi-plus-lg"></i>
          <span>Thêm giao dịch mới</span>
        </button>
      `
    },
    budgets: {
      badge: "Lập kế hoạch",
      title: "Quản lý ngân sách và danh mục",
      description: "Theo dõi hạn mức ngân sách tháng và tùy biến các danh mục thu chi.",
      cta: `
        <button class="btn btn-main" type="button" id="btn-focus-budget">
          <i class="bi bi-pencil-fill"></i>
          <span>Đặt hạn mức</span>
        </button>
      `
    },
    ai: {
      badge: "Trí tuệ nhân tạo",
      title: "Phân tích, dự đoán và gợi ý bằng AI",
      description: "Sử dụng sức mạnh của Machine Learning để dự báo chi tiêu và tự động phân loại.",
      cta: `
        <button class="btn btn-main" type="button" id="btn-focus-ai-desc">
          <i class="bi bi-magic"></i>
          <span>Hỏi AI Assistant</span>
        </button>
      `
    },
    settings: {
      badge: "Tài khoản",
      title: "Thông tin cá nhân và bảo mật tài khoản",
      description: "Cập nhật thông tin liên hệ, đổi mật khẩu và quản lý gói Premium VIP.",
      cta: `
        <button class="btn btn-main" type="button" onclick="alert('Tính năng nâng cấp Premium VIP!')">
          <i class="bi bi-gem"></i>
          <span>Đăng ký Premium</span>
        </button>
      `
    }
  };

  function setInnerHTMLWithScripts(el, html) {
    el.innerHTML = html;
    const scripts = el.querySelectorAll("script");
    scripts.forEach(oldScript => {
      const newScript = document.createElement("script");
      Array.from(oldScript.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value));
      newScript.appendChild(document.createTextNode(oldScript.innerHTML));
      oldScript.parentNode.replaceChild(newScript, oldScript);
    });
  }

  async function switchTab(tabId) {
    activeTab = tabId;
    
    // Cập nhật trạng thái active trong sidebar & offcanvas
    tabLinks.forEach(link => {
      if (link.getAttribute("data-tab") === tabId) {
        link.classList.add("active");
      } else {
        link.classList.remove("active");
      }
    });

    // Tạo hiệu ứng chuyển cảnh mượt cho Hero Section / Topbar
    const topbarText = document.querySelector(".topbar-text");
    const topbarActions = document.querySelector(".topbar-actions");
    
    if (topbarText && topbarActions) {
      topbarText.classList.add("fade-out");
      topbarActions.classList.add("fade-out");
      
      setTimeout(() => {
        const config = heroConfig[tabId] || heroConfig.overview;
        
        // Cập nhật nội dung Hero
        const currentTabLabel = document.getElementById("current-tab-label");
        const topbarTitle = document.getElementById("topbar-title");
        const topbarSubtext = document.getElementById("topbar-subtext");
        
        if (currentTabLabel) currentTabLabel.innerText = config.badge;
        if (topbarTitle) topbarTitle.innerText = config.title;
        if (topbarSubtext) topbarSubtext.innerText = config.description;
        topbarActions.innerHTML = config.cta;
        
        // Xóa class để hoàn thành hiệu ứng mượt
        topbarText.classList.remove("fade-out");
        topbarActions.classList.remove("fade-out");
      }, 200);
    }

    const container = document.getElementById("hero-content-container");
    if (!container) return;

    // Hiệu ứng fade-out nội dung
    container.classList.add("fade-out");
    container.classList.remove("fade-in");

    // Chờ animation fade-out chạy xong (150ms) rồi inject HTML và load data
    setTimeout(async () => {
      // TODO: Module Transactions sẽ được Member phụ trách Transaction phát triển
      if (tabId === "transactions") {
        container.innerHTML = `
          <div class="empty-state text-center py-5">
              <i class="bi bi-folder-x display-3 text-secondary"></i>
              <h3 class="mt-3">Module đang được phát triển</h3>
              <p class="text-muted">
                  Chức năng này đang được thành viên khác phụ trách phát triển.
              </p>
          </div>
        `;
        container.classList.remove("fade-out");
        container.classList.add("fade-in");
        return;
      }

      // Tab Ngân sách: render trực tiếp từ client template
      if (tabId === "budgets") {
        container.innerHTML = pageTemplates.budgets;
        container.classList.remove("fade-out");
        container.classList.add("fade-in");
        if (document.getElementById("budget-detailed-list")) {
          loadBudgetsTab();
        }
        return;
      }

      // 1. Nếu là tab overview, render trực tiếp từ client template
      if (tabId === "overview") {
        container.innerHTML = pageTemplates.overview;
        container.classList.remove("fade-out");
        container.classList.add("fade-in");
        if (document.getElementById("balance-amount")) {
          loadHomeData();
        }
        return;
      }

      // 2. Với các tab khác, hiển thị loading spinner tạm thời
      container.innerHTML = pageTemplates[tabId] || `<div class="text-center py-5"><div class="spinner-border text-success"></div><p class="mt-2 text-muted">Đang tải...</p></div>`;
      container.classList.remove("fade-out");
      container.classList.add("fade-in");

      // Ánh xạ tabId sang endpoint tương ứng trên backend Flask
      let backendTab = tabId;
      if (tabId === "ai") backendTab = "ai-hub";
      if (tabId === "settings") backendTab = "profile";

      try {
        const response = await fetch(`/home/content/${backendTab}`);
        if (!response.ok) throw new Error("Không thể kết nối đến máy chủ");
        const htmlText = await response.text();

        // Nếu backend trả về empty-state (tức là file HTML không tồn tại trên server)
        if (htmlText.includes("empty-state")) {
          container.innerHTML = pageTemplates[tabId] || `<div class="alert alert-warning">Tab không hợp lệ.</div>`;
        } else {
          // Trích xuất phần nội dung container chính
          const tempDiv = document.createElement("div");
          tempDiv.innerHTML = htmlText;

          let targetHtml = "";
          if (tabId === "settings") {
            // Tự động nạp thêm file CSS của tab Profile để đảm bảo giao diện đẹp
            targetHtml += `<link rel="stylesheet" href="/static/css/user/profile.css">`;
            const targetEl = tempDiv.querySelector(".container.py-5");
            targetHtml += targetEl ? targetEl.innerHTML : htmlText;
          } else if (tabId === "ai") {
            // Tự động chèn CSS nội bộ của tab AI do bị bỏ đi khi render partial
            targetHtml += `
              <style>
                .ai-card { border-radius: 15px; border: none; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
                .suggestion-chip { cursor: pointer; transition: 0.2s; }
                .suggestion-chip:hover { transform: translateY(-2px); box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                #ai-loading-spinner { display: none; }
                #ai-result-container { display: none; }
              </style>
            `;
            const targetEl = tempDiv.querySelector(".container");
            let aiInner = targetEl ? targetEl.innerHTML : htmlText;

            // Map các ID từ ai.html gốc sang các ID tương thích với home.js
            aiInner = aiInner.replace(/id="expenseForm"/g, 'id="aiInputForm"');
            aiInner = aiInner.replace(/id="description"/g, 'id="ai-description"');
            aiInner = aiInner.replace(/id="userType"/g, 'id="ai-model-type"');
            aiInner = aiInner.replace(/id="loadingSpinner"/g, 'id="ai-loading-spinner"');
            aiInner = aiInner.replace(/id="resultContainer"/g, 'id="ai-result-container"');
            aiInner = aiInner.replace(/id="resAmount"/g, 'id="ai-res-amount"');
            aiInner = aiInner.replace(/id="resCategory"/g, 'id="ai-res-category"');
            aiInner = aiInner.replace(/id="aiConfidenceBar"/g, 'id="ai-confidence-bar"');
            aiInner = aiInner.replace(/id="aiConfidenceText"/g, 'id="ai-confidence-text"');
            aiInner = aiInner.replace(/id="methodText"/g, 'id="ai-method-text"');
            aiInner = aiInner.replace(/id="reviewSection"/g, 'id="ai-review-section"');
            aiInner = aiInner.replace(/id="suggestionTags"/g, 'id="ai-suggestion-tags"');
            aiInner = aiInner.replace(/onclick="saveTransaction\(\)"/g, 'onclick="saveAiTransaction()"');

            targetHtml += aiInner;
          } else {
            targetHtml = htmlText;
          }

          // Chèn HTML vào trang (và kích hoạt script nếu có)
          setInnerHTMLWithScripts(container, targetHtml);
        }

        // Gọi các hàm tải dữ liệu động tương ứng
        if (tabId === "transactions") {
          if (document.getElementById("transaction-table-body")) {
            loadTransactions();
          }
        } else if (tabId === "budgets") {
          if (document.getElementById("budget-detailed-list")) {
            loadBudgetsTab();
          }
        } else if (tabId === "ai") {
          loadAiHubTab();
        } else if (tabId === "settings") {
          loadProfileTab();
        }

      } catch (err) {
        console.error("Lỗi khi tải tab:", err);
        container.innerHTML = `<div class="alert alert-danger m-4"><i class="bi bi-exclamation-triangle-fill"></i> Lỗi: ${err.message}</div>`;
      }
    }, 150);
  }

  // Sử dụng Event Delegation để xử lý click chuyển tab nhanh từ các link và nút động
  document.addEventListener("click", (e) => {
    const link = e.target.closest("[data-tab]");
    if (link) {
      e.preventDefault();
      const tabId = link.getAttribute("data-tab");
      switchTab(tabId);
    }

    // Dynamic focus actions in topbar cta buttons
    if (e.target.closest("#btn-focus-budget")) {
      const amtInput = document.getElementById("budget-amount");
      if (amtInput) amtInput.focus();
    }
    if (e.target.closest("#btn-focus-ai-desc")) {
      const aiInput = document.getElementById("ai-description");
      if (aiInput) aiInput.focus();
    }
  });

  // --- 3. TẢI DANH MỤC (CATEGORIES) ---
  async function loadCategories() {
    try {
      const response = await fetch("/api/categories");
      if (!response.ok) throw new Error("Không thể lấy danh sách danh mục");
      globalCategories = await response.json();
      
      // Cập nhật dropdowns
      populateCategoryDropdowns();
    } catch (err) {
      console.error("Lỗi lấy danh mục:", err);
    }
  }

  function populateCategoryDropdowns() {
    const filterSelect = document.getElementById("tx-filter-category");
    const addSelect = document.getElementById("add-tx-category");
    const editSelect = document.getElementById("edit-tx-category");
    const budgetSelect = document.getElementById("budget-category-select");

    const categoryOptionsHtml = globalCategories
      .map(c => `<option value="${c.id}">${c.name}</option>`)
      .join("");

    if (filterSelect) {
      filterSelect.innerHTML = '<option value="">-- Danh mục --</option>' + categoryOptionsHtml;
    }
    if (addSelect) {
      addSelect.innerHTML = categoryOptionsHtml;
    }
    if (editSelect) {
      editSelect.innerHTML = categoryOptionsHtml;
    }
    if (budgetSelect) {
      budgetSelect.innerHTML = categoryOptionsHtml;
    }
  }

  // --- 4. TAB 1: TỔNG QUAN (HOME DATA) ---
  async function loadHomeData() {
    try {
      const response = await fetch(`/api/home-data?user_id=${queryUserId}`);
      if (!response.ok) throw new Error("Lỗi fetch home-data");
      const json = await response.json();
      if (!json.success || !json.data) throw new Error(json.message);

      const res = json.data;
      userRole = res.user.vaiTro;

      // Cập nhật Sidebar User info
      const nameEl = document.getElementById("user-name");
      if (nameEl) nameEl.innerText = res.user.hoTen;
      const emailEl = document.getElementById("user-email");
      if (emailEl) emailEl.innerText = res.user.email;
      const sidebarAvatar = document.getElementById("user-avatar");
      if (sidebarAvatar) {
        sidebarAvatar.innerText = res.user.hoTen.charAt(0).toUpperCase();
      }

      // Cập nhật Mobile Sidebar User info
      const mobNameEl = document.querySelector(".mobile-user-name");
      if (mobNameEl) mobNameEl.innerText = res.user.hoTen;
      const mobEmailEl = document.querySelector(".mobile-user-email");
      if (mobEmailEl) mobEmailEl.innerText = res.user.email;
      const mobSidebarAvatar = document.querySelector(".mobile-user-avatar");
      if (mobSidebarAvatar) {
        mobSidebarAvatar.innerText = res.user.hoTen.charAt(0).toUpperCase();
      }

      // Cập nhật Topbar Greeting và Subtext
      const topbarSubtext = document.getElementById("topbar-subtext");
      if (topbarSubtext && activeTab === "overview") {
        topbarSubtext.innerText = `Xin chào, ${res.user.hoTen}! Xem và phân tích tình hình thu chi, số dư hiện tại của tài khoản của bạn.`;
      }

      // Cập nhật Thẻ Thống Kê
      const balanceEl = document.getElementById("balance-amount");
      if (balanceEl) balanceEl.innerText = formatCurrency(res.stats.soDu);
      updateTrend("balance-trend", res.stats.soDuTrend);

      const incomeEl = document.getElementById("income-amount");
      if (incomeEl) incomeEl.innerText = formatCurrency(res.stats.thuNhapThang);
      updateTrend("income-trend", res.stats.thuNhapTrend);

      const expenseEl = document.getElementById("expense-amount");
      if (expenseEl) expenseEl.innerText = formatCurrency(res.stats.chiTieuThang);
      updateTrend("expense-trend", res.stats.chiTieuTrend);

      const progressEl = document.getElementById("saving-progress-percent");
      if (progressEl) progressEl.innerText = `${res.stats.tienDoTietKiem}%`;
      const savingDetail = document.getElementById("saving-progress-detail");
      if (savingDetail) {
        savingDetail.innerHTML = `<i class="bi bi-check-circle"></i>${formatCurrency(res.stats.tietKiemThucTe)} / ${formatCurrency(res.stats.tietKiemMucTieu)}`;
      }

      // Vẽ biểu đồ Thu chi
      renderHomeCharts(res.chartData);

      // Cập nhật danh sách giao dịch gần đây (Tab 1)
      renderRecentTransactions(res.giaoDichGanDay);

      // Cập nhật Top danh mục chi tiêu
      renderTopCategories(res.topDanhMucChiTieu);

      // Cập nhật Hạn mức ngân sách thu nhỏ
      renderBudgetWidget(res.nganSach);

      // Cập nhật AI Coach
      const coachInsightEl = document.getElementById("ai-coach-insight");
      if (coachInsightEl) coachInsightEl.innerText = res.aiCoach.insight;
      const coachDetailEl = document.getElementById("ai-coach-detail");
      if (coachDetailEl) coachDetailEl.innerText = res.aiCoach.detail;

    } catch (err) {
      console.error("Lỗi hiển thị trang chủ:", err);
    }
  }

  function renderHomeCharts(chartData) {
    const ctxIncome = document.getElementById("incomeChart");
    if (ctxIncome) {
      if (incomeChartInstance) incomeChartInstance.destroy();
      incomeChartInstance = new Chart(ctxIncome.getContext("2d"), {
        type: "bar",
        data: {
          labels: chartData.labels,
          datasets: [{
            label: "Thu nhập (đ)",
            data: chartData.thuNhap,
            backgroundColor: "#10b981",
            borderRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } }
        }
      });
    }

    const ctxExpense = document.getElementById("expenseChart");
    if (ctxExpense) {
      if (expenseChartInstance) expenseChartInstance.destroy();
      const ctx2d = ctxExpense.getContext("2d");
      const gradient = ctx2d.createLinearGradient(0, 0, 0, 200);
      gradient.addColorStop(0, "rgba(59, 130, 246, 0.35)");
      gradient.addColorStop(1, "rgba(59, 130, 246, 0)");

      expenseChartInstance = new Chart(ctx2d, {
        type: "line",
        data: {
          labels: chartData.labels,
          datasets: [{
            label: "Chi tiêu (đ)",
            data: chartData.chiTieu,
            borderColor: "#3b82f6",
            backgroundColor: gradient,
            fill: true,
            tension: 0.4,
            borderWidth: 2,
            pointRadius: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } }
        }
      });
    }
  }

  function renderRecentTransactions(list) {
    const container = document.getElementById("recent-transactions-list");
    if (!container) return;

    if (list.length === 0) {
      container.innerHTML = '<p class="text-center text-secondary py-3">Không có giao dịch gần đây</p>';
      return;
    }

    container.innerHTML = list.map(item => {
      const isThu = item.loai === "THU";
      const iconClass = isThu ? "transaction-icon income" : "transaction-icon";
      const amountClass = isThu ? "amount plus" : "amount minus";
      const sign = isThu ? "+" : "-";
      const icon = getCategoryIcon(item.tenDanhMuc);

      return `
        <div class="transaction-item">
          <div class="${iconClass}">
            <i class="bi ${icon}"></i>
          </div>
          <div>
            <h3>${item.moTa}</h3>
            <p>${isThu ? 'Thu nhập' : 'Chi tiêu'} · ${item.ngayGiaoDich}</p>
          </div>
          <strong class="${amountClass}">${sign}${formatCurrency(item.soTien)}</strong>
        </div>
      `;
    }).join("");
  }

  function renderTopCategories(list) {
    const container = document.getElementById("top-categories-list");
    if (!container) return;

    if (list.length === 0) {
      container.innerHTML = '<p class="text-center text-secondary py-3">Không có dữ liệu chi tiêu tháng này</p>';
      return;
    }

    container.innerHTML = list.map((item, index) => {
      return `
        <div class="category-row">
          <span>#${index + 1}</span>
          <div>
            <h3>${item.tenDanhMuc}</h3>
            <p>${item.tyLe}% tổng chi</p>
          </div>
          <strong>${formatCurrency(item.tongTien)}</strong>
        </div>
      `;
    }).join("");
  }

  function renderBudgetWidget(list) {
    const container = document.getElementById("budget-list");
    if (!container) return;

    if (list.length === 0) {
      container.innerHTML = '<p class="text-center text-secondary py-3">Không có hạn mức ngân sách</p>';
      return;
    }

    container.innerHTML = list.slice(0, 3).map(item => {
      const progressColor = item.tyLe > 100 ? "danger" : item.tyLe > 80 ? "warning" : "blue";
      return `
        <div class="budget-item">
          <div class="budget-top">
            <strong>${item.tenDanhMuc}</strong>
            <span>Đã dùng ${formatCurrency(item.daDung)} / ${formatCurrency(item.hanMuc)}</span>
          </div>
          <div class="progress" role="progressbar" aria-valuenow="${Math.min(item.tyLe, 100)}" aria-valuemin="0" aria-valuemax="100">
            <div class="progress-bar ${progressColor}" style="width: ${Math.min(item.tyLe, 100)}%"></div>
          </div>
        </div>
      `;
    }).join("");
  }

  // --- 5. TAB 2: QUẢN LÝ GIAO DỊCH (TRANSACTIONS CRUD) ---
  let transactionsData = [];

  async function loadTransactions() {
    const tableBody = document.getElementById("transaction-table-body");
    if (!tableBody) return;

    // Repopulate category select inside transaction tab filters
    populateCategoryDropdowns();

    // Attach search/filter listeners dynamically
    const filterBtn = document.getElementById("btn-tx-filter-apply");
    if (filterBtn) {
      filterBtn.onclick = handleFilterTransactions;
    }

    try {
      tableBody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-secondary">Đang tải danh sách giao dịch...</td></tr>';
      
      const response = await fetch("/api/transactions");
      if (!response.ok) throw new Error("Không thể tải giao dịch");
      
      transactionsData = await response.json();
      renderTransactionsTable(transactionsData);
    } catch (err) {
      tableBody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-danger">Lỗi: ${err.message}</td></tr>`;
    }
  }

  function renderTransactionsTable(list) {
    const tableBody = document.getElementById("transaction-table-body");
    if (!tableBody) return;

    if (list.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-secondary">Không tìm thấy giao dịch nào</td></tr>';
      return;
    }

    tableBody.innerHTML = list.map(t => {
      const isThu = t.type.toLowerCase() === "income" || t.type.toLowerCase() === "thu";
      const badgeClass = isThu ? "badge-income" : "badge-expense";
      const badgeText = isThu ? "Thu nhập" : "Chi tiêu";
      
      const category = globalCategories.find(c => c.id === t.category_id);
      const categoryName = category ? category.name : "Khác";
      
      // Định dạng ngày giao dịch
      let displayDate = "Chưa rõ";
      if (t.date) {
        const parts = t.date.split(" ")[0].split("-");
        if (parts.length === 3) displayDate = `${parts[2]}/${parts[1]}/${parts[0]}`;
        else displayDate = t.date.split(" ")[0];
      }

      return `
        <tr>
          <td>${displayDate}</td>
          <td class="fw-bold">${t.description || "Giao dịch không tên"}</td>
          <td><span class="badge bg-light text-dark border"><i class="bi ${getCategoryIcon(categoryName)} me-1"></i>${categoryName}</span></td>
          <td><span class="${badgeClass}">${badgeText}</span></td>
          <td class="text-end fw-black text-dark">${formatCurrency(t.amount)}</td>
          <td class="text-center">
            <div class="d-flex justify-content-center gap-2">
              <button class="btn btn-sm btn-ghost p-1" onclick="openEditModal(${t.id}, ${t.amount}, ${t.category_id}, '${t.type}', '${t.description}')">
                <i class="bi bi-pencil-square text-primary"></i>
              </button>
              <button class="btn btn-sm btn-ghost p-1" onclick="deleteTransaction(${t.id})">
                <i class="bi bi-trash3-fill text-danger"></i>
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join("");
  }

  // Chức năng lọc giao dịch
  async function handleFilterTransactions() {
    const typeEl = document.getElementById("tx-filter-type");
    const categoryIdEl = document.getElementById("tx-filter-category");
    const monthEl = document.getElementById("tx-filter-month");
    const searchEl = document.getElementById("tx-search-input");
    
    const type = typeEl ? typeEl.value : "";
    const categoryId = categoryIdEl ? categoryIdEl.value : "";
    const month = monthEl ? monthEl.value : "";
    const search = searchEl ? searchEl.value : "";

    let queryParams = new URLSearchParams();
    if (type) queryParams.append("type", type);
    if (categoryId) queryParams.append("category_id", categoryId);
    if (month) queryParams.append("month", month);
    queryParams.append("year", "2026");

    const tableBody = document.getElementById("transaction-table-body");
    if (!tableBody) return;
    tableBody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-secondary">Đang tải kết quả lọc...</td></tr>';

    try {
      const response = await fetch(`/api/transactions/filter?${queryParams.toString()}`);
      if (!response.ok) throw new Error("Lỗi khi lọc");
      let filtered = await response.json();

      if (search) {
        filtered = filtered.filter(t => t.description && t.description.toLowerCase().includes(search.toLowerCase()));
      }

      renderTransactionsTable(filtered);
    } catch (err) {
      tableBody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-danger">Lỗi: ${err.message}</td></tr>`;
    }
  }

  // --- HÀNH ĐỘNG XÓA GIAO DỊCH (Global click handler) ---
  window.deleteTransaction = async function(id) {
    if (!confirm("Bạn có chắc chắn muốn xóa giao dịch này không?")) return;
    try {
      const response = await fetch(`/api/transactions/${id}`, { method: "DELETE" });
      if (!response.ok) throw new Error("Lỗi khi xóa giao dịch");
      
      alert("Đã xóa giao dịch thành công!");
      if (activeTab === "transactions") loadTransactions();
      else loadHomeData();
    } catch (err) {
      alert("Lỗi: " + err.message);
    }
  };

  // --- HÀNH ĐỘNG THÊM GIAO DỊCH ---
  const addForm = document.getElementById("addTransactionForm");
  if (addForm) {
    addForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      
      const typeEl = document.querySelector('input[name="tx-type"]:checked');
      const amountEl = document.getElementById("add-tx-amount");
      const categoryIdEl = document.getElementById("add-tx-category");
      const descriptionEl = document.getElementById("add-tx-desc");

      const type = typeEl ? typeEl.value : "CHI";
      const amount = amountEl ? parseFloat(amountEl.value) : 0;
      const categoryId = categoryIdEl ? parseInt(categoryIdEl.value) : 1;
      const description = descriptionEl ? descriptionEl.value : "";

      try {
        const response = await fetch("/api/transactions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            amount: amount,
            type: type,
            category_id: categoryId,
            description: description
          })
        });

        if (!response.ok) throw new Error("Lỗi khi tạo giao dịch");

        // Ẩn modal và reload
        const modalEl = document.getElementById("addTransactionModal");
        if (modalEl) {
          const modal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
          modal.hide();
        }
        
        addForm.reset();
        alert("Ghi chép giao dịch thành công!");
        
        if (activeTab === "transactions") loadTransactions();
        else loadHomeData();
        
      } catch (err) {
        alert("Lỗi: " + err.message);
      }
    });
  }

  // --- HÀNH ĐỘNG SỬA GIAO DỊCH ---
  window.openEditModal = function(id, amount, categoryId, type, description) {
    const editIdEl = document.getElementById("edit-tx-id");
    if (editIdEl) editIdEl.value = id;
    const editAmountEl = document.getElementById("edit-tx-amount");
    if (editAmountEl) editAmountEl.value = amount;
    const editCatEl = document.getElementById("edit-tx-category");
    if (editCatEl) editCatEl.value = categoryId;
    const editDescEl = document.getElementById("edit-tx-desc");
    if (editDescEl) editDescEl.value = description;

    const isIncome = type.toLowerCase() === "income" || type.toLowerCase() === "thu";
    
    const thuRadio = document.getElementById("edit-tx-type-thu");
    const chiRadio = document.getElementById("edit-tx-type-chi");
    if (thuRadio) thuRadio.checked = isIncome;
    if (chiRadio) chiRadio.checked = !isIncome;

    const modalEl = document.getElementById("editTransactionModal");
    if (modalEl) {
      const modal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
      modal.show();
    }
  };

  const editForm = document.getElementById("editTransactionForm");
  if (editForm) {
    editForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      
      const idEl = document.getElementById("edit-tx-id");
      const typeEl = document.querySelector('input[name="edit-tx-type"]:checked');
      const amountEl = document.getElementById("edit-tx-amount");
      const categoryIdEl = document.getElementById("edit-tx-category");
      const descriptionEl = document.getElementById("edit-tx-desc");

      const id = idEl ? idEl.value : "";
      const type = typeEl ? typeEl.value : "CHI";
      const amount = amountEl ? parseFloat(amountEl.value) : 0;
      const categoryId = categoryIdEl ? parseInt(categoryIdEl.value) : 1;
      const description = descriptionEl ? descriptionEl.value : "";

      try {
        const response = await fetch(`/api/transactions/${id}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            amount: amount,
            type: type,
            category_id: categoryId,
            description: description
          })
        });

        if (!response.ok) throw new Error("Lỗi khi cập nhật giao dịch");

        const modalEl = document.getElementById("editTransactionModal");
        if (modalEl) {
          const modal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
          modal.hide();
        }
        
        alert("Cập nhật giao dịch thành công!");
        
        if (activeTab === "transactions") loadTransactions();
        else loadHomeData();
        
      } catch (err) {
        alert("Lỗi: " + err.message);
      }
    });
  }

  // --- 6. TAB 3: NGÂN SÁCH & DANH MỤC ---
  // --- 6. TAB 3: NGÂN SÁCH & DANH MỤC ---
  async function loadBudgetsTab() {
    const container = document.getElementById("budget-detailed-list");
    if (!container) return;

    // Repopulate categories select options
    populateCategoryDropdowns();

    // Attach event listeners dynamically
    const budgetForm = document.getElementById("setBudgetForm");
    if (budgetForm) {
      budgetForm.onsubmit = handleSetBudgetSubmit;
    }

    try {
      container.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-success" role="status"></div></div>';
      
      const response = await fetch(`/api/budget/check?user_id=${queryUserId}&month=6&year=2026`);
      if (!response.ok) throw new Error("Không thể tải hạn mức ngân sách");
      
      const list = await response.json();
      
      if (list.length === 0) {
        container.innerHTML = `
          <div class="budget-empty-state">
            <div class="budget-empty-icon"><i class="bi bi-piggy-bank"></i></div>
            <h4>Chưa có ngân sách nào</h4>
            <p>Hãy thiết lập hạn mức chi tiêu cho các danh mục ở form phía trên để bắt đầu quản lý ngân sách.</p>
          </div>
        `;
        document.getElementById("budget-total-amount").innerText = "0đ";
        document.getElementById("budget-total-spent").innerText = "0đ";
        document.getElementById("budget-total-remaining").innerText = "0đ";
        if (budgetPieChartInstance) budgetPieChartInstance.destroy();
        return;
      }

      // Biến tích lũy tổng quan
      let totalLimit = 0;
      let totalSpent = 0;

      // Mảng dữ liệu cho Pie Chart
      let chartLabels = [];
      let chartData = [];

      // Render danh sách chi tiết
      container.innerHTML = list.map((item, index) => {
        const category = globalCategories.find(c => c.id === item.category_id);
        const categoryName = category ? category.name : "Khác";
        const percent = item.limit > 0 ? (item.spent / item.limit) * 100 : 0.0;
        
        // Cộng dồn tổng số tiền
        totalLimit += item.limit;
        totalSpent += item.spent;

        // Đẩy thông tin vào cấu trúc biểu đồ hình tròn
        chartLabels.push(categoryName);
        chartData.push(item.limit);

        let statusClass = "safe";
        let statusText = "An toàn";
        let statusIcon = "bi-check-circle-fill";
        let progressClass = "budget-progress-safe";
        
        if (item.over) {
          statusClass = "over";
          statusText = "Vượt ngân sách";
          statusIcon = "bi-exclamation-triangle-fill";
          progressClass = "budget-progress-over";
        } else if (percent > 80) {
          statusClass = "warning";
          statusText = "Sắp chạm hạn mức";
          statusIcon = "bi-exclamation-circle-fill";
          progressClass = "budget-progress-warning";
        }

        const remaining = Math.max(0, item.limit - item.spent);

        return `
          <div class="budget-detail-card" style="animation-delay: ${index * 0.06}s">
            <div class="budget-detail-left">
              <div class="budget-detail-cat-icon">
                <i class="bi ${getCategoryIcon(categoryName)}"></i>
              </div>
              <div class="budget-detail-info">
                <h5 class="budget-detail-name">${categoryName}</h5>
                <span class="budget-detail-status ${statusClass}">
                  <i class="bi ${statusIcon}"></i> ${statusText}
                </span>
              </div>
            </div>
            <div class="budget-detail-right">
              <div class="budget-detail-amounts">
                <span class="budget-detail-spent">${formatCurrency(item.spent)}</span>
                <span class="budget-detail-limit">/ ${formatCurrency(item.limit)}</span>
              </div>
              <div class="budget-detail-progress-wrapper">
                <div class="budget-detail-progress">
                  <div class="budget-detail-progress-bar ${progressClass}" style="width: ${Math.min(percent, 100)}%"></div>
                </div>
                <span class="budget-detail-percent">${percent.toFixed(0)}%</span>
              </div>
              <span class="budget-detail-remaining">Còn lại: ${formatCurrency(remaining)}</span>
            </div>
          </div>
        `;
      }).join("");

      // Cập nhật 3 Thẻ Tổng quan phía trên đầu tab
      const remainingAmount = Math.max(0, totalLimit - totalSpent);
      document.getElementById("budget-total-amount").innerText = formatCurrency(totalLimit);
      document.getElementById("budget-total-spent").innerText = formatCurrency(totalSpent);
      document.getElementById("budget-total-remaining").innerText = formatCurrency(remainingAmount);

      // Khởi tạo/Cập nhật Pie Chart phân bổ ngân sách hạn mức
      renderBudgetPieChart(chartLabels, chartData);

    } catch (err) {
      container.innerHTML = `<p class="text-center text-danger py-5">Lỗi: ${err.message}</p>`;
    }
  }

  // Hàm vẽ biểu đồ tròn (Doughnut Chart) bằng Chart.js
  function renderBudgetPieChart(labels, data) {
    const ctxPie = document.getElementById("budgetPieChart");
    if (!ctxPie) return;

    if (budgetPieChartInstance) budgetPieChartInstance.destroy();

    budgetPieChartInstance = new Chart(ctxPie.getContext("2d"), {
      type: "doughnut",
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: [
            "#3b82f6", "#10b981", "#f59e0b", "#ef4444", 
            "#8b5cf6", "#ec4899", "#14b8a6", "#6366f1",
            "#f97316", "#06b6d4"
          ],
          borderWidth: 3,
          borderColor: "#ffffff",
          hoverBorderWidth: 4,
          hoverOffset: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "65%",
        plugins: {
          legend: {
            position: "right",
            labels: {
              boxWidth: 14,
              boxHeight: 14,
              borderRadius: 4,
              useBorderRadius: true,
              font: { size: 13, weight: 600 },
              padding: 14,
              color: "#334155"
            }
          },
          tooltip: {
            backgroundColor: "#0f172a",
            titleFont: { size: 13, weight: 700 },
            bodyFont: { size: 12 },
            padding: 12,
            cornerRadius: 12,
            callbacks: {
              label: function(context) {
                const value = context.raw || 0;
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                return ` ${context.label}: ${formatCurrency(value)} (${percentage}%)`;
              }
            }
          }
        }
      }
    });
  }

  // Hành động Lưu Hạn Mức Ngân Sách
  async function handleSetBudgetSubmit(e) {
    e.preventDefault();

    const categoryIdEl = document.getElementById("budget-category-select");
    const monthEl = document.getElementById("budget-month");
    const yearEl = document.getElementById("budget-year");
    const amountEl = document.getElementById("budget-amount");

    const categoryId = categoryIdEl ? parseInt(categoryIdEl.value) : 1;
    const month = monthEl ? parseInt(monthEl.value) : 6;
    const year = yearEl ? parseInt(yearEl.value) : 2026;
    const amount = amountEl ? parseFloat(amountEl.value) : 0;

    try {
      const response = await fetch("/api/budget", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: parseInt(queryUserId),
          category_id: categoryId,
          month: month,
          year: year,
          limit_amount: amount
        })
      });

      if (!response.ok) throw new Error("Lỗi khi thiết lập ngân sách");
      const res = await response.json();
      
      alert(res.message || "Đã lưu hạn mức ngân sách thành công!");
      const budgetForm = document.getElementById("setBudgetForm");
      if (budgetForm) budgetForm.reset();
      loadBudgetsTab();
    } catch (err) {
      alert("Lỗi: " + err.message);
    }
  }

  // Hành động Thêm Danh Mục mới
  async function handleCreateCategorySubmit(e) {
    e.preventDefault();

    const nameEl = document.getElementById("cat-name");
    const typeEl = document.querySelector('input[name="cat-type"]:checked');

    const name = nameEl ? nameEl.value : "";
    const type = typeEl ? typeEl.value : "CHI";

    try {
      const response = await fetch("/api/categories", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: name,
          type: type
        })
      });

      if (!response.ok) throw new Error("Lỗi khi thêm danh mục");
      
      alert("Thêm danh mục thành công!");
      const categoryForm = document.getElementById("createCategoryForm");
      if (categoryForm) categoryForm.reset();
      
      // Load lại danh mục
      await loadCategories();
      // Refill select options
      populateCategoryDropdowns();
    } catch (err) {
      alert("Lỗi: " + err.message);
    }
  }

  // --- 7. TAB 4: PHÂN TÍCH AI (AI HUB & FORECAST) ---
  function loadAiHubTab() {
    // Attach input form listener dynamically
    const aiForm = document.getElementById("aiInputForm");
    if (aiForm) {
      aiForm.onsubmit = handleAiFormSubmit;
    }

    loadForecastData();
    loadMoMTrendData();
    loadTimeSeriesData();
  }

  // AI Forecast
  async function loadForecastData() {
    const loader = document.getElementById("forecast-loader");
    const resultBox = document.getElementById("forecast-result");
    if (!loader || !resultBox) return;

    loader.classList.remove("d-none");
    resultBox.classList.add("d-none");

    try {
      const response = await fetch("/api/analytics/forecast");
      if (!response.ok) throw new Error("Lỗi fetch dự báo");
      const res = await response.json();

      if (res.status === "success") {
        const forecastAmtEl = document.getElementById("forecast-amount");
        if (forecastAmtEl) forecastAmtEl.innerText = formatCurrency(res.predicted_amount);
        const forecastMonthsEl = document.getElementById("forecast-months");
        if (forecastMonthsEl) forecastMonthsEl.innerText = res.historical_data_months || "0";
        const forecastMethodEl = document.getElementById("forecast-method");
        if (forecastMethodEl) forecastMethodEl.innerText = res.method || "Hồi quy tuyến tính";
        const forecastDiffEl = document.getElementById("forecast-diff");
        if (forecastDiffEl) forecastDiffEl.innerText = `Chênh lệch ${formatCurrency(res.difference_from_last_month)} so với tháng này`;
        
        const badge = document.getElementById("forecast-trend-badge");
        if (badge) {
          if (res.trend === "up") {
            badge.className = "badge bg-danger";
            badge.innerText = "Dự kiến tăng chi tiêu";
          } else if (res.trend === "down") {
            badge.className = "badge bg-success";
            badge.innerText = "Dự kiến giảm chi tiêu";
          } else {
            badge.className = "badge bg-secondary";
            badge.innerText = "Ổn định";
          }
        }

        loader.classList.add("d-none");
        resultBox.classList.remove("d-none");
      }
    } catch (err) {
      loader.innerHTML = `<p class="text-danger small"><i class="bi bi-exclamation-triangle-fill"></i> Không đủ dữ liệu lịch sử hoặc có lỗi xảy ra.</p>`;
    }
  }

  // AI MoM Analysis
  async function loadMoMTrendData() {
    const loader = document.getElementById("mom-loader");
    const resultBox = document.getElementById("mom-result");
    if (!loader || !resultBox) return;

    loader.classList.remove("d-none");
    resultBox.classList.add("d-none");

    try {
      const response = await fetch("/api/analytics/trend/mom");
      if (!response.ok) throw new Error("Lỗi tải xu hướng danh mục");
      const res = await response.json();

      if (res.status === "success" && res.data) {
        const data = res.data;
        
        // Insight
        const insightEl = document.getElementById("mom-insight");
        if (insightEl) {
          insightEl.innerHTML = `
            <div class="fw-bold mb-1"><i class="bi bi-stars text-success me-1"></i>Ý kiến của AI Coach:</div>
            <p class="mb-2 text-dark">${data.overall.insight}</p>
            <div class="small text-muted">${data.overall.warning}</div>
          `;
        }

        // Table breakdown
        const tableBody = document.getElementById("mom-table-body");
        if (tableBody) {
          if (data.category_breakdown.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" class="text-center text-secondary py-3">Chưa có đủ danh mục để đối sánh.</td></tr>';
          } else {
            tableBody.innerHTML = data.category_breakdown.map(cat => {
              const isUp = cat.trend === "tăng";
              const isDown = cat.trend === "giảm";
              const trendBadge = isUp 
                ? '<span class="badge bg-light-danger text-danger border rounded-pill"><i class="bi bi-arrow-up-right me-1"></i>Tăng</span>'
                : isDown 
                  ? '<span class="badge bg-light-success text-success border rounded-pill"><i class="bi bi-arrow-down-right me-1"></i>Giảm</span>'
                  : '<span class="badge bg-light text-secondary border rounded-pill">Không đổi</span>';

              const diffClass = cat.difference > 0 ? "text-danger" : cat.difference < 0 ? "text-success" : "text-muted";
              const diffSign = cat.difference > 0 ? "+" : "";

              return `
                <tr>
                  <td class="fw-bold"><i class="bi ${getCategoryIcon(cat.category)} text-secondary me-1"></i>${cat.category}</td>
                  <td>${formatCurrency(cat.prev_amount)}</td>
                  <td>${formatCurrency(cat.current_amount)}</td>
                  <td class="text-end fw-semibold ${diffClass}">${diffSign}${formatCurrency(cat.difference)} <small class="text-muted">(${cat.change_percentage}%)</small></td>
                  <td class="text-center">${trendBadge}</td>
                </tr>
              `;
            }).join("");
          }
        }

        loader.classList.add("d-none");
        resultBox.classList.remove("d-none");
      }
    } catch (err) {
      loader.innerHTML = `<p class="text-danger small"><i class="bi bi-exclamation-triangle-fill"></i> Lỗi: ${err.message}</p>`;
    }
  }

  // AI Timeseries Chart
  async function loadTimeSeriesData() {
    const loader = document.getElementById("timeseries-loader");
    const resultBox = document.getElementById("timeseries-result");
    if (!loader || !resultBox) return;

    loader.classList.remove("d-none");
    resultBox.classList.add("d-none");

    try {
      const response = await fetch("/api/analytics/trend/timeseries?window_size=3");
      if (!response.ok) throw new Error("Lỗi fetch chuỗi thời gian");
      const res = await response.json();

      if (res.status === "success" && res.chart_data) {
        const insightEl = document.getElementById("timeseries-insight");
        if (insightEl) {
          insightEl.innerHTML = `
            <i class="bi bi-lightbulb-fill text-warning me-1"></i> <strong>Đường xu hướng dài hạn:</strong> ${res.meta.insight}
          `;
        }

        const ctx = document.getElementById("timeSeriesChart");
        if (ctx) {
          if (timeSeriesChartInstance) timeSeriesChartInstance.destroy();
          
          timeSeriesChartInstance = new Chart(ctx.getContext("2d"), {
            data: {
              labels: res.chart_data.labels,
              datasets: [
                {
                  type: "line",
                  label: res.chart_data.datasets[1].label,
                  data: res.chart_data.datasets[1].data,
                  borderColor: "#10b981",
                  borderWidth: 3,
                  pointRadius: 4,
                  fill: false,
                  tension: 0.3
                },
                {
                  type: "bar",
                  label: res.chart_data.datasets[0].label,
                  data: res.chart_data.datasets[0].data,
                  backgroundColor: "rgba(59, 130, 246, 0.4)",
                  borderColor: "#3b82f6",
                  borderWidth: 1,
                  borderRadius: 6
                }
              ]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: { beginAtZero: true }
              }
            }
          });
        }

        loader.classList.add("d-none");
        resultBox.classList.remove("d-none");
      }
    } catch (err) {
      loader.innerHTML = `<p class="text-danger small"><i class="bi bi-exclamation-triangle-fill"></i> Không đủ số tháng dữ liệu chi tiêu để tính trung bình động (yêu cầu tối thiểu 3 tháng).</p>`;
    }
  }

  // --- TRỢ LÝ NHẬP LIỆU AI FORM SUBMIT ---
  async function handleAiFormSubmit(e) {
    e.preventDefault();

    const descEl = document.getElementById("ai-description");
    const modelTypeEl = document.getElementById("ai-model-type");

    const desc = descEl ? descEl.value : "";
    const modelType = modelTypeEl ? modelTypeEl.value : "PREMIUM";

    const spinner = document.getElementById("ai-loading-spinner");
    if (spinner) spinner.style.display = "block";
    
    const resBox = document.getElementById("ai-result-container");
    if (resBox) resBox.style.display = "none";

    try {
      const response = await fetch("/api/transactions/classify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          description: desc,
          user_type: modelType
        })
      });

      const result = await response.json();

      if (result.status === "success") {
        const data = result.data;

        const resAmtEl = document.getElementById("ai-res-amount");
        if (resAmtEl) resAmtEl.innerText = data.amount.toLocaleString("vi-VN") + " đ";
        const resCatEl = document.getElementById("ai-res-category");
        if (resCatEl) resCatEl.innerText = data.category;

        const confBar = document.getElementById("ai-confidence-bar");
        if (confBar) {
          confBar.style.width = data.confidence_score + "%";
          confBar.innerText = data.confidence_score + "%";

          if (data.confidence_score >= 80) {
            confBar.className = "progress-bar bg-success";
          } else if (data.confidence_score >= 50) {
            confBar.className = "progress-bar bg-warning";
          } else {
            confBar.className = "progress-bar bg-danger";
          }
        }

        const confTextEl = document.getElementById("ai-confidence-text");
        if (confTextEl) confTextEl.innerText = data.confidence_score + "%";
        const methodTextEl = document.getElementById("ai-method-text");
        if (methodTextEl) methodTextEl.innerText = data.classification_method;

        // Xử lý cờ needs_user_review
        const reviewSection = document.getElementById("ai-review-section");
        const suggestionTags = document.getElementById("ai-suggestion-tags");
        
        if (suggestionTags) {
          suggestionTags.innerHTML = "";

          if (data.needs_user_review && data.top_predictions) {
            if (reviewSection) reviewSection.style.display = "block";

            for (const [cat, prob] of Object.entries(data.top_predictions)) {
              const btn = document.createElement("span");
              btn.className = "badge bg-white text-dark border p-2 me-2 mb-2 suggestion-chip";
              btn.innerHTML = `${cat} <small class="text-muted">(${prob}%)</small>`;
              btn.onclick = () => {
                const resCatElInner = document.getElementById("ai-res-category");
                if (resCatElInner) resCatElInner.innerText = cat;
                if (confBar) {
                  confBar.style.width = "100%";
                  confBar.className = "progress-bar bg-success";
                  confBar.innerText = "100%";
                }
                const confTextElInner = document.getElementById("ai-confidence-text");
                if (confTextElInner) confTextElInner.innerText = "100% (Xác nhận bởi User)";
                if (reviewSection) reviewSection.style.display = "none";
              };
              suggestionTags.appendChild(btn);
            }
          } else {
            if (reviewSection) reviewSection.style.display = "none";
          }
        }

        if (spinner) spinner.style.display = "none";
        if (resBox) resBox.style.display = "block";

      } else {
        alert("Lỗi từ AI: " + result.message);
        if (spinner) spinner.style.display = "none";
      }

    } catch (err) {
      alert("Lỗi kết nối máy chủ phân loại AI.");
      if (spinner) spinner.style.display = "none";
    }
  }

  // Lưu giao dịch phân tích bởi AI vào Sổ chi tiêu thực (Global click handler)
  window.saveAiTransaction = async function() {
    const amountEl = document.getElementById("ai-res-amount");
    const categoryEl = document.getElementById("ai-res-category");
    const descEl = document.getElementById("ai-description");

    const amountText = amountEl ? amountEl.innerText.replace(/[^\d]/g, "") : "0";
    const amount = parseFloat(amountText);
    const catName = categoryEl ? categoryEl.innerText : "Khác";
    const desc = descEl ? descEl.value : "";

    // Tìm categoryId từ globalCategories
    const matchedCategory = globalCategories.find(c => c.name.toLowerCase() === catName.toLowerCase());
    
    // Nếu không tìm thấy, mặc định chọn danh mục đầu tiên (hoặc Khác)
    const categoryId = matchedCategory ? matchedCategory.id : (globalCategories.length > 0 ? globalCategories[0].id : 1);

    try {
      const response = await fetch("/api/transactions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          amount: amount,
          type: "CHI",
          category_id: categoryId,
          description: `[AI Assistant] ${desc}`
        })
      });

      if (!response.ok) throw new Error("Không thể lưu giao dịch");
      
      alert(`Đã lưu giao dịch ${formatCurrency(amount)} vào danh mục [${catName}] thành công!`);
      
      // Reset form AI
      const aiForm = document.getElementById("aiInputForm");
      if (aiForm) aiForm.reset();
      
      const resBox = document.getElementById("ai-result-container");
      if (resBox) resBox.style.display = "none";
    } catch (err) {
      alert("Lỗi khi lưu giao dịch: " + err.message);
    }
  };

  // --- 8. TAB 5: CÀI ĐẶT CÁ NHÂN & VIP ---
  async function loadProfileTab() {
    // 1. Gán sự kiện submit form cập nhật Profile qua AJAX
    const profileForm = document.querySelector('form[action*="/profile/update"]');
    if (profileForm) {
      profileForm.onsubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(profileForm);

        try {
          const resUpdate = await fetch(profileForm.getAttribute('action') || '/profile/update', {
            method: "POST",
            body: formData
          });
          if (resUpdate.ok) {
            alert("Cập nhật thông tin cá nhân thành công!");
            loadHomeData(); // Reload sidebar user info
            switchTab("settings"); // Reload lại tab settings
          } else {
            alert("Lỗi khi cập nhật thông tin!");
          }
        } catch (err) {
          alert("Lỗi kết nối: " + err.message);
        }
      };
    }

    // 2. Gán sự kiện submit form đổi mật khẩu qua AJAX
    const passwordForm = document.querySelector('form[action*="/profile/password"]');
    if (passwordForm) {
      passwordForm.onsubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(passwordForm);

        // Client side validation matching profile.html input names
        const newPassEl = passwordForm.querySelector('input[name="new_password"]');
        const confirmPassEl = passwordForm.querySelector('input[name="confirm_new_password"]');
        
        if (newPassEl && confirmPassEl && newPassEl.value !== confirmPassEl.value) {
          alert("Mật khẩu mới và mật khẩu xác nhận không khớp!");
          return;
        }

        try {
          const resPassword = await fetch(passwordForm.getAttribute('action') || '/profile/password', {
            method: "POST",
            body: formData
          });
          if (resPassword.ok) {
            alert("Đổi mật khẩu thành công!");
            passwordForm.reset();
          } else {
            alert("Lỗi khi đổi mật khẩu!");
          }
        } catch (err) {
          alert("Lỗi kết nối: " + err.message);
        }
      };
    }

    // 3. Gán sự kiện tự động upload avatar qua AJAX
    const avatarUpload = document.getElementById("avatarUpload");
    const avatarForm = document.getElementById("avatarForm");
    const avatarPreview = document.getElementById("avatarPreview");

    if (avatarUpload && avatarForm) {
      avatarUpload.onchange = async () => {
        if (avatarUpload.files.length > 0) {
          const file = avatarUpload.files[0];
          
          // Preview local
          const reader = new FileReader();
          reader.onload = function(e) { 
            if (avatarPreview) avatarPreview.src = e.target.result; 
          }
          reader.readAsDataURL(file);

          const formData = new FormData();
          formData.append("avatar", file);

          try {
            const resAvatar = await fetch(avatarForm.getAttribute('action') || '/profile/avatar', {
              method: "POST",
              body: formData
            });
            if (resAvatar.ok) {
              alert("Cập nhật ảnh đại diện thành công!");
              loadHomeData(); // Cập nhật sidebar avatar
            } else {
              alert("Lỗi tải ảnh đại diện!");
            }
          } catch (err) {
            alert("Lỗi upload: " + err.message);
          }
        }
      };
    }
  }

  // --- 9. BẮT ĐẦU KHỞI CHẠY (INITIALIZATION) ---
  (async function init() {
    await loadCategories();
    switchTab("overview");
  })();
});
