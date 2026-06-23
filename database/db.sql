SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS thanh_toan;
DROP TABLE IF EXISTS tin_nhan_chatbot;
DROP TABLE IF EXISTS lich_su_du_doan_chi_tieu;
DROP TABLE IF EXISTS lich_su_ai_phan_loai;
DROP TABLE IF EXISTS du_lieu_huan_luyen_ai;
DROP TABLE IF EXISTS ngan_sach;
DROP TABLE IF EXISTS giao_dich;
DROP TABLE IF EXISTS danh_muc;
DROP TABLE IF EXISTS goi_premium;
DROP TABLE IF EXISTS nguoi_dung;
DROP TABLE IF EXISTS tai_khoan;

SET FOREIGN_KEY_CHECKS = 1;

-- =========================
-- 1. TÀI KHOẢN
-- =========================
CREATE TABLE tai_khoan (
    id INT AUTO_INCREMENT PRIMARY KEY,

    email VARCHAR(100) NOT NULL UNIQUE,
    mat_khau_hash VARCHAR(255) NOT NULL,

    vai_tro ENUM('USER', 'PREMIUM', 'ADMIN') DEFAULT 'USER',
    trang_thai ENUM('ACTIVE', 'BANNED') DEFAULT 'ACTIVE',

    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =========================
-- 2. NGƯỜI DÙNG
-- =========================
CREATE TABLE nguoi_dung (
    id INT AUTO_INCREMENT PRIMARY KEY,

    tai_khoan_id INT NOT NULL UNIQUE,

    ho_ten VARCHAR(100) NOT NULL,
    so_dien_thoai VARCHAR(20),
    ngay_sinh DATE,
    gioi_tinh ENUM('NAM', 'NU', 'KHAC'),
    anh_dai_dien VARCHAR(255),

    is_premium BOOLEAN DEFAULT FALSE,
    premium_start_date DATETIME DEFAULT NULL,
    premium_end_date DATETIME DEFAULT NULL,

    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (tai_khoan_id) REFERENCES tai_khoan(id)
        ON DELETE CASCADE
);

-- =========================
-- 3. GÓI PREMIUM
-- =========================
CREATE TABLE goi_premium (
    id INT AUTO_INCREMENT PRIMARY KEY,

    tai_khoan_id INT NOT NULL,

    ten_goi VARCHAR(50) DEFAULT 'PREMIUM',
    gia DECIMAL(12,2) NOT NULL,

    trang_thai ENUM('ACTIVE', 'EXPIRED', 'CANCELLED') DEFAULT 'ACTIVE',

    ngay_bat_dau DATETIME DEFAULT CURRENT_TIMESTAMP,
    ngay_ket_thuc DATETIME NOT NULL,

    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (tai_khoan_id) REFERENCES tai_khoan(id)
        ON DELETE CASCADE
);

-- =========================
-- 4. DANH MỤC THU / CHI
-- Bảng danh mục lưu keyword_ai cho rule-based/AI phân loại giao dịch
-- Không dùng cột icon trong phiên bản hiện tại
-- =========================
CREATE TABLE danh_muc (
    id INT AUTO_INCREMENT PRIMARY KEY,

    ten_danh_muc VARCHAR(100) NOT NULL,
    loai ENUM('THU', 'CHI') NOT NULL,
    keyword_ai TEXT,
    trang_thai ENUM('ACTIVE', 'INACTIVE') DEFAULT 'ACTIVE',

    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uq_danh_muc_ten_loai (ten_danh_muc, loai)
);

-- =========================
-- 5. GIAO DỊCH
-- =========================
CREATE TABLE giao_dich (
    id INT AUTO_INCREMENT PRIMARY KEY,

    tai_khoan_id INT NOT NULL,
    danh_muc_id INT,

    loai ENUM('THU', 'CHI') NOT NULL,
    so_tien DECIMAL(12,2) NOT NULL,

    mo_ta TEXT,
    ngay_giao_dich DATE NOT NULL,

    phuong_thuc_phan_loai ENUM('THU_CONG', 'RULE_BASED', 'MACHINE_LEARNING') DEFAULT 'THU_CONG',
    do_tin_cay DECIMAL(5,2),

    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (tai_khoan_id) REFERENCES tai_khoan(id)
        ON DELETE CASCADE,

    FOREIGN KEY (danh_muc_id) REFERENCES danh_muc(id)
        ON DELETE SET NULL
);

-- =========================
-- 6. NGÂN SÁCH
-- =========================
CREATE TABLE ngan_sach (
    id INT AUTO_INCREMENT PRIMARY KEY,

    tai_khoan_id INT NOT NULL,
    danh_muc_id INT,

    thang INT NOT NULL,
    nam INT NOT NULL,
    han_muc DECIMAL(12,2) NOT NULL,

    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (tai_khoan_id) REFERENCES tai_khoan(id)
        ON DELETE CASCADE,

    FOREIGN KEY (danh_muc_id) REFERENCES danh_muc(id)
        ON DELETE SET NULL
);

-- =========================
-- 7. DỮ LIỆU HUẤN LUYỆN AI
-- =========================
CREATE TABLE du_lieu_huan_luyen_ai (
    id INT AUTO_INCREMENT PRIMARY KEY,

    mo_ta TEXT NOT NULL,
    danh_muc_id INT NOT NULL,

    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (danh_muc_id) REFERENCES danh_muc(id)
        ON DELETE CASCADE
);

-- =========================
-- 8. LỊCH SỬ AI PHÂN LOẠI
-- =========================
CREATE TABLE lich_su_ai_phan_loai (
    id INT AUTO_INCREMENT PRIMARY KEY,

    tai_khoan_id INT NOT NULL,

    van_ban_nhap TEXT,
    danh_muc_du_doan_id INT,

    do_tin_cay DECIMAL(5,2),
    ten_model VARCHAR(100),

    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (tai_khoan_id) REFERENCES tai_khoan(id)
        ON DELETE CASCADE,

    FOREIGN KEY (danh_muc_du_doan_id) REFERENCES danh_muc(id)
        ON DELETE SET NULL
);

-- =========================
-- 9. LỊCH SỬ DỰ ĐOÁN CHI TIÊU
-- =========================
CREATE TABLE lich_su_du_doan_chi_tieu (
    id INT AUTO_INCREMENT PRIMARY KEY,

    tai_khoan_id INT NOT NULL,

    thang_du_doan INT NOT NULL,
    nam_du_doan INT NOT NULL,

    so_tien_du_doan DECIMAL(12,2) NOT NULL,
    do_tin_cay DECIMAL(5,2),

    xu_huong ENUM('TANG', 'GIAM', 'ON_DINH'),

    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (tai_khoan_id) REFERENCES tai_khoan(id)
        ON DELETE CASCADE
);

-- =========================
-- 10. TIN NHẮN CHATBOT
-- =========================
CREATE TABLE tin_nhan_chatbot (
    id INT AUTO_INCREMENT PRIMARY KEY,

    tai_khoan_id INT NOT NULL,

    nguoi_gui ENUM('USER', 'BOT') NOT NULL,
    noi_dung TEXT NOT NULL,

    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (tai_khoan_id) REFERENCES tai_khoan(id)
        ON DELETE CASCADE
);

-- =========================
-- 11. THANH TOÁN
-- =========================
CREATE TABLE thanh_toan (
    id INT AUTO_INCREMENT PRIMARY KEY,

    tai_khoan_id INT NOT NULL,
    goi_premium_id INT,

    so_tien DECIMAL(12,2) NOT NULL,
    phuong_thuc_thanh_toan VARCHAR(50),

    trang_thai_thanh_toan ENUM('PENDING', 'SUCCESS', 'FAILED') DEFAULT 'PENDING',
    ma_giao_dich VARCHAR(100),

    ngay_thanh_toan DATETIME,
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (tai_khoan_id) REFERENCES tai_khoan(id)
        ON DELETE CASCADE,

    FOREIGN KEY (goi_premium_id) REFERENCES goi_premium(id)
        ON DELETE SET NULL
);

-- =========================================================
-- 12. SEED DATA
-- =========================================================

-- =========================
-- TÀI KHOẢN
-- Mật khẩu:
-- admin@example.com -> admin123
-- các user còn lại -> user123
-- =========================
INSERT INTO tai_khoan (id, email, mat_khau_hash, vai_tro, trang_thai) VALUES
(1, 'admin@example.com', 'scrypt:32768:8:1$LhaTnYqO7XnGarwz$c9bf0068e1611356e1dbd38b03bb93d196cf9adfef0f4b6ab52d8fffd9606374e98e95fd880754a71e468d0f5e4220c9915b2955a9d3bd306ece4a125a1a2114', 'ADMIN', 'ACTIVE'),
(2, 'user@example.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE'),
(3, 'premium@example.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'PREMIUM', 'ACTIVE'),
(4, 'nguyenvana@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE'),
(5, 'tranminhb@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'PREMIUM', 'ACTIVE'),
(6, 'lehoangc@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE'),
(7, 'phamthid@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'BANNED'),
(8, 'dangquange@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'PREMIUM', 'ACTIVE');

-- =========================
-- NGƯỜI DÙNG
-- =========================
INSERT INTO nguoi_dung 
(tai_khoan_id, ho_ten, so_dien_thoai, ngay_sinh, gioi_tinh, anh_dai_dien) 
VALUES
(1, 'Administrator', '0900000001', '2000-01-01', 'NAM', NULL),
(2, 'Example User', '0900000002', '2003-05-10', 'NAM', NULL),
(3, 'Premium User', '0900000003', '2002-03-15', 'NAM', NULL),
(4, 'Nguyễn Văn A', '0901234567', '2003-01-12', 'NAM', NULL),
(5, 'Trần Minh B', '0912345678', '2002-07-20', 'NAM', NULL),
(6, 'Lê Hoàng C', '0923456789', '2004-11-05', 'NAM', NULL),
(7, 'Phạm Thị D', '0934567890', '2001-09-25', 'NU', NULL),
(8, 'Đặng Quang E', '0945678901', '2000-12-01', 'NAM', NULL);

-- =========================
-- DANH MỤC
-- Không còn cột icon
-- =========================
INSERT INTO danh_muc 
(id, ten_danh_muc, loai, keyword_ai, trang_thai) 
VALUES
(1, 'Lương', 'THU', 'lương, nhận lương, salary, lương tháng, công ty chuyển khoản', 'ACTIVE'),
(2, 'Thưởng', 'THU', 'thưởng, bonus, thưởng KPI, thưởng dự án, tiền thưởng', 'ACTIVE'),
(3, 'Đầu tư', 'THU', 'lãi đầu tư, chứng khoán, cổ phiếu, lãi gửi tiết kiệm, crypto', 'ACTIVE'),

(4, 'Ăn uống', 'CHI', 'ăn sáng, ăn trưa, ăn tối, cơm, phở, bún bò, cafe, cà phê, trà sữa, nhà hàng', 'ACTIVE'),
(5, 'Di chuyển', 'CHI', 'grab, taxi, xe buýt, đổ xăng, xăng xe, vé xe, gửi xe, đi lại', 'ACTIVE'),
(6, 'Mua sắm', 'CHI', 'mua áo, mua giày, shopee, lazada, tiki, quần áo, tai nghe, balo, mua đồ', 'ACTIVE'),
(7, 'Giải trí', 'CHI', 'xem phim, cgv, game, nạp game, karaoke, concert, du lịch, giải trí', 'ACTIVE'),
(8, 'Học tập', 'CHI', 'học phí, khóa học, sách, tài liệu, học tiếng anh, python, lập trình', 'ACTIVE'),
(9, 'Sức khỏe', 'CHI', 'khám bệnh, mua thuốc, nha khoa, bệnh viện, sức khỏe, khám sức khỏe', 'ACTIVE'),
(10, 'Hóa đơn', 'CHI', 'tiền điện, tiền nước, internet, điện thoại, hóa đơn, wifi, thanh toán điện', 'ACTIVE'),
(11, 'Nhà ở', 'CHI', 'tiền thuê phòng, tiền nhà, phòng trọ, sửa phòng, thuê nhà, nhà ở', 'ACTIVE'),
(12, 'Khác', 'CHI', 'khác, linh tinh, không rõ, chi phí khác', 'ACTIVE');

-- =========================
-- GÓI PREMIUM
-- =========================
INSERT INTO goi_premium 
(id, tai_khoan_id, ten_goi, gia, trang_thai, ngay_bat_dau, ngay_ket_thuc) 
VALUES
(1, 3, 'PREMIUM', 99000.00, 'ACTIVE', '2026-06-01 08:00:00', '2026-07-01 08:00:00'),
(2, 5, 'PREMIUM', 99000.00, 'ACTIVE', '2026-06-03 09:30:00', '2026-07-03 09:30:00'),
(3, 8, 'PREMIUM', 99000.00, 'ACTIVE', '2026-05-20 14:00:00', '2026-06-20 14:00:00'),
(4, 6, 'PREMIUM', 99000.00, 'EXPIRED', '2026-04-01 10:00:00', '2026-05-01 10:00:00');

-- =========================
-- THANH TOÁN
-- =========================
INSERT INTO thanh_toan 
(tai_khoan_id, goi_premium_id, so_tien, phuong_thuc_thanh_toan, trang_thai_thanh_toan, ma_giao_dich, ngay_thanh_toan) 
VALUES
(3, 1, 99000.00, 'MOMO', 'SUCCESS', 'MOMO202606010001', '2026-06-01 08:00:00'),
(5, 2, 99000.00, 'VNPAY', 'SUCCESS', 'VNPAY202606030001', '2026-06-03 09:30:00'),
(8, 3, 99000.00, 'BANKING', 'SUCCESS', 'BANK202605200001', '2026-05-20 14:00:00'),
(6, 4, 99000.00, 'MOMO', 'SUCCESS', 'MOMO202604010001', '2026-04-01 10:00:00'),
(4, NULL, 99000.00, 'MOMO', 'FAILED', 'MOMO202606040001', NULL),
(2, NULL, 99000.00, 'VNPAY', 'PENDING', 'VNPAY202606050001', NULL);

-- =========================
-- GIAO DỊCH
-- =========================
INSERT INTO giao_dich 
(tai_khoan_id, danh_muc_id, loai, so_tien, mo_ta, ngay_giao_dich, phuong_thuc_phan_loai, do_tin_cay) 
VALUES
-- User 2 (Example User) - June 2026
(2, 1, 'THU', 8000000.00, 'Nhận lương tháng 6', '2026-06-01', 'THU_CONG', NULL),
(2, 4, 'CHI', 35000.00, 'Cơm trưa văn phòng', '2026-06-01', 'RULE_BASED', 95.00),
(2, 4, 'CHI', 29000.00, 'Cà phê sữa đá Highlands', '2026-06-01', 'RULE_BASED', 90.00),
(2, 4, 'CHI', 120000.00, 'Ăn trưa với bạn', '2026-06-02', 'RULE_BASED', 92.50),
(2, 5, 'CHI', 75000.00, 'Đi Grab đến trường', '2026-06-02', 'RULE_BASED', 88.00),
(2, 4, 'CHI', 45000.00, 'Bún bò ăn tối', '2026-06-02', 'RULE_BASED', 91.00),
(2, 10, 'CHI', 350000.00, 'Thanh toán tiền điện', '2026-06-03', 'MACHINE_LEARNING', 84.25),
(2, 5, 'CHI', 50000.00, 'Đổ xăng xe máy', '2026-06-03', 'RULE_BASED', 87.00),
(2, 4, 'CHI', 40000.00, 'Cơm tấm sườn bì', '2026-06-03', 'RULE_BASED', 92.00),
(2, 11, 'CHI', 2500000.00, 'Tiền phòng trọ tháng 6', '2026-06-04', 'RULE_BASED', 96.00),
(2, 8, 'CHI', 150000.00, 'Mua sách học lập trình Python', '2026-06-04', 'RULE_BASED', 89.00),
(2, 4, 'CHI', 65000.00, 'Mì cay Hàn Quốc ăn tối', '2026-06-04', 'RULE_BASED', 93.00),
(2, 2, 'THU', 1500000.00, 'Thưởng dự án Freelance', '2026-06-05', 'RULE_BASED', 94.00),
(2, 6, 'CHI', 230000.00, 'Mua quần áo Shopee', '2026-06-05', 'RULE_BASED', 91.00),
(2, 4, 'CHI', 55000.00, 'Trà sữa Gong Cha', '2026-06-05', 'RULE_BASED', 90.00),
(2, 4, 'CHI', 420000.00, 'Đi siêu thị Co.opmart mua đồ ăn', '2026-06-06', 'RULE_BASED', 95.00),
(2, 5, 'CHI', 90000.00, 'Đi taxi Grab', '2026-06-06', 'RULE_BASED', 88.00),
(2, 7, 'CHI', 150000.00, 'Xem phim CGV cuối tuần', '2026-06-07', 'RULE_BASED', 89.00),
(2, 4, 'CHI', 20000.00, 'Bánh mì ăn sáng', '2026-06-07', 'RULE_BASED', 90.00),
(2, 4, 'CHI', 280000.00, 'Ăn lẩu Kichi Kichi', '2026-06-07', 'RULE_BASED', 92.00),
(2, 9, 'CHI', 45000.00, 'Mua thuốc cảm cúm Pharmacity', '2026-06-08', 'RULE_BASED', 94.00),
(2, 4, 'CHI', 45000.00, 'Bún chả Hà Nội trưa', '2026-06-08', 'RULE_BASED', 91.00),
(2, 10, 'CHI', 85000.00, 'Đóng tiền nước sinh hoạt', '2026-06-09', 'RULE_BASED', 89.00),
(2, 4, 'CHI', 35000.00, 'Trà đào sả', '2026-06-09', 'RULE_BASED', 90.00),
(2, 3, 'THU', 850000.00, 'Lãi đầu tư chứng khoán', '2026-06-10', 'RULE_BASED', 92.00),
(2, 6, 'CHI', 350000.00, 'Mua tai nghe chụp tai mới', '2026-06-10', 'RULE_BASED', 91.00),
(2, 5, 'CHI', 7000.00, 'Đi xe bus', '2026-06-10', 'RULE_BASED', 95.00),
(2, 4, 'CHI', 25000.00, 'Ăn tối hủ tiếu gõ', '2026-06-11', 'RULE_BASED', 90.00),
(2, 4, 'CHI', 30000.00, 'Cà phê Aha', '2026-06-11', 'RULE_BASED', 90.00),
(2, 10, 'CHI', 100000.00, 'Nạp tiền điện thoại Viettel', '2026-06-12', 'RULE_BASED', 92.00),
(2, 4, 'CHI', 115000.00, 'Đi ăn gà rán KFC', '2026-06-12', 'RULE_BASED', 93.00),
(2, 7, 'CHI', 250000.00, 'Đi uống bia với đồng nghiệp', '2026-06-13', 'RULE_BASED', 88.00),
(2, 5, 'CHI', 80000.00, 'Đi taxi Mai Linh', '2026-06-13', 'RULE_BASED', 87.00),
(2, 12, 'CHI', 70000.00, 'Đi cắt tóc nam', '2026-06-14', 'RULE_BASED', 90.00),
(2, 4, 'CHI', 40000.00, 'Ăn phở bò sáng', '2026-06-14', 'RULE_BASED', 91.00),
(2, 1, 'THU', 2000000.00, 'Nhận tiền hỗ trợ từ gia đình', '2026-06-15', 'RULE_BASED', 94.00),
(2, 4, 'CHI', 35000.00, 'Cơm trưa văn phòng', '2026-06-15', 'RULE_BASED', 95.00),
(2, 4, 'CHI', 15000.00, 'Trà chanh vỉa hè', '2026-06-15', 'RULE_BASED', 90.00),
(2, 10, 'CHI', 220000.00, 'Thanh toán hóa đơn internet', '2026-06-16', 'RULE_BASED', 92.00),
(2, 5, 'CHI', 60000.00, 'Đổ xăng xe máy', '2026-06-16', 'RULE_BASED', 89.00),
(2, 12, 'CHI', 135000.00, 'Mua kem đánh răng và sữa tắm', '2026-06-17', 'RULE_BASED', 90.00),
(2, 4, 'CHI', 35000.00, 'Bún riêu cua ăn tối', '2026-06-17', 'RULE_BASED', 91.00),
(2, 7, 'CHI', 450000.00, 'Mua vé xem ca nhạc', '2026-06-18', 'RULE_BASED', 88.00),
(2, 4, 'CHI', 25000.00, 'Bánh ngọt ăn nhẹ', '2026-06-18', 'RULE_BASED', 90.00),
(2, 12, 'CHI', 95000.00, 'Mua đồ dùng cá nhân', '2026-06-19', 'RULE_BASED', 90.00),
(2, 4, 'CHI', 45000.00, 'Cơm gà ăn trưa', '2026-06-19', 'RULE_BASED', 91.00),
(2, 4, 'CHI', 30000.00, 'Sinh tố bơ tối', '2026-06-19', 'RULE_BASED', 90.00),

-- User 3 (Premium User) - June 2026
(3, 1, 'THU', 12000000.00, 'Lương công ty', '2026-06-01', 'THU_CONG', NULL),
(3, 4, 'CHI', 95000.00, 'Cafe sáng', '2026-06-01', 'MACHINE_LEARNING', 91.30),
(3, 6, 'CHI', 650000.00, 'Mua áo mới', '2026-06-02', 'MACHINE_LEARNING', 86.70),
(3, 8, 'CHI', 299000.00, 'Mua khóa học Python', '2026-06-04', 'MACHINE_LEARNING', 94.10),

-- User 4 (Nguyễn Văn A) - June 2026
(4, 1, 'THU', 5000000.00, 'Lương part-time', '2026-06-01', 'THU_CONG', NULL),
(4, 4, 'CHI', 45000.00, 'Cơm trưa', '2026-06-02', 'RULE_BASED', 90.00),
(4, 7, 'CHI', 120000.00, 'Xem phim cuối tuần', '2026-06-03', 'RULE_BASED', 78.50),

-- User 5 (Trần Minh B) - June 2026
(5, 1, 'THU', 15000000.00, 'Lương tháng 6', '2026-06-01', 'THU_CONG', NULL),
(5, 11, 'CHI', 3000000.00, 'Tiền thuê phòng', '2026-06-01', 'MACHINE_LEARNING', 89.20),
(5, 9, 'CHI', 450000.00, 'Khám sức khỏe', '2026-06-02', 'MACHINE_LEARNING', 83.40),

-- User 6 (Lê Hoàng C) - June 2026
(6, 2, 'THU', 1000000.00, 'Tiền thưởng dự án', '2026-06-02', 'THU_CONG', NULL),
(6, 6, 'CHI', 850000.00, 'Mua tai nghe', '2026-06-03', 'RULE_BASED', 76.80),

-- User 8 (Đặng Quang E) - June 2026
(8, 3, 'THU', 2500000.00, 'Lãi đầu tư', '2026-06-04', 'THU_CONG', NULL),
(8, 10, 'CHI', 500000.00, 'Thanh toán internet', '2026-06-04', 'MACHINE_LEARNING', 87.90),
(8, 4, 'CHI', 180000.00, 'Ăn tối gia đình', '2026-06-05', 'MACHINE_LEARNING', 92.00);

-- =========================
-- NGÂN SÁCH
-- =========================
INSERT INTO ngan_sach 
(tai_khoan_id, danh_muc_id, thang, nam, han_muc) 
VALUES
(2, 4, 6, 2026, 2500000.00),
(2, 5, 6, 2026, 1000000.00),
(2, 10, 6, 2026, 800000.00),

(3, 4, 6, 2026, 3000000.00),
(3, 6, 6, 2026, 2000000.00),
(3, 8, 6, 2026, 1500000.00),

(4, 4, 6, 2026, 1800000.00),
(4, 7, 6, 2026, 700000.00),

(5, 11, 6, 2026, 3500000.00),
(5, 9, 6, 2026, 1000000.00),

(8, 4, 6, 2026, 2500000.00),
(8, 10, 6, 2026, 1200000.00);

-- =========================
-- DỮ LIỆU HUẤN LUYỆN AI
-- =========================
INSERT INTO du_lieu_huan_luyen_ai 
(mo_ta, danh_muc_id) 
VALUES
('ăn sáng bún bò', 4),
('ăn trưa cơm tấm', 4),
('uống cà phê Highlands', 4),
('mua trà sữa', 4),
('ăn tối nhà hàng', 4),

('đi Grab', 5),
('đổ xăng xe máy', 5),
('vé xe buýt', 5),
('taxi đi sân bay', 5),

('mua áo thun', 6),
('mua giày sneaker', 6),
('mua đồ trên Shopee', 6),
('mua balo mới', 6),

('xem phim CGV', 7),
('nạp game', 7),
('đi karaoke', 7),
('mua vé concert', 7),

('mua sách lập trình', 8),
('đóng học phí', 8),
('mua khóa học online', 8),
('học tiếng Anh', 8),

('khám bệnh', 9),
('mua thuốc', 9),
('khám nha khoa', 9),

('trả tiền điện', 10),
('trả tiền nước', 10),
('thanh toán internet', 10),
('trả hóa đơn điện thoại', 10),

('tiền thuê phòng', 11),
('đóng tiền nhà', 11),
('sửa đồ trong phòng trọ', 11),

('nhận lương tháng', 1),
('lương công ty chuyển khoản', 1),

('tiền thưởng KPI', 2),
('thưởng dự án', 2),

('lãi đầu tư chứng khoán', 3),
('lãi gửi tiết kiệm', 3);

-- =========================
-- LỊCH SỬ AI PHÂN LOẠI
-- =========================
INSERT INTO lich_su_ai_phan_loai 
(tai_khoan_id, van_ban_nhap, danh_muc_du_doan_id, do_tin_cay, ten_model) 
VALUES
(2, 'ăn trưa với bạn', 4, 92.50, 'Rule Based v1'),
(2, 'đi Grab đến trường', 5, 88.00, 'Rule Based v1'),
(2, 'thanh toán tiền điện', 10, 84.25, 'Logistic Regression'),

(3, 'Cafe sáng', 4, 91.30, 'Logistic Regression'),
(3, 'Mua áo mới', 6, 86.70, 'Logistic Regression'),
(3, 'Mua khóa học Python', 8, 94.10, 'Logistic Regression'),

(4, 'Cơm trưa', 4, 90.00, 'Rule Based v1'),
(4, 'Xem phim cuối tuần', 7, 78.50, 'Rule Based v1'),

(5, 'Tiền thuê phòng', 11, 89.20, 'Logistic Regression'),
(5, 'Khám sức khỏe', 9, 83.40, 'Logistic Regression'),

(6, 'mua đồ linh tinh ngoài chợ', 12, 55.20, 'Logistic Regression'),

(8, 'Thanh toán internet', 10, 87.90, 'Logistic Regression'),
(8, 'Ăn tối gia đình', 4, 92.00, 'Logistic Regression');

-- =========================
-- LỊCH SỬ DỰ ĐOÁN CHI TIÊU
-- =========================
INSERT INTO lich_su_du_doan_chi_tieu 
(tai_khoan_id, thang_du_doan, nam_du_doan, so_tien_du_doan, do_tin_cay, xu_huong) 
VALUES
(2, 7, 2026, 4200000.00, 81.50, 'TANG'),
(3, 7, 2026, 5800000.00, 86.20, 'GIAM'),
(4, 7, 2026, 2700000.00, 74.80, 'ON_DINH'),
(5, 7, 2026, 6500000.00, 88.00, 'TANG'),
(6, 7, 2026, 3100000.00, 69.50, 'TANG'),
(8, 7, 2026, 3900000.00, 84.70, 'ON_DINH');

-- =========================
-- TIN NHẮN CHATBOT
-- =========================
INSERT INTO tin_nhan_chatbot 
(tai_khoan_id, nguoi_gui, noi_dung) 
VALUES
(2, 'USER', 'Tháng này tôi chi nhiều nhất vào đâu?'),
(2, 'BOT', 'Tháng này bạn chi nhiều nhất vào Ăn uống và Hóa đơn.'),

(3, 'USER', 'Dự đoán chi tiêu tháng sau của tôi là bao nhiêu?'),
(3, 'BOT', 'Dựa trên dữ liệu hiện tại, chi tiêu tháng sau của bạn có thể khoảng 5,800,000đ.'),

(4, 'USER', 'Làm sao để tiết kiệm hơn?'),
(4, 'BOT', 'Bạn nên đặt ngân sách cho Ăn uống và Giải trí vì đây là hai danh mục chi nhiều.'),

(5, 'USER', 'Tôi có đang chi vượt ngân sách không?'),
(5, 'BOT', 'Bạn đang gần đạt giới hạn ngân sách Nhà ở, hãy theo dõi thêm trong tuần này.'),

(8, 'USER', 'Danh mục nào chi tiêu tăng mạnh nhất?'),
(8, 'BOT', 'Danh mục Hóa đơn có xu hướng tăng nhẹ so với tháng trước.');
