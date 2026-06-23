document.addEventListener('DOMContentLoaded', function() {
    const upgradeBtn = document.getElementById('upgradePremiumNowBtn');
    if (upgradeBtn) {
        upgradeBtn.addEventListener('click', function() {
            // Chuyển hướng người dùng sang trang thanh toán
            window.location.href = '/premium/payment';
        });
    }
});
