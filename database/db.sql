CREATE DATABASE quan_ly_chi_tieu_ai;
USE quan_ly_chi_tieu_ai;

-- =========================
-- 1. NGƯỜI DÙNG
-- =========================
CREATE TABLE nguoi_dung (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ho_ten VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    mat_khau_hash VARCHAR(255) NOT NULL,
    vai_tro ENUM('USER', 'PREMIUM', 'ADMIN') DEFAULT 'USER',
    trang_thai BOOLEAN DEFAULT TRUE,
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =========================
-- 2. GÓI PREMIUM
-- =========================
CREATE TABLE goi_premium (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nguoi_dung_id INT NOT NULL,
    ten_goi VARCHAR(50) DEFAULT 'PREMIUM',
    gia DECIMAL(12,2) NOT NULL,
    trang_thai ENUM('ACTIVE', 'EXPIRED', 'CANCELLED') DEFAULT 'ACTIVE',
    ngay_bat_dau DATETIME DEFAULT CURRENT_TIMESTAMP,
    ngay_ket_thuc DATETIME NOT NULL,
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (nguoi_dung_id) REFERENCES nguoi_dung(id)
        ON DELETE CASCADE
);

-- =========================
-- 3. DANH MỤC THU / CHI
-- =========================
CREATE TABLE danh_muc (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ten_danh_muc VARCHAR(100) NOT NULL,
    loai ENUM('THU', 'CHI') NOT NULL,
    icon VARCHAR(100),
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- 4. GIAO DỊCH
-- =========================
CREATE TABLE giao_dich (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nguoi_dung_id INT NOT NULL,
    danh_muc_id INT,
    loai ENUM('THU', 'CHI') NOT NULL,
    so_tien DECIMAL(12,2) NOT NULL,
    mo_ta TEXT,
    ngay_giao_dich DATE NOT NULL,
    phuong_thuc_phan_loai ENUM('THU_CONG', 'RULE_BASED', 'MACHINE_LEARNING') DEFAULT 'THU_CONG',
    do_tin_cay DECIMAL(5,2),
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (nguoi_dung_id) REFERENCES nguoi_dung(id)
        ON DELETE CASCADE,

    FOREIGN KEY (danh_muc_id) REFERENCES danh_muc(id)
        ON DELETE SET NULL
);

-- =========================
-- 5. NGÂN SÁCH
-- =========================
CREATE TABLE ngan_sach (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nguoi_dung_id INT NOT NULL,
    danh_muc_id INT,
    thang INT NOT NULL,
    nam INT NOT NULL,
    han_muc DECIMAL(12,2) NOT NULL,
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (nguoi_dung_id) REFERENCES nguoi_dung(id)
        ON DELETE CASCADE,

    FOREIGN KEY (danh_muc_id) REFERENCES danh_muc(id)
        ON DELETE SET NULL
);

-- =========================
-- 6. DỮ LIỆU HUẤN LUYỆN AI
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
-- 7. LỊCH SỬ AI PHÂN LOẠI
-- =========================
CREATE TABLE lich_su_ai_phan_loai (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nguoi_dung_id INT NOT NULL,
    van_ban_nhap TEXT,
    danh_muc_du_doan_id INT,
    do_tin_cay DECIMAL(5,2),
    ten_model VARCHAR(100),
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (nguoi_dung_id) REFERENCES nguoi_dung(id)
        ON DELETE CASCADE,

    FOREIGN KEY (danh_muc_du_doan_id) REFERENCES danh_muc(id)
        ON DELETE SET NULL
);

-- =========================
-- 8. LỊCH SỬ DỰ ĐOÁN CHI TIÊU
-- =========================
CREATE TABLE lich_su_du_doan_chi_tieu (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nguoi_dung_id INT NOT NULL,
    thang_du_doan INT NOT NULL,
    nam_du_doan INT NOT NULL,
    so_tien_du_doan DECIMAL(12,2) NOT NULL,
    do_tin_cay DECIMAL(5,2),
    xu_huong ENUM('TANG', 'GIAM', 'ON_DINH'),
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (nguoi_dung_id) REFERENCES nguoi_dung(id)
        ON DELETE CASCADE
);

-- =========================
-- 9. TIN NHẮN CHATBOT
-- =========================
CREATE TABLE tin_nhan_chatbot (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nguoi_dung_id INT NOT NULL,
    nguoi_gui ENUM('USER', 'BOT') NOT NULL,
    noi_dung TEXT NOT NULL,
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (nguoi_dung_id) REFERENCES nguoi_dung(id)
        ON DELETE CASCADE
);

-- =========================
-- 10. THANH TOÁN
-- =========================
CREATE TABLE thanh_toan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nguoi_dung_id INT NOT NULL,
    goi_premium_id INT,
    so_tien DECIMAL(12,2) NOT NULL,
    phuong_thuc_thanh_toan VARCHAR(50),
    trang_thai_thanh_toan ENUM('PENDING', 'SUCCESS', 'FAILED') DEFAULT 'PENDING',
    ma_giao_dich VARCHAR(100),
    ngay_thanh_toan DATETIME,
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (nguoi_dung_id) REFERENCES nguoi_dung(id)
        ON DELETE CASCADE,

    FOREIGN KEY (goi_premium_id) REFERENCES goi_premium(id)
        ON DELETE SET NULL
);