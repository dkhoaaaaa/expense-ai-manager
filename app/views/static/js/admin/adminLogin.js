// loginAdmin.js
// Xử lý đăng nhập admin

document.addEventListener("DOMContentLoaded", function () {
  const loginForm = document.getElementById("loginForm");

  if (!loginForm) return;

  loginForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!email || !password) {
      showToast("error", "Thiếu thông tin", "Vui lòng nhập email và mật khẩu");
      return;
    }

    try {
      const response = await fetch("/admin/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const result = await response.json();

      if (result.success) {
        saveAdminSession(result.accessToken, result.admin);
        window.location.href = "/admin/home";
      } else {
        showToast("error", "Đăng nhập thất bại", result.message || "Sai thông tin đăng nhập");
      }
    } catch (error) {
      console.error("Lỗi đăng nhập admin:", error);
      showToast("error", "Lỗi", "Không thể kết nối máy chủ");
    }
  });
});
