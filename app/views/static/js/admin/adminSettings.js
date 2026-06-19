// adminSettings.js
// Load profile, cập nhật thông tin cá nhân, upload avatar, đổi mật khẩu

async function fetchAdminProfile() {
  try {
    const apiResult = await apiRequest("/admin/api/profile");
    if (!apiResult) return;

    const { result } = apiResult;

    if (result.success && result.admin) {
      const admin = result.admin;

      updateAdminUI(admin.hoTen, admin.avatar);
      fillAdminProfileForm(admin);
    }
  } catch (error) {
    console.error("Lỗi fetch thông tin admin:", error);
  }
}

function updateAdminUI(hoTen, avatar) {
  const displayName = hoTen || "Admin";

  const adminNameElements = document.querySelectorAll(
    "#adminName, #dropdownAdminName",
  );
  adminNameElements.forEach((el) => (el.textContent = displayName));

  const greetingAdminName = document.getElementById("greetingAdminName");
  if (greetingAdminName) {
    greetingAdminName.textContent = displayName;
  }

  const avatarLetter = displayName.charAt(0).toUpperCase();
  const avatarElements = document.querySelectorAll(
    "#adminAvatarLetter, #topbarAdminAvatar, #dropdownAvatarLetter, #settingsAvatarPreview",
  );

  avatarElements.forEach((el) => {
    if (avatar) {
      el.innerHTML = `<img src="${avatar}" alt="Avatar">`;
    } else {
      el.innerHTML = avatarLetter;
    }
  });
}

function fillAdminProfileForm(admin) {
  const nameProfile = document.getElementById("adminFullNameInput");
  const emailProfile = document.getElementById("adminEmailInput");
  const sdtProfile = document.getElementById("adminPhoneInput");
  const ngaySinhProfile = document.getElementById("adminBirthdayInput");
  const vaiTroProfile = document.getElementById("adminRoleInput");

  if (nameProfile) nameProfile.value = admin.hoTen || "Admin";
  if (emailProfile) emailProfile.value = admin.email || "";
  if (sdtProfile) sdtProfile.value = admin.sdt || "";
  if (ngaySinhProfile) ngaySinhProfile.value = admin.ngaySinh || "";
  if (vaiTroProfile) vaiTroProfile.value = admin.vaiTro || "Chưa cập nhật";
}

function validateAdminProfileForm(hoTen, sdt, ngaySinh) {
  if (!hoTen) {
    return "Họ tên không được để trống";
  }

  if (!/^\d{10}$/.test(sdt)) {
    return "Số điện thoại phải đủ 10 số và chỉ được chứa số";
  }

  if (ngaySinh) {
    const birthDate = new Date(ngaySinh);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (birthDate > today) {
      return "Ngày sinh không được lớn hơn ngày hiện tại";
    }
  }

  return null;
}

function initUpdateProfileForm() {
  const updateProfileForm = document.getElementById("adminProfileForm");

  if (!updateProfileForm) return;

  updateProfileForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const hoTen = document.getElementById("adminFullNameInput").value.trim();
    const sdt = document.getElementById("adminPhoneInput").value.trim();
    const ngaySinh = document.getElementById("adminBirthdayInput").value;

    const errorMessage = validateAdminProfileForm(hoTen, sdt, ngaySinh);
    if (errorMessage) {
      showToast("error", "Dữ liệu không hợp lệ", errorMessage);
      return;
    }

    try {
      const apiResult = await apiRequest("/admin/api/profile", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ hoTen, sdt, ngaySinh }),
      });
      if (!apiResult) return;

      const { result } = apiResult;

      if (result.success) {
        showToast(
          "success",
          "Thành công",
          result.message || "Cập nhật thông tin thành công!",
        );
        fetchAdminProfile();
      } else {
        showToast("error", "Thất bại", result.message || "Cập nhật thất bại");
      }
    } catch (error) {
      console.error("Lỗi cập nhật profile:", error);
      showToast("error", "Lỗi", "Có lỗi xảy ra khi cập nhật hồ sơ");
    }
  });
}

function validateAvatarFile(file) {
  const allowedTypes = ["image/jpeg", "image/png", "image/gif", "image/jpg"];

  if (!allowedTypes.includes(file.type)) {
    return "Chỉ chấp nhận tệp hình ảnh (.jpg, .jpeg, .png, .gif)";
  }

  if (file.size > 2 * 1024 * 1024) {
    return "Dung lượng tệp không được vượt quá 2MB";
  }

  return null;
}

function previewAvatar(file) {
  const settingsAvatarPreview = document.getElementById("settingsAvatarPreview");
  if (!settingsAvatarPreview) return;

  const reader = new FileReader();

  reader.onload = function (e) {
    settingsAvatarPreview.innerHTML = `
      <img src="${e.target.result}" alt="Avatar Preview">
    `;
  };

  reader.readAsDataURL(file);
}

function initAvatarUpload() {
  const btnTriggerAvatarUpload = document.getElementById("btnTriggerAvatarUpload");
  const adminAvatarFileInput = document.getElementById("adminAvatarFileInput");

  if (!btnTriggerAvatarUpload || !adminAvatarFileInput) return;

  btnTriggerAvatarUpload.addEventListener("click", function () {
    adminAvatarFileInput.click();
  });

  adminAvatarFileInput.addEventListener("change", async function () {
    const file = this.files[0];
    if (!file) return;

    const errorMessage = validateAvatarFile(file);
    if (errorMessage) {
      showToast("error", "Lỗi tệp tin", errorMessage);
      this.value = "";
      return;
    }

    previewAvatar(file);

    try {
      const formData = new FormData();
      formData.append("avatar", file);

      const apiResult = await apiRequest("/admin/api/profile/avatar", {
        method: "POST",
        body: formData,
      });
      if (!apiResult) return;

      const { result } = apiResult;

      if (result.success) {
        showToast("success", "Thành công", "Tải lên ảnh đại diện thành công!");
        fetchAdminProfile();
      } else {
        showToast("error", "Thất bại", result.message || "Tải lên thất bại");
        fetchAdminProfile();
      }
    } catch (error) {
      console.error("Lỗi tải lên avatar:", error);
      showToast("error", "Lỗi", "Có lỗi xảy ra khi kết nối máy chủ");
      fetchAdminProfile();
    } finally {
      this.value = "";
    }
  });
}

function initChangePasswordForm() {
  const changePasswordForm = document.getElementById("changePasswordForm");

  if (!changePasswordForm) return;

  changePasswordForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const currentPassword = document
      .getElementById("currentPassword")
      .value.trim();
    const newPassword = document.getElementById("newPassword").value.trim();
    const confirmPassword = document
      .getElementById("confirmPassword")
      .value.trim();

    try {
      const apiResult = await apiRequest("/admin/api/profile/password", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          currentPassword,
          newPassword,
          confirmPassword,
        }),
      });
      if (!apiResult) return;

      const { result } = apiResult;

      if (result.success) {
        showToast("success", "Thành công", result.message);
        changePasswordForm.reset();
      } else {
        showToast(
          "error",
          "Thất bại",
          result.message || "Đổi mật khẩu thất bại",
        );
      }
    } catch (error) {
      console.error("Lỗi đổi mật khẩu:", error);
      showToast("error", "Lỗi", "Có lỗi xảy ra khi đổi mật khẩu");
    }
  });
}

function initSettingsModule() {
  fetchAdminProfile();
  initUpdateProfileForm();
  initAvatarUpload();
  initChangePasswordForm();
}


// Alias để homeAdmin.js gọi module setting.
function initProfileModule() {
  initSettingsModule();
}
