// adminChatbot.js
// Quan ly lich su tin nhan chatbot qua /admin/api/chatbot/logs.

let chatbotSearchTimer = null;

function initChatbotModule() {
  const searchInput = document.getElementById("searchChatbotInput");
  const senderFilter = document.getElementById("filterChatbotSender");
  const fromDateInput = document.getElementById("chatbotFromDate");
  const toDateInput = document.getElementById("chatbotToDate");

  if (searchInput) {
    searchInput.addEventListener("input", () => {
      clearTimeout(chatbotSearchTimer);
      chatbotSearchTimer = setTimeout(populateChatbotLogsTable, 300);
    });
  }

  [senderFilter, fromDateInput, toDateInput].forEach((element) => {
    if (element) element.addEventListener("change", populateChatbotLogsTable);
  });
}

async function populateChatbotLogsTable() {
  const tableBody = document.getElementById("chatbotLogsTableBody");
  if (!tableBody) return;

  tableBody.innerHTML = `
    <tr>
      <td colspan="7" class="text-center text-muted py-4">Đang tải...</td>
    </tr>
  `;

  const params = new URLSearchParams({
    search: document.getElementById("searchChatbotInput")?.value.trim() || "",
    sender: document.getElementById("filterChatbotSender")?.value || "ALL",
    fromDate: document.getElementById("chatbotFromDate")?.value || "",
    toDate: document.getElementById("chatbotToDate")?.value || "",
  });

  try {
    const result = await fetchAdminChatbotApi(`/admin/api/chatbot/logs?${params.toString()}`);
    if (!result) return;

    if (!result.success) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="7" class="text-center text-danger py-4">
            ${escapeChatbotHtml(result.message || "Không thể tải chatbot logs.")}
          </td>
        </tr>
      `;
      return;
    }

    renderChatbotLogsTable(result.data?.logs || result.data?.items || []);
  } catch (error) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="7" class="text-center text-danger py-4">
          ${escapeChatbotHtml(error.message || "Không thể tải chatbot logs.")}
        </td>
      </tr>
    `;
  }
}

function renderChatbotLogsTable(logs) {
  const tableBody = document.getElementById("chatbotLogsTableBody");
  if (!tableBody) return;

  if (!logs.length) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="7" class="text-center text-muted py-4">
          Không có dữ liệu chatbot để hiển thị.
        </td>
      </tr>
    `;
    return;
  }

  tableBody.innerHTML = logs
    .map((log) => {
      const sender = log.sender || log.nguoiGui;
      return `
        <tr>
          <td class="font-monospace">#${log.id}</td>
          <td>${escapeChatbotHtml(log.email || "-")}</td>
          <td>${escapeChatbotHtml(log.fullName || log.hoTen || "-")}</td>
          <td>${renderChatbotSenderBadge(sender)}</td>
          <td class="text-truncate" style="max-width: 360px">
            ${escapeChatbotHtml(log.content || log.noiDung || "-")}
          </td>
          <td>${formatDateTime(log.createdAt || log.ngayTao)}</td>
          <td class="text-end">
            <button
              type="button"
              class="btn btn-sm btn-outline-primary btn-chatbot-detail"
              data-id="${log.id}"
              title="Xem chi tiết"
            >
              <i class="bi bi-eye"></i>
            </button>
          </td>
        </tr>
      `;
    })
    .join("");

  document.querySelectorAll(".btn-chatbot-detail").forEach((button) => {
    button.addEventListener("click", () => viewChatbotLogDetail(button.dataset.id));
  });
}

async function viewChatbotLogDetail(id) {
  const result = await fetchAdminChatbotApi(`/admin/api/chatbot/logs/${id}`);
  if (!result) return;

  if (!result.success) {
    showHtmlModal("Lỗi", `<p class="mb-0">${escapeChatbotHtml(result.message || "Không lấy được chi tiết chatbot log")}</p>`);
    return;
  }

  const log = result.data;
  showDetailModal("Chi tiết chatbot log", {
    "ID": "#" + log.id,
    "Email": log.email,
    "Họ tên": log.fullName || log.hoTen,
    "Người gửi": log.sender || log.nguoiGui,
    "Nội dung": log.content || log.noiDung,
    "Thời gian": formatDateTime(log.createdAt || log.ngayTao),
  });
}

function formatDateTime(dateString) {
  if (!dateString) return "-";

  const date = new Date(String(dateString).replace(" ", "T"));
  if (Number.isNaN(date.getTime())) return dateString;

  return date.toLocaleString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

async function fetchAdminChatbotApi(url, options = {}) {
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

function renderChatbotSenderBadge(sender) {
  if (sender === "USER") {
    return '<span class="badge bg-blue-soft text-primary">USER</span>';
  }

  return '<span class="badge bg-success-soft text-success">BOT</span>';
}

function escapeChatbotHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
