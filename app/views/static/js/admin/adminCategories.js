// adminCategories.js
// Quan ly danh muc thu/chi qua /admin/api/categories.

let categorySearchTimer = null;
let categoryBootstrapModal = null;

function initCategoriesModule() {
  const searchInput = document.getElementById("searchCategoryInput");
  const typeFilter = document.getElementById("filterCategoryType");
  const statusFilter = document.getElementById("filterCategoryStatus");
  const openButton = document.getElementById("btnOpenCategoryModal");
  const form = document.getElementById("categoryForm");

  if (searchInput) {
    searchInput.addEventListener("input", () => {
      clearTimeout(categorySearchTimer);
      categorySearchTimer = setTimeout(populateCategoriesTable, 300);
    });
  }

  [typeFilter, statusFilter].forEach((element) => {
    if (element) element.addEventListener("change", populateCategoriesTable);
  });

  if (openButton) {
    openButton.addEventListener("click", openCreateCategoryModal);
  }

  if (form) {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      saveCategory();
    });
  }
}

async function populateCategoriesTable() {
  const tableBody = document.getElementById("categoriesTableBody");
  if (!tableBody) return;

  tableBody.innerHTML = `
    <tr>
      <td colspan="7" class="text-center text-muted py-4">Đang tải...</td>
    </tr>
  `;

  const params = new URLSearchParams({
    search: document.getElementById("searchCategoryInput")?.value.trim() || "",
    type: document.getElementById("filterCategoryType")?.value || "ALL",
    status: document.getElementById("filterCategoryStatus")?.value || "ALL",
  });

  try {
    const result = await fetchAdminCategoryApi(`/admin/api/categories?${params.toString()}`);
    if (!result) return;

    if (!result.success) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="7" class="text-center text-danger py-4">
            ${escapeCategoryHtml(result.message || "Không thể tải danh mục.")}
          </td>
        </tr>
      `;
      return;
    }

    renderCategoriesTable(result.data?.categories || []);
  } catch (error) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="7" class="text-center text-danger py-4">
          ${escapeCategoryHtml(error.message || "Không thể tải danh mục.")}
        </td>
      </tr>
    `;
    showToast("error", "Lỗi API", error.message || "Không thể tải danh mục.");
  }
}

function renderCategoriesTable(categories) {
  const tableBody = document.getElementById("categoriesTableBody");
  if (!tableBody) return;

  if (!categories.length) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="7" class="text-center text-muted py-4">
          Không có dữ liệu danh mục để hiển thị.
        </td>
      </tr>
    `;
    return;
  }

  tableBody.innerHTML = categories
    .map((category) => {
      const type = category.type || category.loai;
      const status = category.status || category.trangThai;
      const transactionCount = Number(category.transactionCount || 0);

      return `
        <tr>
          <td class="font-monospace">#${category.id}</td>
          <td class="fw-semibold">${escapeCategoryHtml(category.name || category.tenDanhMuc || "-")}</td>
          <td>${renderCategoryTypeBadge(type)}</td>
          <td class="text-truncate" style="max-width: 320px">
            ${escapeCategoryHtml(category.keywordAi || category.keywordAI || "-")}
          </td>
          <td>${renderCategoryStatusBadge(status)}</td>
          <td>${transactionCount}</td>
          <td class="text-end">
            <div class="btn-group btn-group-sm" role="group" aria-label="Hành động danh mục">
              <button
                type="button"
                class="btn btn-outline-primary btn-category-edit"
                data-id="${category.id}"
                title="Sửa danh mục"
              >
                <i class="bi bi-pencil"></i>
              </button>
              <button
                type="button"
                class="btn ${status === "ACTIVE" ? "btn-outline-warning" : "btn-outline-success"} btn-category-toggle"
                data-id="${category.id}"
                title="Bật/tắt danh mục"
              >
                <i class="bi ${status === "ACTIVE" ? "bi-toggle-on" : "bi-toggle-off"}"></i>
              </button>
            </div>
          </td>
        </tr>
      `;
    })
    .join("");

  document.querySelectorAll(".btn-category-edit").forEach((button) => {
    button.addEventListener("click", () => openEditCategoryModal(button.dataset.id));
  });

  document.querySelectorAll(".btn-category-toggle").forEach((button) => {
    button.addEventListener("click", () => toggleCategoryStatus(button.dataset.id));
  });
}

function openCreateCategoryModal() {
  resetCategoryForm();
  setCategoryModalTitle("Thêm danh mục");
  getCategoryModal().show();
}

async function openEditCategoryModal(id) {
  try {
    const result = await fetchAdminCategoryApi(`/admin/api/categories/${id}`);
    if (!result) return;

    if (!result.success) {
      showHtmlModal("Lỗi", `<p class="mb-0">${escapeCategoryHtml(result.message || "Không thể tải danh mục")}</p>`);
      return;
    }

    const category = result.data;
    document.getElementById("categoryIdInput").value = category.id;
    document.getElementById("categoryNameInput").value = category.name || category.tenDanhMuc || "";
    document.getElementById("categoryTypeInput").value = category.type || category.loai || "CHI";
    document.getElementById("categoryKeywordAiInput").value =
      category.keywordAi || category.keywordAI || "";

    setCategoryModalTitle("Sửa danh mục");
    getCategoryModal().show();
  } catch (error) {
    showHtmlModal("Lỗi", `<p class="mb-0">${escapeCategoryHtml(error.message || "Không thể tải danh mục")}</p>`);
  }
}

async function saveCategory() {
  const categoryId = document.getElementById("categoryIdInput")?.value || "";
  const data = {
    name: document.getElementById("categoryNameInput")?.value.trim() || "",
    type: document.getElementById("categoryTypeInput")?.value || "CHI",
    keywordAi: document.getElementById("categoryKeywordAiInput")?.value.trim() || "",
  };

  if (!data.name) {
    showHtmlModal("Thiếu thông tin", "<p class=\"mb-0\">Tên danh mục không được trống.</p>");
    return;
  }

  const url = categoryId ? `/admin/api/categories/${categoryId}` : "/admin/api/categories";
  const method = categoryId ? "PATCH" : "POST";

  try {
    const result = await fetchAdminCategoryApi(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!result) return;

    showToast(
      result.success ? "success" : "error",
      result.success ? "Thành công" : "Không thể xử lý",
      result.message
    );

    if (result.success) {
      getCategoryModal().hide();
      populateCategoriesTable();
    }
  } catch (error) {
    showHtmlModal("Lỗi", `<p class="mb-0">${escapeCategoryHtml(error.message || "Không thể lưu danh mục")}</p>`);
  }
}

async function toggleCategoryStatus(id) {
  showConfirmModal("Bật/tắt danh mục", "Bạn có chắc muốn bật/tắt danh mục này?", async () => {
    try {
      const result = await fetchAdminCategoryApi(`/admin/api/categories/${id}/toggle-status`, {
        method: "PATCH",
      });
      if (!result) return;

      showToast(
        result.success ? "success" : "error",
        result.success ? "Thành công" : "Không thể xử lý",
        result.message
      );

      if (result.success) {
        populateCategoriesTable();
      }
    } catch (error) {
      showHtmlModal("Lỗi", `<p class="mb-0">${escapeCategoryHtml(error.message || "Không thể cập nhật trạng thái")}</p>`);
    }
  });
}

async function fetchAdminCategoryApi(url, options = {}) {
  const token = localStorage.getItem("adminAccessToken");
  const headers = options.headers || {};

  const response = await fetch(url, {
    ...options,
    headers: {
      ...headers,
      Authorization: `Bearer ${token}`,
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

function getCategoryModal() {
  const modalElement = document.getElementById("categoryModal");
  if (!categoryBootstrapModal) {
    categoryBootstrapModal = new bootstrap.Modal(modalElement);
  }

  return categoryBootstrapModal;
}

function resetCategoryForm() {
  document.getElementById("categoryForm")?.reset();
  document.getElementById("categoryIdInput").value = "";
  document.getElementById("categoryTypeInput").value = "CHI";
}

function setCategoryModalTitle(title) {
  const titleElement = document.getElementById("categoryModalTitle");
  if (titleElement) titleElement.innerText = title;
}

function renderCategoryTypeBadge(type) {
  if (type === "THU") {
    return '<span class="badge bg-success-soft text-success">Thu</span>';
  }

  return '<span class="badge bg-danger-soft text-danger">Chi</span>';
}

function renderCategoryStatusBadge(status) {
  if (status === "ACTIVE") {
    return '<span class="badge bg-success-soft text-success">ACTIVE</span>';
  }

  return '<span class="badge bg-secondary text-light">INACTIVE</span>';
}

function escapeCategoryHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
