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

function injectToastCSS() {
  if (document.getElementById("toast-dynamic-styles")) return;
  const style = document.createElement("style");
  style.id = "toast-dynamic-styles";
  style.innerHTML = `
    .toast-notify {
      font-family: 'Be Vietnam Pro', 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
      transform: translateX(120%) scale(0.9) !important;
      opacity: 0 !important;
      transition: 
        transform 0.45s cubic-bezier(0.34, 1.56, 0.64, 1) !important,
        opacity 0.35s ease !important;
    }
    .toast-notify.toast-show {
      transform: translateX(0) scale(1) !important;
      opacity: 1 !important;
    }
    .toast-notify.toast-hide {
      transform: translateX(120%) scale(0.9) !important;
      opacity: 0 !important;
      transition: 
        transform 0.4s cubic-bezier(0.36, 0.07, 0.19, 0.97) !important,
        opacity 0.3s ease !important;
    }

    #commonDetailModal .modal-content, 
    #logoutConfirmModal .modal-content,
    .modal-content {
      font-family: 'Be Vietnam Pro', 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }
    
    .toast-notify.toast-warning { border-left-color: #d97706 !important; }
    .toast-notify.toast-warning .toast-icon-box { background: #fef3c7 !important; color: #b45309 !important; }
    .toast-notify.toast-warning .toast-title { color: #b45309 !important; }
    .toast-notify.toast-warning .toast-progress-bar { background: #d97706 !important; }

    .toast-notify.toast-info { border-left-color: #2563eb !important; }
    .toast-notify.toast-info .toast-icon-box { background: #dbeafe !important; color: #1d4ed8 !important; }
    .toast-notify.toast-info .toast-title { color: #1d4ed8 !important; }
    .toast-notify.toast-info .toast-progress-bar { background: #2563eb !important; }
  `;
  document.head.appendChild(style);
}

function showToast(messageOrType, typeOrTitle, message, duration = 4000) {
  injectToastCSS();
  let container = document.getElementById("toastContainer");
  if (!container) {
    container = document.createElement("div");
    container.id = "toastContainer";
    container.className = "toast-container-custom";
    document.body.appendChild(container);
  }

  let type = "info";
  let title = "Thông báo";
  let msg = "";
  let dur = duration;

  const validTypes = ["success", "error", "warning", "info", "danger", "pending"];

  if (validTypes.includes(messageOrType) && typeof typeOrTitle === "string" && typeof message === "string") {
    type = messageOrType === "danger" ? "error" : messageOrType;
    title = typeOrTitle;
    msg = message;
    if (typeof duration === "number") dur = duration;
  } else {
    msg = messageOrType;
    type = typeOrTitle || "info";
    if (type === "danger") type = "error";

    if (type === "success") title = "Thành công";
    else if (type === "error") title = "Lỗi";
    else if (type === "warning") title = "Cảnh báo";
    else title = "Thông báo";
  }

  const iconMap = {
    success: '<i class="bi bi-check-circle-fill"></i>',
    error: '<i class="bi bi-x-circle-fill"></i>',
    warning: '<i class="bi bi-exclamation-triangle-fill"></i>',
    info: '<i class="bi bi-info-circle-fill"></i>'
  };

  const icon = iconMap[type] || iconMap.info;
  const id = "toast_" + Date.now() + "_" + Math.random().toString(36).slice(2, 6);

  const toast = document.createElement("div");
  toast.id = id;
  toast.className = `toast-notify toast-${type}`;
  toast.innerHTML = `
    <div class="toast-icon-box">${icon}</div>
    <div class="toast-body-content">
      <p class="toast-title">${title}</p>
      <p class="toast-message">${msg}</p>
    </div>
    <button class="toast-close-btn" onclick="dismissToast('${id}')" title="Đóng">
      <i class="bi bi-x-lg"></i>
    </button>
    <div class="toast-progress-bar" style="animation-duration: ${dur}ms;"></div>
  `;

  container.appendChild(toast);

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      toast.classList.add("toast-show");
    });
  });

  toast._autoClose = setTimeout(() => dismissToast(id), dur);
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

// Modal xác nhận Đăng xuất cho Admin (dùng chung logic với User)
function showLogoutConfirmModal(target) {
  const oldModal = document.getElementById("logoutConfirmModal");
  if (oldModal) {
    const bsModal = bootstrap.Modal.getInstance(oldModal);
    if (bsModal) bsModal.hide();
    oldModal.remove();
  }

  const modalHtml = `
    <div class="modal fade" id="logoutConfirmModal" tabindex="-1" aria-labelledby="logoutConfirmModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow-lg" style="border-radius: 16px; overflow: hidden; font-family: 'Be Vietnam Pro', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
          <div class="modal-header border-bottom-0 pb-0" style="padding: 24px 24px 8px;">
            <h5 class="modal-title fw-bold text-dark d-flex align-items-center gap-2" id="logoutConfirmModalLabel">
              <i class="bi bi-box-arrow-right text-danger"></i> Xác nhận đăng xuất
            </h5>
            <button type="button" class="btn-close shadow-none" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body py-3" style="padding: 8px 24px 24px;">
            <p class="mb-0 text-secondary" style="font-size: 15px;">Bạn có chắc chắn muốn đăng xuất khỏi hệ thống không?</p>
          </div>
          <div class="modal-footer border-top-0 pt-0" style="padding: 8px 24px 24px; gap: 12px;">
            <button type="button" class="btn btn-light border fw-semibold px-4 py-2 rounded-pill shadow-sm" data-bs-dismiss="modal" id="logoutCancelBtn" style="font-size: 14px; min-width: 100px;">Hủy</button>
            <button type="button" class="btn btn-danger fw-semibold px-4 py-2 rounded-pill shadow-sm d-flex align-items-center justify-content-center gap-2" id="logoutConfirmBtn" style="font-size: 14px; min-width: 120px; background-color: #dc3545; border-color: #dc3545;">
              Đăng xuất
            </button>
          </div>
        </div>
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML("beforeend", modalHtml);

  const modalEl = document.getElementById("logoutConfirmModal");
  const modal = new bootstrap.Modal(modalEl);
  modal.show();

  const confirmBtn = document.getElementById("logoutConfirmBtn");
  const cancelBtn = document.getElementById("logoutCancelBtn");
  const closeBtn = modalEl.querySelector(".btn-close");

  confirmBtn.addEventListener("click", function () {
    confirmBtn.disabled = true;
    cancelBtn.disabled = true;
    closeBtn.disabled = true;
    confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Đang xử lý...';

    if (typeof clearAdminSession === "function") {
      clearAdminSession();
    } else {
      localStorage.removeItem("adminAccessToken");
      localStorage.removeItem("adminInfo");
    }
    setTimeout(() => {
      modal.hide();
      window.location.href = "/admin/login";
    }, 1000);
  });

  modalEl.addEventListener("hidden.bs.modal", function () {
    modalEl.remove();
  });
}
