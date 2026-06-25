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
                },
                body: JSON.stringify({
                    payment_method: selectedMethod.toUpperCase()
                })
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


