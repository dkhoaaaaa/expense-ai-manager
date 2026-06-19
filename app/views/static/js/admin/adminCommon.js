// adminCommon.js
// Dùng chung: session, toast, apiRequest. Không chứa logic riêng của từng tab.

const AdminState = {
  token: localStorage.getItem("adminAccessToken"),
  dashboardData: null,
  charts: {},
  currentTheme: localStorage.getItem("adminTheme") || "light",
};

function requireAdminToken() {
  if (!AdminState.token) {
    window.location.href = "/admin/login";
    return false;
  }

  return true;
}

function saveAdminSession(accessToken, admin) {
  localStorage.setItem("adminAccessToken", accessToken);
  localStorage.setItem("adminInfo", JSON.stringify(admin));
  AdminState.token = accessToken;
}

function clearAdminSession() {
  localStorage.removeItem("adminAccessToken");
  localStorage.removeItem("adminInfo");
  AdminState.token = null;
}

function redirectToAdminLogin(delay = 0) {
  setTimeout(() => {
    clearAdminSession();
    window.location.href = "/admin/login";
  }, delay);
}

function handleUnauthorized(result) {
  showToast("error", "Phiên hết hạn", result?.message || "Vui lòng đăng nhập lại");
  redirectToAdminLogin(2000);
}


// adminToast.js
// Toast notification góc phải màn hình

function showToast(type, title, message, duration = 4000) {
  const container = document.getElementById("toastContainer");

  if (!container) {
    console.warn("Không tìm thấy #toastContainer");
    return;
  }

  const icon =
    type === "success"
      ? '<i class="bi bi-check-circle-fill"></i>'
      : '<i class="bi bi-x-circle-fill"></i>';

  const id =
    "toast_" + Date.now() + "_" + Math.random().toString(36).slice(2, 6);

  const toast = document.createElement("div");
  toast.id = id;
  toast.className = `toast-notify toast-${type}`;
  toast.innerHTML = `
    <div class="toast-icon-box">${icon}</div>
    <div class="toast-body-content">
      <p class="toast-title">${title}</p>
      <p class="toast-message">${message}</p>
    </div>
    <button class="toast-close-btn" onclick="dismissToast('${id}')" title="Đóng">
      <i class="bi bi-x-lg"></i>
    </button>
    <div class="toast-progress-bar" style="animation-duration: ${duration}ms;"></div>
  `;

  container.appendChild(toast);

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      toast.classList.add("toast-show");
    });
  });

  toast._autoClose = setTimeout(() => dismissToast(id), duration);
}

function dismissToast(id) {
  const toast = document.getElementById(id);
  if (!toast) return;

  clearTimeout(toast._autoClose);

  toast.classList.remove("toast-show");
  toast.classList.add("toast-hide");

  setTimeout(() => {
    if (toast.parentNode) toast.parentNode.removeChild(toast);
  }, 400);
}


// Fetch dùng chung, chỉ tự gắn token và xử lý 401.
async function apiRequest(url, options = {}) {
  const headers = options.headers || {};

  const response = await fetch(url, {
    ...options,
    headers: {
      ...headers,
      Authorization: "Bearer " + AdminState.token,
    },
  });

  const result = await response.json();

  if (response.status === 401) {
    handleUnauthorized(result);
    return null;
  }

  return { response, result };
}

function formatVnd(value) {
  const amount = Number(value || 0);
  return amount.toLocaleString("vi-VN") + "đ";
}

function formatAdminDate(value) {
  if (!value) return "-";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return date.toLocaleDateString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

function closeCommonModal() {
  const modalElement = document.getElementById("commonDetailModal");
  if (!modalElement) return;

  const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
  modal.hide();
}

function showDetailModal(title, data) {
  const rows = Object.entries(data || {})
    .map(([label, value]) => {
      const displayValue = formatModalValue(label, value);
      return `
        <div class="row g-0 border-bottom py-2">
          <div class="col-5 col-md-4 text-muted fw-semibold">${escapeModalHtml(label)}</div>
          <div class="col-7 col-md-8 text-break">${displayValue}</div>
        </div>
      `;
    })
    .join("");

  showHtmlModal(title, `<div class="detail-modal-kv">${rows || '<p class="text-muted mb-0">Không có dữ liệu.</p>'}</div>`);
}

function showHtmlModal(title, htmlContent) {
  const titleElement = document.getElementById("commonDetailModalTitle");
  const bodyElement = document.getElementById("commonDetailModalBody");
  const footerElement = document.getElementById("commonDetailModalFooter");
  const modalElement = document.getElementById("commonDetailModal");

  if (!titleElement || !bodyElement || !footerElement || !modalElement) return;

  titleElement.innerText = title || "Chi tiết";
  bodyElement.innerHTML = htmlContent || "";
  footerElement.innerHTML = `
    <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
      Đóng
    </button>
  `;

  bootstrap.Modal.getOrCreateInstance(modalElement).show();
}

function showConfirmModal(title, message, onConfirm) {
  const titleElement = document.getElementById("commonDetailModalTitle");
  const bodyElement = document.getElementById("commonDetailModalBody");
  const footerElement = document.getElementById("commonDetailModalFooter");
  const modalElement = document.getElementById("commonDetailModal");

  if (!titleElement || !bodyElement || !footerElement || !modalElement) return;

  titleElement.innerText = title || "Xác nhận";
  bodyElement.innerHTML = `<p class="mb-0">${escapeModalHtml(message || "Bạn có chắc muốn tiếp tục?")}</p>`;
  footerElement.innerHTML = `
    <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
      Hủy
    </button>
    <button type="button" class="btn btn-primary-gradient" id="commonDetailConfirmBtn">
      Xác nhận
    </button>
  `;

  const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
  modal.show();

  const confirmButton = document.getElementById("commonDetailConfirmBtn");
  if (confirmButton) {
    confirmButton.addEventListener(
      "click",
      () => {
        modal.hide();
        if (typeof onConfirm === "function") onConfirm();
      },
      { once: true }
    );
  }
}

function formatModalValue(label, value) {
  if (value === null || value === undefined || value === "") return "-";

  const stringValue = String(value);
  const normalizedLabel = String(label || "").toLowerCase();

  if (isModalStatusValue(stringValue)) {
    return renderStatusBadge(stringValue);
  }

  if (normalizedLabel.includes("ngày") || normalizedLabel.includes("date")) {
    return escapeModalHtml(formatAdminDate(stringValue));
  }

  return escapeModalHtml(stringValue);
}

function isModalStatusValue(value) {
  return [
    "SUCCESS",
    "PENDING",
    "FAILED",
    "ACTIVE",
    "INACTIVE",
    "CANCELLED",
    "BANNED",
    "EXPIRED",
    "USER",
    "PREMIUM",
    "ADMIN",
    "THU",
    "CHI",
  ].includes(value);
}

function renderStatusBadge(status) {
  const classMap = {
    SUCCESS: "bg-success-soft text-success",
    ACTIVE: "bg-success-soft text-success",
    THU: "bg-success-soft text-success",
    PENDING: "bg-warning-soft text-warning",
    EXPIRED: "bg-warning-soft text-warning",
    FAILED: "bg-danger-soft text-danger",
    BANNED: "bg-danger-soft text-danger",
    CHI: "bg-danger-soft text-danger",
    INACTIVE: "bg-secondary text-light",
    CANCELLED: "bg-secondary text-light",
    USER: "bg-blue-soft text-primary",
    PREMIUM: "bg-yellow-soft text-warning",
    ADMIN: "bg-purple-soft text-purple",
  };

  return `<span class="badge ${classMap[status] || "bg-secondary text-light"}">${escapeModalHtml(status)}</span>`;
}

function escapeModalHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
