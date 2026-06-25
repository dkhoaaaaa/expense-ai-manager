// adminTransactions.js
// Quan ly giao dich toan he thong qua /admin/api/transactions.

let transactionSearchTimer = null;
let transactionCategoryLoaded = false;

// Initialize pagination state in AdminState
if (typeof AdminState !== "undefined" && !AdminState.transactionsPage) {
  AdminState.transactionsPage = 1;
} else if (typeof AdminState === "undefined") {
  window.AdminState = { transactionsPage: 1 };
}

function initTransactionsModule() {
  const searchInput = document.getElementById("searchTxnInput");
  const typeFilter = document.getElementById("filterTxnType");
  const categoryFilter = document.getElementById("filterTxnCategory");
  const fromDateInput = document.getElementById("txnFromDate");
  const toDateInput = document.getElementById("txnToDate");

  if (searchInput) {
    searchInput.addEventListener("input", () => {
      AdminState.transactionsPage = 1; // Reset to page 1 on search
      clearTimeout(transactionSearchTimer);
      transactionSearchTimer = setTimeout(populateTransactionsTable, 300);
    });
  }

  [typeFilter, categoryFilter, fromDateInput, toDateInput].forEach((element) => {
    if (element) {
      element.addEventListener("change", () => {
        AdminState.transactionsPage = 1; // Reset to page 1 on filter change
        populateTransactionsTable();
      });
    }
  });

  loadCategoryFilter();
}

async function populateTransactionsTable() {
  const tableBody = document.getElementById("transactionsTableBody");
  if (!tableBody) return;

  tableBody.innerHTML = `
    <tr>
      <td colspan="11" class="text-center text-muted py-4">Đang tải...</td>
    </tr>
  `;

  const params = new URLSearchParams({
    search: document.getElementById("searchTxnInput")?.value.trim() || "",
    type: document.getElementById("filterTxnType")?.value || "ALL",
    categoryId: document.getElementById("filterTxnCategory")?.value || "",
    fromDate: document.getElementById("txnFromDate")?.value || "",
    toDate: document.getElementById("txnToDate")?.value || "",
    page: AdminState.transactionsPage || 1,
    limit: 10,
  });

  const result = await fetchAdminTransactionApi(`/admin/api/transactions?${params.toString()}`);
  if (!result) return;

  if (!result.success) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="11" class="text-center text-danger py-4">${escapeTransactionHtml(result.message)}</td>
      </tr>
    `;
    renderTransactionStats({});
    renderTransactionsPagination(1, 1, 0, 10);
    return;
  }

  const transactions = result.data?.transactions || result.data?.items || [];
  const stats = result.data?.stats || result.data?.summary || {};
  const page = result.data?.page || 1;
  const totalPages = result.data?.totalPages || result.data?.total_pages || 1;
  const totalItems = result.data?.total || result.data?.total_items || 0;
  const limit = result.data?.limit || result.data?.per_page || 10;

  renderTransactionStats(stats);
  renderTransactionsTable(transactions);
  renderTransactionsPagination(page, totalPages, totalItems, limit);
}

function renderTransactionsTable(transactions) {
  const tableBody = document.getElementById("transactionsTableBody");
  if (!tableBody) return;

  if (!transactions.length) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="11" class="text-center text-muted py-4">
          Không có dữ liệu giao dịch để hiển thị.
        </td>
      </tr>
    `;
    return;
  }

  tableBody.innerHTML = transactions
    .map((transaction) => `
      <tr>
        <td class="font-monospace">#${transaction.id}</td>
        <td>${escapeTransactionHtml(transaction.email || "-")}</td>
        <td>${escapeTransactionHtml(transaction.hoTen || "-")}</td>
        <td>${escapeTransactionHtml(transaction.tenDanhMuc || "-")}</td>
        <td>
          <span class="badge ${getTransactionTypeClass(transaction.loai)}">
            ${escapeTransactionHtml(transaction.loai || "-")}
          </span>
        </td>
        <td class="fw-semibold">${formatCurrencyVnd(transaction.soTien)}</td>
        <td class="text-truncate" style="max-width: 220px">${escapeTransactionHtml(transaction.moTa || "-")}</td>
        <td>${formatDate(transaction.ngayGiaoDich)}</td>
        <td><span class="small font-monospace">${escapeTransactionHtml(transaction.phuongThucPhanLoai || "-")}</span></td>
        <td>${formatAiConfidence(transaction.doTinCay)}</td>
        <td class="text-end">
          <button
            type="button"
            class="btn btn-sm btn-outline-primary btn-transaction-detail"
            data-id="${transaction.id}"
            title="Xem chi tiết"
          >
            <i class="bi bi-eye"></i>
          </button>
        </td>
      </tr>
    `)
    .join("");

  document.querySelectorAll(".btn-transaction-detail").forEach((button) => {
    button.addEventListener("click", () => showTransactionDetail(button.dataset.id));
  });
}

function renderTransactionsPagination(page, totalPages, totalItems, limit) {
  const paginationEl = document.getElementById("transactionsPagination");
  const infoEl = document.getElementById("transactionsPaginationInfo");
  if (!paginationEl || !infoEl) return;

  if (totalItems === 0) {
    infoEl.innerText = "Hiển thị 0-0 trên 0 giao dịch";
    paginationEl.innerHTML = "";
    return;
  }

  const startItem = (page - 1) * limit + 1;
  const endItem = Math.min(page * limit, totalItems);
  infoEl.innerText = `Hiển thị ${startItem}-${endItem} trên ${totalItems} giao dịch`;

  let html = "";

  // Prev Button
  const prevDisabled = page === 1 ? "disabled" : "";
  html += `
    <li class="page-item ${prevDisabled}">
      <a class="page-link" href="#" data-page="${page - 1}" aria-label="Trước">
        <span aria-hidden="true">&laquo; Trước</span>
      </a>
    </li>
  `;

  // Number Buttons
  for (let i = 1; i <= totalPages; i++) {
    const activeClass = i === page ? "active" : "";
    html += `
      <li class="page-item ${activeClass}">
        <a class="page-link" href="#" data-page="${i}">${i}</a>
      </li>
    `;
  }

  // Next Button
  const nextDisabled = page === totalPages ? "disabled" : "";
  html += `
    <li class="page-item ${nextDisabled}">
      <a class="page-link" href="#" data-page="${page + 1}" aria-label="Sau">
        <span aria-hidden="true">Sau &raquo;</span>
      </a>
    </li>
  `;

  paginationEl.innerHTML = html;

  paginationEl.querySelectorAll(".page-link").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const targetPage = parseInt(link.dataset.page);
      if (targetPage && targetPage !== page && targetPage >= 1 && targetPage <= totalPages) {
        AdminState.transactionsPage = targetPage;
        populateTransactionsTable();
      }
    });
  });
}

function renderTransactionStats(stats) {
  setTransactionText("transactionTotalCount", stats.totalCount || 0);
  setTransactionText("transactionTotalIncome", formatCurrencyVnd(stats.totalIncome || 0));
  setTransactionText("transactionTotalExpense", formatCurrencyVnd(stats.totalExpense || 0));
  setTransactionText("transactionAiCount", stats.aiCount || 0);
}

async function loadCategoryFilter() {
  const categoryFilter = document.getElementById("filterTxnCategory");
  if (!categoryFilter || transactionCategoryLoaded) return;

  const result = await fetchAdminTransactionApi("/admin/api/transactions");
  if (!result || !result.success) return;

  const categories = result.data?.categories || [];
  categoryFilter.innerHTML = `<option value="ALL">Tất cả danh mục</option>`;

  categories.forEach((category) => {
    const option = document.createElement("option");
    option.value = category.id;
    option.textContent = `${category.tenDanhMuc} (${category.loai})`;
    categoryFilter.appendChild(option);
  });

  transactionCategoryLoaded = true;
}

function formatCurrencyVnd(amount) {
  return Number(amount || 0).toLocaleString("vi-VN", {
    style: "currency",
    currency: "VND",
    maximumFractionDigits: 0,
  });
}

function formatDate(dateString) {
  if (!dateString) return "-";

  const datePart = String(dateString).split("T")[0].split(" ")[0];
  const dateParts = datePart.split("-");
  if (dateParts.length === 3) {
    return `${dateParts[2]}/${dateParts[1]}/${dateParts[0]}`;
  }

  const date = new Date(dateString);
  if (Number.isNaN(date.getTime())) return dateString;

  return date.toLocaleDateString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

async function showTransactionDetail(id) {
  const result = await fetchAdminTransactionApi(`/admin/api/transactions/${id}`);
  if (!result) return;

  if (!result.success) {
    showHtmlModal("Lỗi", `<p class="mb-0">${escapeTransactionHtml(result.message || "Không lấy được chi tiết giao dịch")}</p>`);
    return;
  }

  const transaction = result.data;
  showDetailModal("Chi tiết giao dịch", {
    "ID giao dịch": "#" + transaction.id,
    "Email": transaction.email,
    "Họ tên": transaction.hoTen,
    "Danh mục": transaction.tenDanhMuc,
    "Loại": transaction.loai,
    "Số tiền": formatCurrencyVnd(transaction.soTien),
    "Mô tả": transaction.moTa,
    "Ngày giao dịch": formatDate(transaction.ngayGiaoDich),
    "Phân loại bởi": transaction.phuongThucPhanLoai,
    "Độ tin cậy AI": formatAiConfidenceText(transaction.doTinCay),
  });
}

async function fetchAdminTransactionApi(url, options = {}) {
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

function formatAiConfidence(value) {
  const percentText = formatAiConfidenceText(value);
  const percent = Number(value || 0);
  let className = "text-success";
  if (percent < 70) className = "text-danger";
  else if (percent < 90) className = "text-warning";

  return `<strong class="${className}">${percentText}</strong>`;
}

function formatAiConfidenceText(value) {
  if (value === null || value === undefined || value === "") return "-";
  return `${Math.round(Number(value || 0))}%`;
}

function getTransactionTypeClass(type) {
  if (type === "THU") return "bg-success-soft text-success";
  return "bg-danger-soft text-danger";
}

function setTransactionText(id, value) {
  const element = document.getElementById(id);
  if (element) element.innerText = value;
}

function escapeTransactionHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
