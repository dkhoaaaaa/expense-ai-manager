// adminPayments.js
// Quan ly danh sach thanh toan Premium qua /admin/api/payments.

let paymentSearchTimer = null;

function initPaymentsModule() {
  const searchInput = document.getElementById("searchPaymentsInput");
  const statusFilter = document.getElementById("filterPaymentStatus");
  const fromDateInput = document.getElementById("paymentFromDate");
  const toDateInput = document.getElementById("paymentToDate");

  if (searchInput) {
    searchInput.addEventListener("input", () => {
      clearTimeout(paymentSearchTimer);
      paymentSearchTimer = setTimeout(populatePaymentsTable, 300);
    });
  }

  [statusFilter, fromDateInput, toDateInput].forEach((element) => {
    if (element) element.addEventListener("change", populatePaymentsTable);
  });
}

async function populatePaymentsTable() {
  const tableBody = document.getElementById("paymentsTableBody");
  if (!tableBody) return;

  tableBody.innerHTML = `
    <tr>
      <td colspan="8" class="text-center text-muted py-4">Đang tải...</td>
    </tr>
  `;

  const params = new URLSearchParams({
    search: document.getElementById("searchPaymentsInput")?.value.trim() || "",
    status: document.getElementById("filterPaymentStatus")?.value || "ALL",
    fromDate: document.getElementById("paymentFromDate")?.value || "",
    toDate: document.getElementById("paymentToDate")?.value || "",
  });

  const result = await fetchAdminPaymentApi(`/admin/api/payments?${params.toString()}`);
  if (!result) return;

  if (!result.success) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="8" class="text-center text-danger py-4">${escapeHtml(result.message)}</td>
      </tr>
    `;
    renderPaymentStats({});
    return;
  }

  const payments = result.data?.payments || result.data?.items || [];
  const stats = result.data?.stats || result.data?.summary || {};

  renderPaymentStats(stats);
  renderPaymentsTable(payments);
}

function renderPaymentsTable(payments) {
  const tableBody = document.getElementById("paymentsTableBody");
  if (!tableBody) return;

  if (!payments.length) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="8" class="text-center text-muted py-4">
          Không có dữ liệu thanh toán để hiển thị.
        </td>
      </tr>
    `;
    return;
  }

  tableBody.innerHTML = payments
    .map((payment) => {
      const paymentDate = payment.ngayThanhToan || payment.ngayTao;
      return `
        <tr>
          <td class="font-monospace">${escapeHtml(payment.maGiaoDich || "#" + payment.id)}</td>
          <td>${escapeHtml(payment.email || "-")}</td>
          <td>${escapeHtml(payment.hoTen || "-")}</td>
          <td class="fw-semibold">${formatCurrencyVnd(payment.soTien)}</td>
          <td>${escapeHtml(payment.phuongThucThanhToan || "-")}</td>
          <td>
            <span class="badge ${getPaymentStatusClass(payment.trangThaiThanhToan)}">
              ${escapeHtml(payment.trangThaiThanhToan || "-")}
            </span>
          </td>
          <td>${formatDate(paymentDate)}</td>
          <td class="text-end">
            <button
              type="button"
              class="btn btn-sm btn-outline-primary btn-payment-detail"
              data-id="${payment.id}"
              title="Xem chi tiet"
            >
              <i class="bi bi-eye"></i>
            </button>
          </td>
        </tr>
      `;
    })
    .join("");

  document.querySelectorAll(".btn-payment-detail").forEach((button) => {
    button.addEventListener("click", () => showPaymentDetail(button.dataset.id));
  });
}

function renderPaymentStats(stats) {
  setPaymentText("paymentRevenueTotal", formatCurrencyVnd(stats.totalRevenue || 0));
  setPaymentText("paymentSuccessCount", stats.successCount || 0);
  setPaymentText("paymentPendingCount", stats.pendingCount || 0);
  setPaymentText("paymentFailedCount", stats.failedCount || 0);
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

async function showPaymentDetail(paymentId) {
  const result = await fetchAdminPaymentApi(`/admin/api/payments/${paymentId}`);
  if (!result) return;

  if (!result.success) {
    showHtmlModal("Lỗi", `<p class="mb-0">${escapeHtml(result.message || "Không lấy được chi tiết thanh toán")}</p>`);
    return;
  }

  const payment = result.data;
  showDetailModal("Chi tiết thanh toán", {
    "Mã giao dịch": payment.maGiaoDich || "#" + payment.id,
    "Email": payment.email,
    "Họ tên": payment.hoTen,
    "Gói": payment.tenGoi,
    "Số tiền": formatCurrencyVnd(payment.soTien),
    "Phương thức": payment.phuongThucThanhToan,
    "Trạng thái": payment.trangThaiThanhToan,
    "Ngày thanh toán": formatDate(payment.ngayThanhToan || payment.ngayTao),
  });
}

async function fetchAdminPaymentApi(url) {
  const token = localStorage.getItem("adminAccessToken");

  const response = await fetch(url, {
    headers: {
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

function getPaymentStatusClass(status) {
  if (status === "SUCCESS") return "bg-success-soft text-success";
  if (status === "FAILED") return "bg-danger-soft text-danger";
  return "bg-warning-soft text-warning";
}

function setPaymentText(id, value) {
  const element = document.getElementById(id);
  if (element) element.innerText = value;
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
