document.addEventListener('DOMContentLoaded', function() {
    const methodCards = document.querySelectorAll('.payment-method-card');
    let selectedMethod = 'banking'; // Mặc định là banking

    // Xử lý khi chọn phương thức thanh toán
    methodCards.forEach(card => {
        card.addEventListener('click', function() {
            // Remove active style from all cards
            methodCards.forEach(c => {
                c.classList.remove('active');
                c.querySelector('.select-indicator i').classList.add('d-none');
            });

            // Add active style to selected card
            this.classList.add('active');
            this.querySelector('.select-indicator i').classList.remove('d-none');

            // Cập nhật phương thức đã chọn
            selectedMethod = this.getAttribute('data-method');
        });
    });

    // Xử lý khi nhấn nút "Xác nhận thanh toán"
    const confirmBtn = document.getElementById('confirmPaymentBtn');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', function() {
            // Vô hiệu hóa nút để tránh click nhiều lần
            confirmBtn.disabled = true;
            confirmBtn.innerText = 'Đang xử lý...';

            // Gọi API kích hoạt Premium
            fetch('/api/premium/activate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Không thể kích hoạt Premium, vui lòng thử lại.');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Hiển thị toast thành công
                    showToast('success', 'Thanh toán thành công', 'Tài khoản đã được nâng cấp Premium!');
                    
                    // Chuyển hướng về trang chủ sau 2 giây để người dùng kịp đọc toast
                    setTimeout(() => {
                        window.location.href = '/home';
                    }, 2000);
                } else {
                    showToast('error', 'Thất bại', data.error || 'Có lỗi xảy ra khi kích hoạt Premium.');
                    confirmBtn.disabled = false;
                    confirmBtn.innerText = 'Xác nhận thanh toán';
                }
            })
            .catch(error => {
                showToast('error', 'Lỗi kết nối', error.message || 'Lỗi kết nối server.');
                confirmBtn.disabled = false;
                confirmBtn.innerText = 'Xác nhận thanh toán';
            });
        });
    }
});

// Toast notification function tương tự như trong admin folder
function showToast(type, title, message, duration = 4000) {
    const container = document.getElementById("toastContainer");
    if (!container) {
        console.warn("Không tìm thấy #toastContainer");
        return;
    }

    const icon = type === "success"
        ? '<i class="bi bi-check-circle-fill"></i>'
        : '<i class="bi bi-x-circle-fill"></i>';

    const id = "toast_" + Date.now() + "_" + Math.random().toString(36).slice(2, 6);
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
