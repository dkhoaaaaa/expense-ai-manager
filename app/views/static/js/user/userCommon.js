// userCommon.js
// Thư viện helper dùng chung cho frontend User: Toast notification, Logout & Confirm Modals

// Tự động chèn CSS của Toast vào trang nếu chưa tồn tại
function injectToastCSS() {
  if (document.getElementById("toast-dynamic-styles")) return;
  const style = document.createElement("style");
  style.id = "toast-dynamic-styles";
  style.innerHTML = `
    .toast-container-custom {
      position: fixed;
      top: 24px;
      right: 24px;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 12px;
      pointer-events: none;
    }
    .toast-notify {
      font-family: 'Be Vietnam Pro', 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      min-width: 320px;
      max-width: 420px;
      display: flex;
      align-items: flex-start;
      gap: 12px;
      padding: 16px;
      border-radius: 16px;
      background: #ffffff;
      box-shadow: 0 20px 45px rgba(15, 23, 42, 0.18);
      transform: translateX(120%) scale(0.9);
      opacity: 0;
      transition: 
        transform 0.45s cubic-bezier(0.34, 1.56, 0.64, 1),
        opacity 0.35s ease;
      position: relative;
      overflow: hidden;
      pointer-events: all;
      border-left: 4px solid transparent;
    }
    .toast-show {
      transform: translateX(0) scale(1);
      opacity: 1;
    }
    .toast-hide {
      transform: translateX(120%) scale(0.9);
      opacity: 0;
      transition: 
        transform 0.4s cubic-bezier(0.36, 0.07, 0.19, 0.97),
        opacity 0.3s ease;
    }
    .toast-icon-box {
      font-size: 22px;
      line-height: 1;
      flex-shrink: 0;
    }
    .toast-notify.toast-success { border-left-color: #16a34a; }
    .toast-notify.toast-success .toast-icon-box { color: #16a34a; }
    
    .toast-notify.toast-error { border-left-color: #dc2626; }
    .toast-notify.toast-error .toast-icon-box { color: #dc2626; }

    .toast-notify.toast-warning { border-left-color: #d97706; }
    .toast-notify.toast-warning .toast-icon-box { color: #d97706; }

    .toast-notify.toast-info { border-left-color: #2563eb; }
    .toast-notify.toast-info .toast-icon-box { color: #2563eb; }

    .toast-body-content {
      flex: 1;
    }
    .toast-title {
      margin: 0;
      font-weight: 700;
      font-size: 15px;
      color: #0f172a;
    }
    .toast-message {
      margin: 4px 0 0;
      font-size: 14px;
      color: #64748b;
      line-height: 1.4;
    }
    .toast-close-btn {
      border: none;
      background: transparent;
      color: #64748b;
      cursor: pointer;
      padding: 0;
      line-height: 1;
      font-size: 16px;
      transition: color 0.2s;
    }
    .toast-close-btn:hover {
      color: #0f172a;
    }
    .toast-progress-bar {
      position: absolute;
      left: 0;
      bottom: 0;
      height: 4px;
      width: 100%;
      animation-name: toastProgress;
      animation-timing-function: linear;
      animation-fill-mode: forwards;
    }
    .toast-success .toast-progress-bar { background: #16a34a; }
    .toast-error .toast-progress-bar { background: #dc2626; }
    .toast-warning .toast-progress-bar { background: #d97706; }
    .toast-info .toast-progress-bar { background: #2563eb; }

    @keyframes toastProgress {
      from { width: 100%; }
      to { width: 0%; }
    }
  `;
  document.head.appendChild(style);
}

// Đảm bảo phần tử container cho toast tồn tại trên DOM
function ensureToastContainer() {
  let container = document.getElementById("toastContainer");
  if (!container) {
    container = document.createElement("div");
    container.id = "toastContainer";
    container.className = "toast-container-custom";
    document.body.appendChild(container);
  }
  return container;
}

// Hàm hiển thị Toast Notification đa năng
function showToast(messageOrType, typeOrTitle, message, duration = 4000) {
  injectToastCSS();
  const container = ensureToastContainer();

  let type = "info";
  let title = "Thông báo";
  let msg = "";
  let dur = duration;

  const validTypes = ["success", "error", "warning", "info", "danger", "pending"];

  // Kiểm tra signature: showToast(type, title, message, duration)
  if (validTypes.includes(messageOrType) && typeof typeOrTitle === "string" && typeof message === "string") {
    type = messageOrType === "danger" ? "error" : messageOrType;
    title = typeOrTitle;
    msg = message;
    if (typeof duration === "number") dur = duration;
  } else {
    // Signature mới: showToast(message, type = "info")
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
    info: '<i class="bi bi-info-circle-fill"></i>',
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

// Hàm tắt toast
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

// Modal xác nhận Đăng xuất cho User và Admin (dùng chung)
function showLogoutConfirmModal(target) {
  // Xóa modal cũ nếu có trên DOM
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
    // Đưa modal vào trạng thái loading và tắt click đúp
    confirmBtn.disabled = true;
    cancelBtn.disabled = true;
    closeBtn.disabled = true;
    confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Đang xử lý...';

    // Xác định xem có phải là Admin logout hay User logout
    const isAdmin = window.location.pathname.startsWith("/admin") || (target && (target.id === "logoutBtn" || target.id === "drop-logout"));

    if (isAdmin) {
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
    } else {
      const logoutUrl = (target && target.getAttribute("href")) || "/auth/logout";
      setTimeout(() => {
        modal.hide();
        window.location.href = logoutUrl;
      }, 1000);
    }
  });

  // Tự động xóa modal khỏi DOM sau khi ẩn hoàn toàn
  modalEl.addEventListener("hidden.bs.modal", function () {
    modalEl.remove();
  });
}

// Modal xác nhận chung cho các tác vụ quan trọng của User (ví dụ: Xóa giao dịch)
function showConfirmModal(title, message, onConfirm) {
  const oldModal = document.getElementById("commonConfirmModal");
  if (oldModal) {
    const bsModal = bootstrap.Modal.getInstance(oldModal);
    if (bsModal) bsModal.hide();
    oldModal.remove();
  }

  const modalHtml = `
    <div class="modal fade" id="commonConfirmModal" tabindex="-1" aria-labelledby="commonConfirmModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow-lg" style="border-radius: 16px; overflow: hidden; font-family: 'Be Vietnam Pro', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
          <div class="modal-header border-bottom-0 pb-0" style="padding: 24px 24px 8px;">
            <h5 class="modal-title fw-bold text-dark d-flex align-items-center gap-2" id="commonConfirmModalLabel">
              <i class="bi bi-exclamation-triangle-fill text-warning"></i> ${title || "Xác nhận"}
            </h5>
            <button type="button" class="btn-close shadow-none" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body py-3" style="padding: 8px 24px 24px;">
            <p class="mb-0 text-secondary" style="font-size: 15px;">${message}</p>
          </div>
          <div class="modal-footer border-top-0 pt-0" style="padding: 8px 24px 24px; gap: 12px;">
            <button type="button" class="btn btn-light border fw-semibold px-4 py-2 rounded-pill shadow-sm" data-bs-dismiss="modal" id="commonConfirmCancelBtn" style="font-size: 14px; min-width: 100px;">Hủy</button>
            <button type="button" class="btn btn-primary fw-semibold px-4 py-2 rounded-pill shadow-sm d-flex align-items-center justify-content-center gap-2" id="commonConfirmOkBtn" style="font-size: 14px; min-width: 120px; background: #10b981; border: none;">
              Xác nhận
            </button>
          </div>
        </div>
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML("beforeend", modalHtml);

  const modalEl = document.getElementById("commonConfirmModal");
  const modal = new bootstrap.Modal(modalEl);
  modal.show();

  const confirmBtn = document.getElementById("commonConfirmOkBtn");
  const cancelBtn = document.getElementById("commonConfirmCancelBtn");
  const closeBtn = modalEl.querySelector(".btn-close");

  confirmBtn.addEventListener("click", function () {
    confirmBtn.disabled = true;
    cancelBtn.disabled = true;
    closeBtn.disabled = true;
    confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Đang xử lý...';

    if (typeof onConfirm === "function") {
      Promise.resolve(onConfirm()).finally(() => {
        modal.hide();
      });
    } else {
      modal.hide();
    }
  });

  modalEl.addEventListener("hidden.bs.modal", function () {
    modalEl.remove();
  });
}

// Tự động chặn hành động click logout mặc định và hiển thị modal xác nhận cho User
document.addEventListener("DOMContentLoaded", function () {
  document.addEventListener("click", function (e) {
    const logoutTarget = e.target.closest('a[href*="/logout"], a[href*="/auth/logout"], .logout-btn, #logout-btn, #logoutBtn, #drop-logout');
    if (logoutTarget) {
      e.preventDefault();
      showLogoutConfirmModal(logoutTarget);
    }
  });
});
