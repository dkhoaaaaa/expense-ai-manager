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
INSERT INTO tai_khoan (id, email, mat_khau_hash, vai_tro, trang_thai, ngay_tao, ngay_cap_nhat) VALUES
(1, 'admin@example.com', 'scrypt:32768:8:1$LhaTnYqO7XnGarwz$c9bf0068e1611356e1dbd38b03bb93d196cf9adfef0f4b6ab52d8fffd9606374e98e95fd880754a71e468d0f5e4220c9915b2955a9d3bd306ece4a125a1a2114', 'ADMIN', 'ACTIVE', '2026-01-01 08:00:00', '2026-01-01 08:00:00'),
(2, 'user@example.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-01-15 10:30:00', '2026-01-15 10:30:00'),
(3, 'premium@example.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'PREMIUM', 'ACTIVE', '2026-05-28 14:15:00', '2026-05-28 14:15:00'),
(4, 'nguyenvana@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-05-30 09:20:00', '2026-05-30 09:20:00'),
(5, 'tranminhb@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'PREMIUM', 'ACTIVE', '2026-06-01 11:00:00', '2026-06-01 11:00:00'),
(6, 'lehoangc@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-04-12 16:45:00', '2026-04-12 16:45:00'),
(7, 'phamthid@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'BANNED', '2026-03-22 13:10:00', '2026-03-22 13:10:00'),
(8, 'dangquange@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'PREMIUM', 'ACTIVE', '2026-05-18 15:40:00', '2026-05-18 15:40:00'),
(9, 'levanlam9@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-01-21 08:01:47', '2026-01-21 08:01:47'),
(10, 'tranthilan10@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-01-05 18:06:43', '2026-01-05 18:06:43'),
(11, 'nguyenminhkhoi11@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-01-14 07:01:05', '2026-01-14 07:01:05'),
(12, 'phamthanhthao12@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-02-20 07:35:12', '2026-02-20 07:35:12'),
(13, 'hoangvannam13@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-02-15 16:17:51', '2026-02-15 16:17:51'),
(14, 'buithituyet14@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-02-23 13:21:17', '2026-02-23 13:21:17'),
(15, 'vuhoanglong15@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-02-04 08:24:06', '2026-02-04 08:24:06'),
(16, 'ominhtuan16@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-02-09 19:02:46', '2026-02-09 19:02:46'),
(17, 'phanthanhson17@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-02-03 15:18:53', '2026-02-03 15:18:53'),
(18, 'ngoquynhchi18@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-02-07 18:04:02', '2026-02-07 18:04:02'),
(19, 'duongquocanh19@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-02-03 20:14:55', '2026-02-03 20:14:55'),
(20, 'lyhoaian20@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-02-15 17:53:23', '2026-02-15 17:53:23'),
(21, 'vothihang21@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-03-07 17:17:44', '2026-03-07 17:17:44'),
(22, 'angminhtri22@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-03-21 09:34:46', '2026-03-21 09:34:46'),
(23, 'buihuykhanh23@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-03-13 11:59:40', '2026-03-13 11:59:40'),
(24, 'nguyenthingoc24@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-03-27 19:49:03', '2026-03-27 19:49:03'),
(25, 'tranhuyhoang25@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-03-13 11:04:13', '2026-03-13 11:04:13'),
(26, 'legiabao26@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-03-21 14:25:56', '2026-03-21 14:25:56'),
(27, 'phamminhuc27@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-03-09 09:15:47', '2026-03-09 09:15:47'),
(28, 'hoangkimngan28@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-03-14 21:37:25', '2026-03-14 21:37:25'),
(29, 'othuylinh29@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-03-17 14:05:48', '2026-03-17 14:05:48'),
(30, 'phananhtuan30@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-03-21 09:50:43', '2026-03-21 09:50:43'),
(31, 'ngominhhang31@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-03-13 16:29:33', '2026-03-13 16:29:33'),
(32, 'duonggiakhanh32@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-03-22 21:34:48', '2026-03-22 21:34:48'),
(33, 'vominhtriet33@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-03-10 13:10:29', '2026-03-10 13:10:29'),
(34, 'tranngochai34@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-04-25 09:32:58', '2026-04-25 09:32:58'),
(35, 'nguyenhoangnam35@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-04-17 16:12:09', '2026-04-17 16:12:09'),
(36, 'lethimai36@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-04-25 21:33:58', '2026-04-25 21:33:58'),
(37, 'phamvanong37@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-04-01 08:59:23', '2026-04-01 08:59:23'),
(38, 'hoangquocviet38@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-04-02 10:56:36', '2026-04-02 10:56:36'),
(39, 'omaiphuong39@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-04-27 08:48:34', '2026-04-27 08:48:34'),
(40, 'phanvanhung40@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-04-22 14:35:10', '2026-04-22 14:35:10'),
(41, 'ngothanhvan41@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-05-18 19:46:44', '2026-05-18 19:46:44'),
(42, 'duonghoanglong42@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-05-22 17:23:28', '2026-05-22 17:23:28'),
(43, 'vothidung43@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-05-08 10:04:21', '2026-05-08 10:04:21'),
(44, 'tranquocbao44@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-05-08 07:04:45', '2026-05-08 07:04:45'),
(45, 'nguyenlananh45@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-05-03 21:02:55', '2026-05-03 21:02:55'),
(46, 'leminhquan46@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-05-08 11:42:31', '2026-05-08 11:42:31'),
(47, 'phamhoainam47@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-05-19 14:15:50', '2026-05-19 14:15:50'),
(48, 'hoangthutrang48@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-05-04 08:42:27', '2026-05-04 08:42:27'),
(49, 'ovantien49@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-05-15 20:46:03', '2026-05-15 20:46:03'),
(50, 'phanthihong50@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-05-13 18:21:51', '2026-05-13 18:21:51'),
(51, 'ngotiendung51@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-05-07 10:34:28', '2026-05-07 10:34:28'),
(52, 'duongmylinh52@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-05-09 14:15:55', '2026-05-09 14:15:55'),
(53, 'vominhuc53@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-05-04 07:41:34', '2026-05-04 07:41:34'),
(54, 'trangiahan54@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-05-25 20:15:10', '2026-05-25 20:15:10'),
(55, 'nguyentuankiet55@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-05-07 20:25:57', '2026-05-07 20:25:57'),
(56, 'lequynhanh56@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-06-01 13:16:59', '2026-06-01 13:16:59'),
(57, 'phamthanhhai57@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-06-14 18:46:50', '2026-06-14 18:46:50'),
(58, 'hoangphihung58@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-06-07 11:13:03', '2026-06-07 11:13:03'),
(59, 'ominhtriet59@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-06-02 07:37:30', '2026-06-02 07:37:30'),
(60, 'phangialac60@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-06-17 08:54:11', '2026-06-17 08:54:11'),
(61, 'ngovanat61@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-06-13 08:56:36', '2026-06-13 08:56:36'),
(62, 'duongthuytrang62@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-06-03 13:42:37', '2026-06-03 13:42:37'),
(63, 'vothibich63@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-06-07 17:45:20', '2026-06-07 17:45:20'),
(64, 'trananhdung64@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-06-05 17:41:19', '2026-06-05 17:41:19'),
(65, 'nguyenkhanhlinh65@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-06-01 14:39:36', '2026-06-01 14:39:36'),
(66, 'lehuuat66@gmail.com', 'scrypt:32768:8:1$9YPIsy2D2o9qTBPT$84ff2baf99746d534b164918633621cf7a1018a7305e6cf672cc6ba97d6e8d5091e2ba413efe1b174d49428ad4c465362dde02e725f53f9664b575cfbd065d21', 'USER', 'ACTIVE', '2026-06-07 15:16:08', '2026-06-07 15:16:08');

-- =========================
-- NGƯỜI DÙNG
-- =========================
INSERT INTO nguoi_dung (tai_khoan_id, ho_ten, so_dien_thoai, ngay_sinh, gioi_tinh, anh_dai_dien, is_premium, premium_start_date, premium_end_date, ngay_tao, ngay_cap_nhat) VALUES
(1, 'Administrator', '0900000001', '2000-01-01', 'NAM', NULL, 0, NULL, NULL, '2026-01-01 08:00:00', '2026-01-01 08:00:00'),
(2, 'Example User', '0900000002', '2003-05-10', 'NAM', NULL, 0, NULL, NULL, '2026-01-15 10:30:00', '2026-01-15 10:30:00'),
(3, 'Premium User', '0900000003', '2002-03-15', 'NAM', NULL, 1, '2026-05-28 14:15:00', '2026-06-27 14:15:00', '2026-05-28 14:15:00', '2026-05-28 14:15:00'),
(4, 'Nguyễn Văn A', '0901234567', '2003-01-12', 'NAM', NULL, 0, NULL, NULL, '2026-05-30 09:20:00', '2026-05-30 09:20:00'),
(5, 'Trần Minh B', '0912345678', '2002-07-20', 'NAM', NULL, 1, '2026-06-01 11:00:00', '2026-07-01 11:00:00', '2026-06-01 11:00:00', '2026-06-01 11:00:00'),
(6, 'Lê Hoàng C', '0923456789', '2004-11-05', 'NAM', NULL, 0, NULL, NULL, '2026-04-12 16:45:00', '2026-04-12 16:45:00'),
(7, 'Phạm Thị D', '0934567890', '2001-09-25', 'NU', NULL, 0, NULL, NULL, '2026-03-22 13:10:00', '2026-03-22 13:10:00'),
(8, 'Đặng Quang E', '0945678901', '2000-12-01', 'NAM', NULL, 1, '2026-05-18 15:40:00', '2026-06-17 15:40:00', '2026-05-18 15:40:00', '2026-05-18 15:40:00'),
(9, 'Lê Văn Lâm', '0939958838', '1999-12-02', 'NAM', NULL, 0, NULL, NULL, '2026-01-21 08:01:47', '2026-01-21 08:01:47'),
(10, 'Trần Thị Lan', '0989254563', '1994-09-12', 'NAM', NULL, 0, NULL, NULL, '2026-01-05 18:06:43', '2026-01-05 18:06:43'),
(11, 'Nguyễn Minh Khôi', '0977827638', '2000-07-20', 'NAM', NULL, 0, NULL, NULL, '2026-01-14 07:01:05', '2026-01-14 07:01:05'),
(12, 'Phạm Thanh Thảo', '0939587039', '1994-12-22', 'NU', NULL, 0, NULL, NULL, '2026-02-20 07:35:12', '2026-02-20 07:35:12'),
(13, 'Hoàng Văn Nam', '0931429110', '1993-04-03', 'NAM', NULL, 0, NULL, NULL, '2026-02-15 16:17:51', '2026-02-15 16:17:51'),
(14, 'Bùi Thị Tuyết', '0955176955', '2001-04-05', 'NAM', NULL, 0, NULL, NULL, '2026-02-23 13:21:17', '2026-02-23 13:21:17'),
(15, 'Vũ Hoàng Long', '0991030736', '1998-12-23', 'NU', NULL, 0, NULL, NULL, '2026-02-04 08:24:06', '2026-02-04 08:24:06'),
(16, 'Đỗ Minh Tuấn', '0960806024', '1997-11-07', 'NAM', NULL, 0, NULL, NULL, '2026-02-09 19:02:46', '2026-02-09 19:02:46'),
(17, 'Phan Thanh Sơn', '0987490893', '1995-12-15', 'NU', NULL, 0, NULL, NULL, '2026-02-03 15:18:53', '2026-02-03 15:18:53'),
(18, 'Ngô Quỳnh Chi', '0948840994', '1995-08-03', 'NAM', NULL, 0, NULL, NULL, '2026-02-07 18:04:02', '2026-02-07 18:04:02'),
(19, 'Dương Quốc Anh', '0947308985', '2001-11-14', 'NU', NULL, 0, NULL, NULL, '2026-02-03 20:14:55', '2026-02-03 20:14:55'),
(20, 'Lý Hoài An', '0957683626', '2001-03-06', 'NU', NULL, 0, NULL, NULL, '2026-02-15 17:53:23', '2026-02-15 17:53:23'),
(21, 'Võ Thị Hằng', '0991756179', '1995-05-04', 'NAM', NULL, 0, NULL, NULL, '2026-03-07 17:17:44', '2026-03-07 17:17:44'),
(22, 'Đặng Minh Trí', '0972043515', '2000-04-04', 'NAM', NULL, 0, NULL, NULL, '2026-03-21 09:34:46', '2026-03-21 09:34:46'),
(23, 'Bùi Huy Khánh', '0953524491', '1995-04-15', 'NAM', NULL, 0, NULL, NULL, '2026-03-13 11:59:40', '2026-03-13 11:59:40'),
(24, 'Nguyễn Thị Ngọc', '0952339391', '2000-06-07', 'NAM', NULL, 0, NULL, NULL, '2026-03-27 19:49:03', '2026-03-27 19:49:03'),
(25, 'Trần Huy Hoàng', '0938538251', '1996-08-22', 'NU', NULL, 0, NULL, NULL, '2026-03-13 11:04:13', '2026-03-13 11:04:13'),
(26, 'Lê Gia Bảo', '0929175900', '1995-10-17', 'NU', NULL, 0, NULL, NULL, '2026-03-21 14:25:56', '2026-03-21 14:25:56'),
(27, 'Phạm Minh Đức', '0988461803', '1996-09-15', 'NU', NULL, 0, NULL, NULL, '2026-03-09 09:15:47', '2026-03-09 09:15:47'),
(28, 'Hoàng Kim Ngân', '0928566572', '1998-12-11', 'NAM', NULL, 0, NULL, NULL, '2026-03-14 21:37:25', '2026-03-14 21:37:25'),
(29, 'Đỗ Thùy Linh', '0930514014', '2002-06-23', 'NAM', NULL, 0, NULL, NULL, '2026-03-17 14:05:48', '2026-03-17 14:05:48'),
(30, 'Phan Anh Tuấn', '0961642594', '1998-04-08', 'NAM', NULL, 0, NULL, NULL, '2026-03-21 09:50:43', '2026-03-21 09:50:43'),
(31, 'Ngô Minh Hằng', '0925374874', '2000-03-08', 'NAM', NULL, 0, NULL, NULL, '2026-03-13 16:29:33', '2026-03-13 16:29:33'),
(32, 'Dương Gia Khánh', '0924972279', '2000-01-05', 'NU', NULL, 0, NULL, NULL, '2026-03-22 21:34:48', '2026-03-22 21:34:48'),
(33, 'Võ Minh Triết', '0977187530', '2002-12-19', 'NU', NULL, 0, NULL, NULL, '2026-03-10 13:10:29', '2026-03-10 13:10:29'),
(34, 'Trần Ngọc Hải', '0995758349', '2001-10-23', 'NU', NULL, 0, NULL, NULL, '2026-04-25 09:32:58', '2026-04-25 09:32:58'),
(35, 'Nguyễn Hoàng Nam', '0982394227', '1998-10-23', 'NAM', NULL, 0, NULL, NULL, '2026-04-17 16:12:09', '2026-04-17 16:12:09'),
(36, 'Lê Thị Mai', '0975579548', '2002-12-30', 'NU', NULL, 0, NULL, NULL, '2026-04-25 21:33:58', '2026-04-25 21:33:58'),
(37, 'Phạm Văn Đông', '0942138745', '1993-02-23', 'NU', NULL, 0, NULL, NULL, '2026-04-01 08:59:23', '2026-04-01 08:59:23'),
(38, 'Hoàng Quốc Việt', '0975228535', '2002-02-13', 'NAM', NULL, 0, NULL, NULL, '2026-04-02 10:56:36', '2026-04-02 10:56:36'),
(39, 'Đỗ Mai Phương', '0927232410', '1994-06-01', 'NAM', NULL, 0, NULL, NULL, '2026-04-27 08:48:34', '2026-04-27 08:48:34'),
(40, 'Phan Văn Hùng', '0938427073', '2000-01-12', 'NU', NULL, 0, NULL, NULL, '2026-04-22 14:35:10', '2026-04-22 14:35:10'),
(41, 'Ngô Thanh Vân', '0963551839', '2000-09-30', 'NU', NULL, 0, NULL, NULL, '2026-05-18 19:46:44', '2026-05-18 19:46:44'),
(42, 'Dương Hoàng Long', '0926240908', '1997-03-14', 'NU', NULL, 0, NULL, NULL, '2026-05-22 17:23:28', '2026-05-22 17:23:28'),
(43, 'Võ Thị Dung', '0988979095', '2002-10-07', 'NAM', NULL, 0, NULL, NULL, '2026-05-08 10:04:21', '2026-05-08 10:04:21'),
(44, 'Trần Quốc Bảo', '0940728046', '1995-12-05', 'NAM', NULL, 0, NULL, NULL, '2026-05-08 07:04:45', '2026-05-08 07:04:45'),
(45, 'Nguyễn Lan Anh', '0979008866', '1999-04-19', 'NAM', NULL, 0, NULL, NULL, '2026-05-03 21:02:55', '2026-05-03 21:02:55'),
(46, 'Lê Minh Quân', '0986644106', '2000-08-07', 'NAM', NULL, 0, NULL, NULL, '2026-05-08 11:42:31', '2026-05-08 11:42:31'),
(47, 'Phạm Hoài Nam', '0935556386', '1997-09-12', 'NU', NULL, 0, NULL, NULL, '2026-05-19 14:15:50', '2026-05-19 14:15:50'),
(48, 'Hoàng Thu Trang', '0965177213', '1999-01-11', 'NU', NULL, 0, NULL, NULL, '2026-05-04 08:42:27', '2026-05-04 08:42:27'),
(49, 'Đỗ Văn Tiến', '0918135295', '1995-06-14', 'NAM', NULL, 0, NULL, NULL, '2026-05-15 20:46:03', '2026-05-15 20:46:03'),
(50, 'Phan Thị Hồng', '0943374088', '1993-05-04', 'NAM', NULL, 0, NULL, NULL, '2026-05-13 18:21:51', '2026-05-13 18:21:51'),
(51, 'Ngô Tiến Dũng', '0934627347', '2001-06-06', 'NU', NULL, 0, NULL, NULL, '2026-05-07 10:34:28', '2026-05-07 10:34:28'),
(52, 'Dương Mỹ Linh', '0983863413', '2002-02-27', 'NU', NULL, 0, NULL, NULL, '2026-05-09 14:15:55', '2026-05-09 14:15:55'),
(53, 'Võ Minh Đức', '0922517517', '1993-08-17', 'NAM', NULL, 0, NULL, NULL, '2026-05-04 07:41:34', '2026-05-04 07:41:34'),
(54, 'Trần Gia Hân', '0974606833', '1998-06-12', 'NU', NULL, 0, NULL, NULL, '2026-05-25 20:15:10', '2026-05-25 20:15:10'),
(55, 'Nguyễn Tuấn Kiệt', '0960864911', '2002-05-06', 'NAM', NULL, 0, NULL, NULL, '2026-05-07 20:25:57', '2026-05-07 20:25:57'),
(56, 'Lê Quỳnh Anh', '0948285503', '1994-03-18', 'NU', NULL, 0, NULL, NULL, '2026-06-01 13:16:59', '2026-06-01 13:16:59'),
(57, 'Phạm Thanh Hải', '0930776478', '1996-10-08', 'NU', NULL, 0, NULL, NULL, '2026-06-14 18:46:50', '2026-06-14 18:46:50'),
(58, 'Hoàng Phi Hùng', '0952091325', '1996-07-04', 'NAM', NULL, 0, NULL, NULL, '2026-06-07 11:13:03', '2026-06-07 11:13:03'),
(59, 'Đỗ Minh Triết', '0917634247', '1997-05-13', 'NAM', NULL, 0, NULL, NULL, '2026-06-02 07:37:30', '2026-06-02 07:37:30'),
(60, 'Phan Gia Lạc', '0941568532', '2002-03-27', 'NAM', NULL, 0, NULL, NULL, '2026-06-17 08:54:11', '2026-06-17 08:54:11'),
(61, 'Ngô Văn Đạt', '0993131979', '2000-03-29', 'NAM', NULL, 0, NULL, NULL, '2026-06-13 08:56:36', '2026-06-13 08:56:36'),
(62, 'Dương Thùy Trang', '0944999379', '1996-08-30', 'NU', NULL, 0, NULL, NULL, '2026-06-03 13:42:37', '2026-06-03 13:42:37'),
(63, 'Võ Thị Bích', '0963121477', '2000-04-29', 'NU', NULL, 0, NULL, NULL, '2026-06-07 17:45:20', '2026-06-07 17:45:20'),
(64, 'Trần Anh Dũng', '0919736572', '1997-11-16', 'NU', NULL, 0, NULL, NULL, '2026-06-05 17:41:19', '2026-06-05 17:41:19'),
(65, 'Nguyễn Khánh Linh', '0982160068', '2001-11-18', 'NAM', NULL, 0, NULL, NULL, '2026-06-01 14:39:36', '2026-06-01 14:39:36'),
(66, 'Lê Hữu Đạt', '0942787299', '1999-02-02', 'NAM', NULL, 0, NULL, NULL, '2026-06-07 15:16:08', '2026-06-07 15:16:08');

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
(2, 9, 'CHI', 260000.00, 'Khám răng định kỳ và lấy cao răng', '2026-01-02', 'THU_CONG', NULL),
(2, 11, 'CHI', 2480000.00, 'Tiền thuê phòng trọ trọn gói', '2026-01-04', 'THU_CONG', NULL),
(2, 6, 'CHI', 500000.00, 'Mua tai nghe bluetooth Baseus', '2026-01-05', 'THU_CONG', NULL),
(2, 6, 'CHI', 180000.00, 'Mua sữa rửa mặt, dầu gội đầu ở siêu thị', '2026-01-06', 'THU_CONG', NULL),
(2, 4, 'CHI', 88000.00, 'Ăn tối bún đậu mắm tôm cùng bạn', '2026-01-08', 'THU_CONG', NULL),
(2, 4, 'CHI', 360000.00, 'Đi ăn lẩu Haidilao cuối tuần', '2026-01-08', 'THU_CONG', NULL),
(2, 9, 'CHI', 800000.00, 'Mua bảo hiểm y tế tự nguyện', '2026-01-10', 'RULE_BASED', 79.70),
(2, 5, 'CHI', 48000.00, 'Đặt xe ôm Grab đi làm trời mưa', '2026-01-11', 'MACHINE_LEARNING', 86.02),
(2, 6, 'CHI', 710000.00, 'Mua giày chạy bộ Bitis Hunter', '2026-01-13', 'MACHINE_LEARNING', 78.96),
(2, 10, 'CHI', 390000.00, 'Đóng tiền điện sinh hoạt gia đình', '2026-01-16', 'MACHINE_LEARNING', 79.15),
(2, 3, 'THU', 2750000.00, 'Làm thêm Freelance thiết kế website', '2026-01-17', 'THU_CONG', NULL),
(2, 10, 'CHI', 410000.00, 'Đóng tiền điện sinh hoạt gia đình', '2026-01-20', 'THU_CONG', NULL),
(2, 7, 'CHI', 340000.00, 'Mua game Steam đợt Summer Sales', '2026-01-21', 'MACHINE_LEARNING', 81.57),
(2, 7, 'CHI', 360000.00, 'Mua game Steam đợt Summer Sales', '2026-01-22', 'MACHINE_LEARNING', 99.17),
(2, 4, 'CHI', 100000.00, 'Ăn tối bún đậu mắm tôm cùng bạn', '2026-01-23', 'MACHINE_LEARNING', 85.61),
(2, 6, 'CHI', 340000.00, 'Mua quần jeans nam dáng suông', '2026-01-24', 'RULE_BASED', 85.18),
(2, 5, 'CHI', 100000.00, 'Mua vé xe bus tháng đi học', '2026-01-24', 'RULE_BASED', 98.89),
(2, 3, 'THU', 59000.00, 'Hoàn tiền mua sắm Shopee Pay', '2026-01-24', 'RULE_BASED', 92.21),
(2, 7, 'CHI', 290000.00, 'Đi hát Karaoke cuối tuần với team', '2026-01-25', 'RULE_BASED', 78.20),
(2, 10, 'CHI', 300000.00, 'Đóng tiền điện sinh hoạt gia đình', '2026-01-26', 'THU_CONG', NULL),
(2, 4, 'CHI', 44000.00, 'Ăn sáng phở bò tái nạm', '2026-01-28', 'RULE_BASED', 92.01),
(2, 12, 'CHI', 320000.00, 'Mua quà sinh nhật cho đồng nghiệp', '2026-01-28', 'THU_CONG', NULL),
(2, 10, 'CHI', 69000.00, 'Thanh toán hóa đơn nước sinh hoạt', '2026-01-28', 'THU_CONG', NULL),
(2, 9, 'CHI', 35000.00, 'Mua thuốc cảm cúm, vitamin C Pharmacity', '2026-01-28', 'RULE_BASED', 75.98),
(2, 7, 'CHI', 260000.00, 'Đăng ký gói Netflix Premium 1 tháng', '2026-01-29', 'RULE_BASED', 79.34),
(2, 7, 'CHI', 260000.00, 'Đăng ký gói Netflix Premium 1 tháng', '2026-02-02', 'RULE_BASED', 95.62),
(2, 7, 'CHI', 330000.00, 'Mua game Steam đợt Summer Sales', '2026-02-02', 'MACHINE_LEARNING', 88.69),
(2, 11, 'CHI', 2400000.00, 'Tiền thuê phòng trọ trọn gói', '2026-02-04', 'THU_CONG', NULL),
(2, 6, 'CHI', 520000.00, 'Mua tai nghe bluetooth Baseus', '2026-02-04', 'MACHINE_LEARNING', 92.59),
(2, 4, 'CHI', 98000.00, 'Ăn tối bún đậu mắm tôm cùng bạn', '2026-02-04', 'THU_CONG', NULL),
(2, 5, 'CHI', 7000.00, 'Vé gửi xe máy chung cư', '2026-02-06', 'THU_CONG', NULL),
(2, 4, 'CHI', 61000.00, 'Mua trà sữa Gong Cha trưa', '2026-02-06', 'RULE_BASED', 77.28),
(2, 12, 'CHI', 97000.00, 'Làm mất ví, hao hụt tiền mặt không rõ', '2026-02-08', 'THU_CONG', NULL),
(2, 3, 'THU', 56000.00, 'Hoàn tiền mua sắm Shopee Pay', '2026-02-11', 'THU_CONG', NULL),
(2, 7, 'CHI', 170000.00, 'Vé xem phim CGV rạp IMAX', '2026-02-11', 'RULE_BASED', 93.31),
(2, 8, 'CHI', 71000.00, 'Mua văn phòng phẩm viết vở thước kẻ', '2026-02-11', 'THU_CONG', NULL),
(2, 3, 'THU', 74000.00, 'Hoàn tiền mua sắm Shopee Pay', '2026-02-11', 'THU_CONG', NULL),
(2, 4, 'CHI', 55000.00, 'Uống cafe Highlands cùng đối tác', '2026-02-12', 'THU_CONG', NULL),
(2, 7, 'CHI', 1880000.00, 'Chi phí đi du lịch Vũng Tàu 2 ngày', '2026-02-12', 'THU_CONG', NULL),
(2, 10, 'CHI', 220000.00, 'Thanh toán tiền mạng Internet Wifi Viettel', '2026-02-12', 'THU_CONG', NULL),
(2, 10, 'CHI', 400000.00, 'Đóng tiền điện sinh hoạt gia đình', '2026-02-13', 'RULE_BASED', 80.68),
(2, 5, 'CHI', 100000.00, 'Mua vé xe bus tháng đi học', '2026-02-14', 'RULE_BASED', 75.85),
(2, 8, 'CHI', 350000.00, 'Đăng ký khóa học Udemy thiết kế UI/UX', '2026-02-14', 'RULE_BASED', 87.98),
(2, 4, 'CHI', 39000.00, 'Cơm tấm sườn bì chả trưa', '2026-02-15', 'THU_CONG', NULL),
(2, 2, 'THU', 1720000.00, 'Tiền thưởng dự án hoàn thành xuất sắc', '2026-02-16', 'THU_CONG', NULL),
(2, 9, 'CHI', 800000.00, 'Mua bảo hiểm y tế tự nguyện', '2026-02-16', 'MACHINE_LEARNING', 88.42),
(2, 6, 'CHI', 350000.00, 'Mua quần jeans nam dáng suông', '2026-02-18', 'MACHINE_LEARNING', 88.84),
(2, 12, 'CHI', 220000.00, 'Mua quà sinh nhật cho đồng nghiệp', '2026-02-19', 'THU_CONG', NULL),
(2, 4, 'CHI', 27000.00, 'Cà phê sữa đá Aha vỉa hè', '2026-02-19', 'RULE_BASED', 92.73),
(2, 3, 'THU', 92000.00, 'Hoàn tiền mua sắm Shopee Pay', '2026-02-20', 'THU_CONG', NULL),
(2, 4, 'CHI', 31000.00, 'Cà phê sữa đá Aha vỉa hè', '2026-02-24', 'RULE_BASED', 85.95),
(2, 8, 'CHI', 42000.00, 'Mua văn phòng phẩm viết vở thước kẻ', '2026-02-24', 'RULE_BASED', 98.49),
(2, 6, 'CHI', 320000.00, 'Mua quần jeans nam dáng suông', '2026-02-25', 'MACHINE_LEARNING', 95.24),
(2, 2, 'THU', 2850000.00, 'Tiền thưởng dự án hoàn thành xuất sắc', '2026-02-26', 'MACHINE_LEARNING', 95.09),
(2, 6, 'CHI', 390000.00, 'Mua tai nghe bluetooth Baseus', '2026-02-26', 'THU_CONG', NULL),
(2, 7, 'CHI', 2300000.00, 'Chi phí đi du lịch Vũng Tàu 2 ngày', '2026-02-27', 'THU_CONG', NULL),
(2, 9, 'CHI', 800000.00, 'Mua bảo hiểm y tế tự nguyện', '2026-02-27', 'THU_CONG', NULL),
(2, 1, 'THU', 12450000.00, 'Nhận lương tháng công ty', '2026-03-01', 'THU_CONG', NULL),
(2, 11, 'CHI', 2280000.00, 'Tiền thuê phòng trọ trọn gói', '2026-03-04', 'RULE_BASED', 76.39),
(2, 6, 'CHI', 340000.00, 'Mua áo khoác gió Shopee', '2026-03-06', 'RULE_BASED', 90.06),
(2, 7, 'CHI', 170000.00, 'Vé xem phim CGV rạp IMAX', '2026-03-08', 'RULE_BASED', 86.02),
(2, 5, 'CHI', 100000.00, 'Mua vé xe bus tháng đi học', '2026-03-10', 'THU_CONG', NULL),
(2, 5, 'CHI', 62000.00, 'Đổ xăng đầy bình xe máy', '2026-03-13', 'THU_CONG', NULL),
(2, 4, 'CHI', 48000.00, 'Mua trà sữa Gong Cha trưa', '2026-03-15', 'MACHINE_LEARNING', 84.91),
(2, 5, 'CHI', 8000.00, 'Vé gửi xe máy chung cư', '2026-03-17', 'MACHINE_LEARNING', 76.01),
(2, 2, 'THU', 2630000.00, 'Tiền thưởng dự án hoàn thành xuất sắc', '2026-03-19', 'THU_CONG', NULL),
(2, 10, 'CHI', 400000.00, 'Đóng tiền điện sinh hoạt gia đình', '2026-03-19', 'THU_CONG', NULL),
(2, 5, 'CHI', 79000.00, 'Đổ xăng đầy bình xe máy', '2026-03-21', 'THU_CONG', NULL),
(2, 5, 'CHI', 6000.00, 'Vé gửi xe máy chung cư', '2026-03-22', 'THU_CONG', NULL),
(2, 6, 'CHI', 840000.00, 'Mua giày chạy bộ Bitis Hunter', '2026-03-22', 'MACHINE_LEARNING', 90.97),
(2, 4, 'CHI', 60000.00, 'Mua trà sữa Gong Cha trưa', '2026-03-23', 'THU_CONG', NULL),
(2, 10, 'CHI', 79000.00, 'Thanh toán hóa đơn nước sinh hoạt', '2026-03-23', 'RULE_BASED', 76.14),
(2, 10, 'CHI', 220000.00, 'Thanh toán tiền mạng Internet Wifi Viettel', '2026-03-24', 'THU_CONG', NULL),
(2, 7, 'CHI', 230000.00, 'Đi hát Karaoke cuối tuần với team', '2026-03-24', 'THU_CONG', NULL),
(2, 6, 'CHI', 410000.00, 'Mua tai nghe bluetooth Baseus', '2026-03-24', 'MACHINE_LEARNING', 92.87),
(2, 12, 'CHI', 140000.00, 'Làm mất ví, hao hụt tiền mặt không rõ', '2026-03-25', 'MACHINE_LEARNING', 90.15),
(2, 3, 'THU', 110000.00, 'Hoàn tiền mua sắm Shopee Pay', '2026-03-27', 'MACHINE_LEARNING', 93.27),
(2, 10, 'CHI', 87000.00, 'Nạp tiền điện thoại Viettel trả trước', '2026-03-28', 'RULE_BASED', 79.81),
(2, 9, 'CHI', 44000.00, 'Mua thuốc cảm cúm, vitamin C Pharmacity', '2026-03-28', 'RULE_BASED', 83.04),
(2, 10, 'CHI', 330000.00, 'Đóng tiền điện sinh hoạt gia đình', '2026-03-28', 'THU_CONG', NULL),
(2, 8, 'CHI', 1620000.00, 'Đóng tiền học phí ôn luyện IELTS tháng', '2026-03-28', 'RULE_BASED', 79.53),
(2, 4, 'CHI', 28000.00, 'Cà phê sữa đá Aha vỉa hè', '2026-03-29', 'THU_CONG', NULL),
(2, 6, 'CHI', 220000.00, 'Mua sữa rửa mặt, dầu gội đầu ở siêu thị', '2026-03-30', 'RULE_BASED', 82.70),
(2, 5, 'CHI', 48000.00, 'Đặt xe ôm Grab đi làm trời mưa', '2026-03-31', 'THU_CONG', NULL),
(2, 1, 'THU', 12610000.00, 'Nhận lương tháng công ty', '2026-04-01', 'RULE_BASED', 75.16),
(2, 2, 'THU', 1550000.00, 'Tiền thưởng dự án hoàn thành xuất sắc', '2026-04-01', 'RULE_BASED', 95.95),
(2, 9, 'CHI', 800000.00, 'Mua bảo hiểm y tế tự nguyện', '2026-04-02', 'RULE_BASED', 83.49),
(2, 3, 'THU', 130000.00, 'Hoàn tiền mua sắm Shopee Pay', '2026-04-04', 'THU_CONG', NULL),
(2, 11, 'CHI', 2320000.00, 'Tiền thuê phòng trọ trọn gói', '2026-04-05', 'THU_CONG', NULL),
(2, 4, 'CHI', 63000.00, 'Mua trà sữa Gong Cha trưa', '2026-04-06', 'MACHINE_LEARNING', 79.38),
(2, 5, 'CHI', 8000.00, 'Vé gửi xe máy chung cư', '2026-04-06', 'THU_CONG', NULL),
(2, 8, 'CHI', 1690000.00, 'Đóng tiền học phí ôn luyện IELTS tháng', '2026-04-07', 'THU_CONG', NULL),
(2, 5, 'CHI', 67000.00, 'Đặt xe ôm Grab đi làm trời mưa', '2026-04-07', 'THU_CONG', NULL),
(2, 9, 'CHI', 78000.00, 'Mua thuốc cảm cúm, vitamin C Pharmacity', '2026-04-08', 'MACHINE_LEARNING', 75.83),
(2, 7, 'CHI', 2760000.00, 'Chi phí đi du lịch Vũng Tàu 2 ngày', '2026-04-10', 'RULE_BASED', 95.36),
(2, 12, 'CHI', 300000.00, 'Mua quà sinh nhật cho đồng nghiệp', '2026-04-10', 'THU_CONG', NULL),
(2, 5, 'CHI', 140000.00, 'Đi taxi Grab cùng đồng nghiệp', '2026-04-11', 'THU_CONG', NULL),
(2, 6, 'CHI', 220000.00, 'Mua sữa rửa mặt, dầu gội đầu ở siêu thị', '2026-04-13', 'MACHINE_LEARNING', 89.75),
(2, 2, 'THU', 1990000.00, 'Tiền thưởng dự án hoàn thành xuất sắc', '2026-04-14', 'MACHINE_LEARNING', 76.06),
(2, 3, 'THU', 100000.00, 'Hoàn tiền mua sắm Shopee Pay', '2026-04-15', 'MACHINE_LEARNING', 86.77),
(2, 10, 'CHI', 220000.00, 'Thanh toán tiền mạng Internet Wifi Viettel', '2026-04-15', 'THU_CONG', NULL),
(2, 8, 'CHI', 320000.00, 'Đăng ký khóa học Udemy thiết kế UI/UX', '2026-04-17', 'RULE_BASED', 80.80),
(2, 6, 'CHI', 260000.00, 'Mua áo khoác gió Shopee', '2026-04-17', 'MACHINE_LEARNING', 93.20),
(2, 7, 'CHI', 260000.00, 'Đăng ký gói Netflix Premium 1 tháng', '2026-04-18', 'THU_CONG', NULL),
(2, 3, 'THU', 52000.00, 'Hoàn tiền mua sắm Shopee Pay', '2026-04-19', 'MACHINE_LEARNING', 75.52),
(2, 4, 'CHI', 45000.00, 'Ăn sáng phở bò tái nạm', '2026-04-21', 'RULE_BASED', 99.09),
(2, 2, 'THU', 1850000.00, 'Tiền thưởng dự án hoàn thành xuất sắc', '2026-04-21', 'MACHINE_LEARNING', 95.45),
(2, 5, 'CHI', 100000.00, 'Mua vé xe bus tháng đi học', '2026-04-22', 'RULE_BASED', 93.06),
(2, 9, 'CHI', 290000.00, 'Khám răng định kỳ và lấy cao răng', '2026-04-22', 'MACHINE_LEARNING', 96.62),
(2, 8, 'CHI', 1400000.00, 'Đóng tiền học phí ôn luyện IELTS tháng', '2026-04-23', 'THU_CONG', NULL),
(2, 7, 'CHI', 230000.00, 'Mua game Steam đợt Summer Sales', '2026-04-23', 'MACHINE_LEARNING', 93.10),
(2, 9, 'CHI', 800000.00, 'Mua bảo hiểm y tế tự nguyện', '2026-04-24', 'RULE_BASED', 94.62),
(2, 8, 'CHI', 1480000.00, 'Đóng tiền học phí ôn luyện IELTS tháng', '2026-04-25', 'RULE_BASED', 94.83),
(2, 8, 'CHI', 50000.00, 'Mua văn phòng phẩm viết vở thước kẻ', '2026-04-25', 'MACHINE_LEARNING', 86.12),
(2, 6, 'CHI', 740000.00, 'Mua giày chạy bộ Bitis Hunter', '2026-04-27', 'MACHINE_LEARNING', 85.79),
(2, 3, 'THU', 4470000.00, 'Làm thêm Freelance thiết kế website', '2026-04-27', 'RULE_BASED', 98.41),
(2, 10, 'CHI', 83000.00, 'Thanh toán hóa đơn nước sinh hoạt', '2026-04-27', 'MACHINE_LEARNING', 98.72),
(2, 6, 'CHI', 210000.00, 'Mua áo khoác gió Shopee', '2026-04-28', 'RULE_BASED', 89.26),
(2, 5, 'CHI', 180000.00, 'Đi taxi Grab cùng đồng nghiệp', '2026-04-29', 'THU_CONG', NULL),
(2, 1, 'THU', 13860000.00, 'Nhận lương tháng công ty', '2026-05-01', 'THU_CONG', NULL),
(2, 8, 'CHI', 41000.00, 'Mua văn phòng phẩm viết vở thước kẻ', '2026-05-02', 'THU_CONG', NULL),
(2, 11, 'CHI', 2210000.00, 'Tiền thuê phòng trọ trọn gói', '2026-05-05', 'THU_CONG', NULL),
(2, 6, 'CHI', 740000.00, 'Mua giày chạy bộ Bitis Hunter', '2026-05-05', 'RULE_BASED', 88.62),
(2, 4, 'CHI', 62000.00, 'Uống cafe Highlands cùng đối tác', '2026-05-05', 'MACHINE_LEARNING', 88.88),
(2, 7, 'CHI', 270000.00, 'Đi hát Karaoke cuối tuần với team', '2026-05-06', 'MACHINE_LEARNING', 90.47),
(2, 4, 'CHI', 440000.00, 'Đi ăn lẩu Haidilao cuối tuần', '2026-05-07', 'RULE_BASED', 88.36),
(2, 9, 'CHI', 800000.00, 'Mua bảo hiểm y tế tự nguyện', '2026-05-07', 'MACHINE_LEARNING', 79.88),
(2, 5, 'CHI', 76000.00, 'Đổ xăng đầy bình xe máy', '2026-05-09', 'THU_CONG', NULL),
(2, 6, 'CHI', 490000.00, 'Mua tai nghe bluetooth Baseus', '2026-05-09', 'RULE_BASED', 85.13),
(2, 6, 'CHI', 270000.00, 'Mua quần jeans nam dáng suông', '2026-05-10', 'RULE_BASED', 93.47),
(2, 5, 'CHI', 6000.00, 'Vé gửi xe máy chung cư', '2026-05-11', 'MACHINE_LEARNING', 88.77),
(2, 12, 'CHI', 500000.00, 'Chi phí linh tinh đi đám cưới bạn cấp 3', '2026-05-12', 'MACHINE_LEARNING', 76.96),
(2, 6, 'CHI', 270000.00, 'Mua áo khoác gió Shopee', '2026-05-12', 'THU_CONG', NULL),
(2, 6, 'CHI', 380000.00, 'Mua tai nghe bluetooth Baseus', '2026-05-14', 'MACHINE_LEARNING', 81.46),
(2, 5, 'CHI', 52000.00, 'Đổ xăng đầy bình xe máy', '2026-05-16', 'MACHINE_LEARNING', 91.19),
(2, 9, 'CHI', 56000.00, 'Mua thuốc cảm cúm, vitamin C Pharmacity', '2026-05-16', 'THU_CONG', NULL),
(2, 6, 'CHI', 390000.00, 'Mua quần jeans nam dáng suông', '2026-05-16', 'MACHINE_LEARNING', 81.81),
(2, 4, 'CHI', 44000.00, 'Ăn sáng phở bò tái nạm', '2026-05-16', 'RULE_BASED', 89.06),
(2, 8, 'CHI', 1250000.00, 'Đóng tiền học phí ôn luyện IELTS tháng', '2026-05-16', 'RULE_BASED', 84.68),
(2, 12, 'CHI', 170000.00, 'Làm mất ví, hao hụt tiền mặt không rõ', '2026-05-18', 'THU_CONG', NULL),
(2, 7, 'CHI', 170000.00, 'Vé xem phim CGV rạp IMAX', '2026-05-18', 'RULE_BASED', 78.44),
(2, 3, 'THU', 280000.00, 'Bán quần áo cũ không dùng trên Group', '2026-05-18', 'THU_CONG', NULL),
(2, 4, 'CHI', 49000.00, 'Cơm tấm sườn bì chả trưa', '2026-05-21', 'MACHINE_LEARNING', 88.56),
(2, 10, 'CHI', 97000.00, 'Nạp tiền điện thoại Viettel trả trước', '2026-05-22', 'RULE_BASED', 76.61),
(2, 3, 'THU', 110000.00, 'Hoàn tiền mua sắm Shopee Pay', '2026-05-23', 'MACHINE_LEARNING', 93.75),
(2, 5, 'CHI', 37000.00, 'Đặt xe ôm Grab đi làm trời mưa', '2026-05-23', 'THU_CONG', NULL),
(2, 3, 'THU', 4220000.00, 'Làm thêm Freelance thiết kế website', '2026-05-25', 'RULE_BASED', 80.71),
(2, 12, 'CHI', 180000.00, 'Làm mất ví, hao hụt tiền mặt không rõ', '2026-05-25', 'MACHINE_LEARNING', 75.30),
(2, 8, 'CHI', 130000.00, 'Mua sách chuyên ngành lập trình Python', '2026-05-25', 'RULE_BASED', 97.50),
(2, 12, 'CHI', 500000.00, 'Chi phí linh tinh đi đám cưới bạn cấp 3', '2026-05-26', 'RULE_BASED', 96.32),
(2, 7, 'CHI', 260000.00, 'Đi hát Karaoke cuối tuần với team', '2026-05-27', 'MACHINE_LEARNING', 99.16),
(2, 9, 'CHI', 800000.00, 'Mua bảo hiểm y tế tự nguyện', '2026-05-27', 'MACHINE_LEARNING', 94.35),
(2, 8, 'CHI', 440000.00, 'Đăng ký khóa học Udemy thiết kế UI/UX', '2026-05-28', 'THU_CONG', NULL),
(2, 2, 'THU', 1830000.00, 'Tiền thưởng dự án hoàn thành xuất sắc', '2026-05-28', 'RULE_BASED', 90.35),
(2, 6, 'CHI', 280000.00, 'Mua quần jeans nam dáng suông', '2026-05-28', 'THU_CONG', NULL),
(2, 4, 'CHI', 450000.00, 'Đi ăn lẩu Haidilao cuối tuần', '2026-05-28', 'THU_CONG', NULL),
(2, 4, 'CHI', 89000.00, 'Ăn tối bún đậu mắm tôm cùng bạn', '2026-05-29', 'MACHINE_LEARNING', 81.91),
(2, 5, 'CHI', 100000.00, 'Mua vé xe bus tháng đi học', '2026-05-30', 'THU_CONG', NULL),
(2, 6, 'CHI', 430000.00, 'Mua tai nghe bluetooth Baseus', '2026-05-30', 'THU_CONG', NULL),
(2, 1, 'THU', 14100000.00, 'Nhận lương tháng công ty', '2026-06-01', 'RULE_BASED', 83.58),
(2, 10, 'CHI', 340000.00, 'Đóng tiền điện sinh hoạt gia đình', '2026-06-01', 'MACHINE_LEARNING', 86.03),
(2, 4, 'CHI', 40000.00, 'Ăn sáng phở bò tái nạm', '2026-06-03', 'MACHINE_LEARNING', 76.86),
(2, 10, 'CHI', 98000.00, 'Nạp tiền điện thoại Viettel trả trước', '2026-06-03', 'THU_CONG', NULL),
(2, 11, 'CHI', 2370000.00, 'Tiền thuê phòng trọ trọn gói', '2026-06-04', 'MACHINE_LEARNING', 84.59),
(2, 5, 'CHI', 5000.00, 'Vé gửi xe máy chung cư', '2026-06-05', 'THU_CONG', NULL),
(2, 5, 'CHI', 100000.00, 'Mua vé xe bus tháng đi học', '2026-06-05', 'MACHINE_LEARNING', 98.25),
(2, 4, 'CHI', 70000.00, 'Ăn tối bún đậu mắm tôm cùng bạn', '2026-06-06', 'RULE_BASED', 76.81),
(2, 5, 'CHI', 100000.00, 'Mua vé xe bus tháng đi học', '2026-06-06', 'MACHINE_LEARNING', 90.11),
(2, 7, 'CHI', 260000.00, 'Đi hát Karaoke cuối tuần với team', '2026-06-07', 'THU_CONG', NULL),
(2, 2, 'THU', 2050000.00, 'Tiền thưởng dự án hoàn thành xuất sắc', '2026-06-09', 'MACHINE_LEARNING', 80.07),
(2, 5, 'CHI', 100000.00, 'Mua vé xe bus tháng đi học', '2026-06-09', 'RULE_BASED', 78.40),
(2, 5, 'CHI', 6000.00, 'Vé gửi xe máy chung cư', '2026-06-11', 'MACHINE_LEARNING', 86.67),
(2, 6, 'CHI', 650000.00, 'Mua giày chạy bộ Bitis Hunter', '2026-06-13', 'THU_CONG', NULL),
(2, 8, 'CHI', 39000.00, 'Mua văn phòng phẩm viết vở thước kẻ', '2026-06-13', 'RULE_BASED', 88.47),
(2, 8, 'CHI', 390000.00, 'Đăng ký khóa học Udemy thiết kế UI/UX', '2026-06-15', 'MACHINE_LEARNING', 98.20),
(2, 5, 'CHI', 100000.00, 'Mua vé xe bus tháng đi học', '2026-06-15', 'RULE_BASED', 81.02),
(2, 3, 'THU', 370000.00, 'Bán quần áo cũ không dùng trên Group', '2026-06-16', 'RULE_BASED', 81.74),
(2, 4, 'CHI', 400000.00, 'Đi ăn lẩu Haidilao cuối tuần', '2026-06-16', 'MACHINE_LEARNING', 78.85),
(2, 7, 'CHI', 470000.00, 'Mua game Steam đợt Summer Sales', '2026-06-18', 'MACHINE_LEARNING', 86.32),
(2, 3, 'THU', 110000.00, 'Hoàn tiền mua sắm Shopee Pay', '2026-06-18', 'THU_CONG', NULL),
(2, 4, 'CHI', 38000.00, 'Cơm tấm sườn bì chả trưa', '2026-06-20', 'RULE_BASED', 94.71),
(2, 7, 'CHI', 170000.00, 'Vé xem phim CGV rạp IMAX', '2026-06-20', 'THU_CONG', NULL),
(2, 7, 'CHI', 260000.00, 'Đăng ký gói Netflix Premium 1 tháng', '2026-06-21', 'RULE_BASED', 80.11),
(2, 7, 'CHI', 260000.00, 'Đăng ký gói Netflix Premium 1 tháng', '2026-06-21', 'MACHINE_LEARNING', 90.53),
(2, 6, 'CHI', 210000.00, 'Mua áo khoác gió Shopee', '2026-06-22', 'THU_CONG', NULL),
(2, 12, 'CHI', 500000.00, 'Chi phí linh tinh đi đám cưới bạn cấp 3', '2026-06-24', 'MACHINE_LEARNING', 84.66),
(2, 9, 'CHI', 800000.00, 'Mua bảo hiểm y tế tự nguyện', '2026-06-24', 'RULE_BASED', 95.84),
(3, 1, 'THU', 12000000.00, 'Lương công ty', '2026-06-01', 'THU_CONG', NULL),
(3, 4, 'CHI', 95000.00, 'Cafe sáng', '2026-06-01', 'MACHINE_LEARNING', 91.30),
(3, 6, 'CHI', 650000.00, 'Mua áo mới', '2026-06-02', 'MACHINE_LEARNING', 86.70),
(3, 8, 'CHI', 299000.00, 'Mua khóa học Python', '2026-06-04', 'MACHINE_LEARNING', 94.10),
(4, 1, 'THU', 5000000.00, 'Lương part-time', '2026-06-01', 'THU_CONG', NULL),
(4, 4, 'CHI', 45000.00, 'Cơm trưa', '2026-06-02', 'RULE_BASED', 90.00),
(4, 7, 'CHI', 120000.00, 'Xem phim cuối tuần', '2026-06-03', 'RULE_BASED', 78.50),
(5, 1, 'THU', 15000000.00, 'Lương tháng 6', '2026-06-01', 'THU_CONG', NULL),
(5, 11, 'CHI', 3000000.00, 'Tiền thuê phòng', '2026-06-01', 'MACHINE_LEARNING', 89.20),
(5, 9, 'CHI', 450000.00, 'Khám sức khỏe', '2026-06-02', 'MACHINE_LEARNING', 83.40),
(6, 2, 'THU', 1000000.00, 'Tiền thưởng dự án', '2026-06-02', 'THU_CONG', NULL),
(6, 6, 'CHI', 850000.00, 'Mua tai nghe', '2026-06-03', 'RULE_BASED', 76.80),
(8, 3, 'THU', 2500000.00, 'Lãi đầu tư', '2026-06-04', 'THU_CONG', NULL),
(8, 10, 'CHI', 500000.00, 'Thanh toán internet', '2026-06-04', 'MACHINE_LEARNING', 87.90),
(8, 4, 'CHI', 180000.00, 'Ăn tối gia đình', '2026-06-05', 'MACHINE_LEARNING', 92.00);

-- =========================
-- NGÂN SÁCH
-- =========================
INSERT INTO ngan_sach 
(tai_khoan_id, danh_muc_id, thang, nam, han_muc) 
VALUES
(2, 4, 1, 2026, 800000.00),
(2, 5, 1, 2026, 3000000.00),
(2, 6, 1, 2026, 800000.00),
(2, 10, 1, 2026, 800000.00),
(2, 4, 2, 2026, 3000000.00),
(2, 5, 2, 2026, 1200000.00),
(2, 6, 2, 2026, 1500000.00),
(2, 10, 2, 2026, 800000.00),
(2, 4, 3, 2026, 800000.00),
(2, 5, 3, 2026, 3000000.00),
(2, 6, 3, 2026, 3000000.00),
(2, 10, 3, 2026, 1500000.00),
(2, 4, 4, 2026, 3000000.00),
(2, 5, 4, 2026, 800000.00),
(2, 6, 4, 2026, 2000000.00),
(2, 10, 4, 2026, 1500000.00),
(2, 4, 5, 2026, 800000.00),
(2, 5, 5, 2026, 1200000.00),
(2, 6, 5, 2026, 800000.00),
(2, 10, 5, 2026, 3000000.00),
(2, 4, 6, 2026, 3000000.00),
(2, 5, 6, 2026, 1500000.00),
(2, 6, 6, 2026, 1200000.00),
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
(2, 'ăn trưa cơm tấm sườn', 4, 95.00, 'Logistic Regression'),
(2, 'cơm trưa văn phòng', 4, 95.00, 'Logistic Regression'),
(2, 'Cà phê sữa đá Highlands', 4, 90.00, 'Logistic Regression'),
(2, 'Thưởng dự án Freelance', 2, 94.00, 'Logistic Regression'),
(2, 'Mua tai nghe chụp tai mới', 6, 91.00, 'Logistic Regression'),
(2, 'Thanh toán tiền mạng Internet', 10, 92.00, 'Logistic Regression'),
(2, 'Thanh toán hóa đơn tiền điện', 10, 84.25, 'Logistic Regression'),

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
(2, 7, 2026, 9150000.00, 89.50, 'GIAM'),
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
(2, 'BOT', 'Dữ liệu tháng này cho thấy bạn chi nhiều nhất cho danh mục Nhà ở (2,500,000 đ) và Ăn uống.'),
(2, 'USER', 'Tôi có đang chi vượt ngân sách không?'),
(2, 'BOT', 'Trong tháng 6 này, chi tiêu của bạn đang được kiểm soát rất tốt. Tuy nhiên trong tháng 5 trước đó, bạn đã chi vượt ngân sách các danh mục Ăn uống, Mua sắm và Giải trí.'),

(3, 'USER', 'Dự đoán chi tiêu tháng sau của tôi là bao nhiêu?'),
(3, 'BOT', 'Dựa trên dữ liệu hiện tại, chi tiêu tháng sau của bạn có thể khoảng 5,800,000đ.'),

(4, 'USER', 'Làm sao để tiết kiệm hơn?'),
(4, 'BOT', 'Bạn nên đặt ngân sách cho Ăn uống và Giải trí vì đây là hai danh mục chi nhiều.'),

(5, 'USER', 'Tôi có đang chi vượt ngân sách không?'),
(5, 'BOT', 'Bạn đang gần đạt giới hạn ngân sách Nhà ở, hãy theo dõi thêm trong tuần này.'),

(8, 'USER', 'Danh mục nào chi tiêu tăng mạnh nhất?'),
(8, 'BOT', 'Danh mục Hóa đơn có xu hướng tăng nhẹ so với tháng trước.');
