// adminUsers.js
// Quan ly nguoi dung qua /admin/api/users.

let usersSearchTimer = null;

// Initialize pagination state in AdminState
if (typeof AdminState !== "undefined" && !AdminState.usersPage) {
  AdminState.usersPage = 1;
} else if (typeof AdminState === "undefined") {
  window.AdminState = { usersPage: 1 };
}

function initUsersModule() {
  const searchInput = document.getElementById("searchUsersInput");
  const roleFilter = document.getElementById("filterUsersRole");
  const statusFilter = document.getElementById("filterUsersStatus");

  if (searchInput) {
    searchInput.addEventListener("input", () => {
      AdminState.usersPage = 1; // Reset to page 1 on search
      clearTimeout(usersSearchTimer);
      usersSearchTimer = setTimeout(populateUsersTable, 300);
    });
  }

  [roleFilter, statusFilter].forEach((element) => {
    if (element) {
      element.addEventListener("change", () => {
        AdminState.usersPage = 1; // Reset to page 1 on filter change
        populateUsersTable();
      });
    }
  });
}

async function populateUsersTable() {
  const tableBody = document.getElementById("usersTableBody");
  if (!tableBody) return;

  tableBody.innerHTML = `
    <tr>
      <td colspan="7" class="text-center text-muted py-4">Đang tải...</td>
    </tr>
  `;

  const params = new URLSearchParams({
    search: document.getElementById("searchUsersInput")?.value.trim() || "",
    role: document.getElementById("filterUsersRole")?.value || "ALL",
    status: document.getElementById("filterUsersStatus")?.value || "ALL",
    page: AdminState.usersPage || 1,
    per_page: 5,
  });

  const result = await fetchAdminUserApi(`/admin/api/users?${params.toString()}`);
  if (!result) return;

  if (!result.success) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="7" class="text-center text-danger py-4">${escapeUserHtml(result.message)}</td>
      </tr>
    `;
    renderUserStats({});
    renderUsersPagination(1, 1, 0, 5);
    return;
  }

  const users = result.data?.users || result.data?.items || [];
  const stats = result.data?.stats || result.data?.summary || {};
  const page = result.data?.page || 1;
  const totalPages = result.data?.total_pages || 1;
  const totalItems = result.data?.total_items || 0;
  const perPage = result.data?.per_page || 5;

  renderUserStats(stats);
  renderUsersTable(users);
  renderUsersPagination(page, totalPages, totalItems, perPage);
}

function renderUsersTable(users) {
  const tableBody = document.getElementById("usersTableBody");
  if (!tableBody) return;

  if (!users.length) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="7" class="text-center text-muted py-4">
          Không có dữ liệu người dùng để hiển thị.
        </td>
      </tr>
    `;
    return;
  }

  tableBody.innerHTML = users
    .map((user) => `
      <tr>
        <td class="font-monospace">#${user.id}</td>
        <td>${escapeUserHtml(user.email || "-")}</td>
        <td>${escapeUserHtml(user.hoTen || "-")}</td>
        <td>
          ${renderUserRoleBadge(user.vaiTro)}
        </td>
        <td>
          <span class="badge ${getUserStatusClass(user.trangThai)}">
            ${escapeUserHtml(user.trangThai || "-")}
          </span>
        </td>
        <td>${formatDate(user.ngayTao)}</td>
        <td class="text-end">
          ${renderUserActionButtons(user)}
        </td>
      </tr>
    `)
    .join("");

  document.querySelectorAll(".btn-user-detail").forEach((button) => {
    button.addEventListener("click", () => showUserDetail(button.dataset.id));
  });

  document.querySelectorAll(".btn-ban-user").forEach((button) => {
    button.addEventListener("click", () => banUser(button.dataset.id));
  });

  document.querySelectorAll(".btn-unban-user").forEach((button) => {
    button.addEventListener("click", () => unbanUser(button.dataset.id));
  });
}

function renderUserRoleBadge(role) {
  const classMap = {
    USER: "bg-blue-soft text-primary",
    PREMIUM: "bg-yellow-soft text-warning fw-bold",
    ADMIN: "bg-purple-soft text-purple fw-bold",
  };
  const badgeClass = classMap[role] || "bg-secondary text-light";
  return `<span class="badge ${badgeClass}">${escapeUserHtml(role || "USER")}</span>`;
}

function renderUsersPagination(page, totalPages, totalItems, perPage) {
  const paginationEl = document.getElementById("usersPagination");
  const infoEl = document.getElementById("usersPaginationInfo");
  if (!paginationEl || !infoEl) return;

  if (totalItems === 0) {
    infoEl.innerText = "Hiển thị 0-0 trên 0 người dùng";
    paginationEl.innerHTML = "";
    return;
  }

  const startItem = (page - 1) * perPage + 1;
  const endItem = Math.min(page * perPage, totalItems);
  infoEl.innerText = `Hiển thị ${startItem}-${endItem} trên ${totalItems} người dùng`;

  let html = "";

  // Prev Button
  const prevDisabled = page === 1 ? "disabled" : "";
  html += `
    <li class="page-item ${prevDisabled}">
      <a class="page-link" href="#" data-page="${page - 1}" aria-label="Previous">
        <span aria-hidden="true">&laquo;</span>
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
      <a class="page-link" href="#" data-page="${page + 1}" aria-label="Next">
        <span aria-hidden="true">&raquo;</span>
      </a>
    </li>
  `;

  paginationEl.innerHTML = html;

  paginationEl.querySelectorAll(".page-link").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const targetPage = parseInt(link.dataset.page);
      if (targetPage && targetPage !== page && targetPage >= 1 && targetPage <= totalPages) {
        AdminState.usersPage = targetPage;
        populateUsersTable();
      }
    });
  });
}

function renderUserStats(stats) {
  setUserText("userTotalCount", stats.totalCount || 0);
  setUserText("normalUserCount", stats.normalUserCount || 0);
  setUserText("premiumUserCount", stats.premiumUserCount || 0);
  setUserText("bannedUserCount", stats.bannedUserCount || 0);
}

async function showUserDetail(id) {
  const result = await fetchAdminUserApi(`/admin/api/users/${id}`);
  if (!result) return;

  if (!result.success) {
    showHtmlModal("Lỗi", `<p class="mb-0">${escapeUserHtml(result.message || "Không lấy được chi tiết người dùng")}</p>`);
    return;
  }

  const user = result.data;
  showDetailModal("Chi tiết người dùng", {
    "ID": "#" + user.id,
    "Email": user.email,
    "Họ tên": user.hoTen,
    "Vai trò": user.vaiTro,
    "Trạng thái": user.trangThai,
    "Ngày tạo": formatDate(user.ngayTao),
  });
}

async function banUser(id) {
  showConfirmModal("Khóa tài khoản", "Bạn có chắc muốn khóa tài khoản này?", async () => {
    const result = await fetchAdminUserApi(`/admin/api/users/${id}/ban`, {
      method: "POST",
    });
    if (!result) return;

    showToast(result.success ? "success" : "error", result.success ? "Thành công" : "Không thể xử lý", result.message);

    if (result.success) {
      populateUsersTable();
    }
  });
}

async function unbanUser(id) {
  showConfirmModal("Mở khóa tài khoản", "Bạn có chắc muốn mở khóa tài khoản này?", async () => {
    const result = await fetchAdminUserApi(`/admin/api/users/${id}/unban`, {
      method: "POST",
    });
    if (!result) return;

    showToast(result.success ? "success" : "error", result.success ? "Thành công" : "Không thể xử lý", result.message);

    if (result.success) {
      populateUsersTable();
    }
  });
}

async function changeUserRole(id, role) {
  const result = await fetchAdminUserApi(`/admin/api/users/${id}/change-role`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ role }),
  });
  if (!result) return;

  showToast(result.success ? "success" : "error", result.success ? "Thành công" : "Không thể xử lý", result.message);

  if (result.success) {
    populateUsersTable();
  }
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

async function fetchAdminUserApi(url, options = {}) {
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

function renderRoleOption(role, currentRole) {
  const selected = role === currentRole ? "selected" : "";
  return `<option value="${role}" ${selected}>${role}</option>`;
}

function renderUserActionButtons(user) {
  const detailButton = `
    <button type="button" class="btn btn-outline-primary btn-action-custom btn-user-detail" data-id="${user.id}" title="Xem chi tiết">
      <i class="bi bi-eye"></i>
    </button>
  `;

  if (user.trangThai === "BANNED") {
    return `
      <div class="btn-group btn-group-sm" role="group" aria-label="Hành động người dùng">
        ${detailButton}
        <button type="button" class="btn btn-outline-success btn-action-custom btn-unban-user" data-id="${user.id}" title="Mở khóa">
          <i class="bi bi-check-circle"></i>
        </button>
      </div>
    `;
  }

  return `
    <div class="btn-group btn-group-sm" role="group" aria-label="Hành động người dùng">
      ${detailButton}
      <button type="button" class="btn btn-outline-danger btn-action-custom btn-ban-user" data-id="${user.id}" title="Khóa">
        <i class="bi bi-slash-circle"></i>
      </button>
    </div>
  `;
}

function getUserStatusClass(status) {
  if (status === "ACTIVE") return "bg-success-soft text-success";
  return "bg-danger-soft text-danger";
}

function setUserText(id, value) {
  const element = document.getElementById(id);
  if (element) element.innerText = value;
}

function escapeUserHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
