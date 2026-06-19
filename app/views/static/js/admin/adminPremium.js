// adminPremium.js
// Quan ly goi Premium qua /admin/api/premium.

let premiumSearchTimer = null;

function initPremiumModule() {
  const searchInput = document.getElementById("searchPremiumInput");
  const statusFilter = document.getElementById("filterPremiumStatus");

  if (searchInput) {
    searchInput.addEventListener("input", () => {
      clearTimeout(premiumSearchTimer);
      premiumSearchTimer = setTimeout(populatePremiumTable, 300);
    });
  }

  if (statusFilter) {
    statusFilter.addEventListener("change", populatePremiumTable);
  }
}

async function populatePremiumTable() {
  const tableBody = document.getElementById("premiumTableBody");
  if (!tableBody) return;

  tableBody.innerHTML = `
    <tr>
      <td colspan="8" class="text-center text-muted py-4">Đang tải...</td>
    </tr>
  `;

  const params = new URLSearchParams({
    search: document.getElementById("searchPremiumInput")?.value.trim() || "",
    status: document.getElementById("filterPremiumStatus")?.value || "ALL",
  });

  const result = await fetchAdminPremiumApi(`/admin/api/premium?${params.toString()}`);
  if (!result) return;

  if (!result.success) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="8" class="text-center text-danger py-4">${escapePremiumHtml(result.message)}</td>
      </tr>
    `;
    renderPremiumStats({});
    return;
  }

  const premiumList = result.data?.premiumList || result.data?.items || [];
  const stats = result.data?.stats || result.data?.summary || {};

  renderPremiumStats(stats);
  renderPremiumTable(premiumList);
}

function renderPremiumTable(premiumList) {
  const tableBody = document.getElementById("premiumTableBody");
  if (!tableBody) return;

  if (!premiumList.length) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="8" class="text-center text-muted py-4">
          Không có dữ liệu Premium để hiển thị.
        </td>
      </tr>
    `;
    return;
  }

  tableBody.innerHTML = premiumList
    .map((premium) => `
      <tr>
        <td class="font-monospace">#${premium.id}</td>
        <td>${escapePremiumHtml(premium.email || "-")}</td>
        <td>${escapePremiumHtml(premium.hoTen || "-")}</td>
        <td>${escapePremiumHtml(premium.tenGoi || "-")}</td>
        <td>
          <span class="badge ${getPremiumStatusClass(premium.trangThai)}">
            ${escapePremiumHtml(premium.trangThai || "-")}
          </span>
        </td>
        <td>${formatDate(premium.ngayBatDau)}</td>
        <td>${formatDate(premium.ngayKetThuc)}</td>
        <td class="text-end">
          <div class="btn-group btn-group-sm" role="group" aria-label="Hành động Premium">
            <button
              type="button"
              class="btn btn-outline-primary btn-premium-detail"
              data-id="${premium.id}"
              title="Xem chi tiết"
            >
              <i class="bi bi-eye"></i>
            </button>
            <button
              type="button"
              class="btn btn-outline-success btn-premium-extend"
              data-id="${premium.id}"
              title="Gia hạn Premium"
            >
              <i class="bi bi-arrow-repeat"></i>
            </button>
            <button
              type="button"
              class="btn btn-outline-danger btn-premium-cancel"
              data-id="${premium.id}"
              title="Hủy Premium"
            >
              <i class="bi bi-x-circle"></i>
            </button>
          </div>
        </td>
      </tr>
    `)
    .join("");

  document.querySelectorAll(".btn-premium-detail").forEach((button) => {
    button.addEventListener("click", () => showPremiumDetail(button.dataset.id));
  });

  document.querySelectorAll(".btn-premium-extend").forEach((button) => {
    button.addEventListener("click", () => extendPremium(button.dataset.id));
  });

  document.querySelectorAll(".btn-premium-cancel").forEach((button) => {
    button.addEventListener("click", () => cancelPremium(button.dataset.id));
  });
}

function renderPremiumStats(stats) {
  setPremiumText("premiumActiveCount", stats.activeCount || 0);
  setPremiumText("premiumExpiringCount", stats.expiringCount || stats.expiringSoonCount || 0);
  setPremiumText("premiumExpiredCount", stats.expiredCount || stats.inactiveCount || 0);
}

async function showPremiumDetail(id) {
  const result = await fetchAdminPremiumApi(`/admin/api/premium/${id}`);
  if (!result) return;

  if (!result.success) {
    showHtmlModal("Lỗi", `<p class="mb-0">${escapePremiumHtml(result.message || "Không lấy được chi tiết Premium")}</p>`);
    return;
  }

  const premium = result.data;
  showDetailModal("Chi tiết Premium", {
    "ID": "#" + premium.id,
    "Email": premium.email,
    "Họ tên": premium.hoTen,
    "Tên gói": premium.tenGoi,
    "Trạng thái": premium.trangThai,
    "Ngày bắt đầu": formatDate(premium.ngayBatDau),
    "Ngày kết thúc": formatDate(premium.ngayKetThuc),
  });
}

async function extendPremium(id) {
  showConfirmModal("Gia hạn Premium", "Bạn có muốn gia hạn gói Premium này thêm 1 tháng?", async () => {
    const result = await fetchAdminPremiumApi(`/admin/api/premium/${id}/extend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ months: 1 }),
    });
    if (!result) return;

    showToast(result.success ? "success" : "error", result.success ? "Thành công" : "Không thể xử lý", result.message);

    if (result.success) {
      populatePremiumTable();
    }
  });
}

async function cancelPremium(id) {
  showConfirmModal("Hủy Premium", "Bạn có chắc muốn hủy gói Premium này?", async () => {
    const result = await fetchAdminPremiumApi(`/admin/api/premium/${id}/cancel`, {
      method: "POST",
    });
    if (!result) return;

    showToast(result.success ? "success" : "error", result.success ? "Thành công" : "Không thể xử lý", result.message);

    if (result.success) {
      populatePremiumTable();
    }
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

async function fetchAdminPremiumApi(url, options = {}) {
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

function getPremiumStatusClass(status) {
  if (status === "ACTIVE") return "bg-success-soft text-success";
  if (status === "CANCELLED") return "bg-danger-soft text-danger";
  return "bg-warning-soft text-warning";
}

function setPremiumText(id, value) {
  const element = document.getElementById(id);
  if (element) element.innerText = value;
}

function escapePremiumHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
