from sqlalchemy import text
from app import db


class AdminDashboardService:

    @staticmethod
    def getStats():
        # Initialize default mock data in case DB queries fail or tables are empty
        mock_data = {
            "stats": {
                "totalUsers": 1248,
                "usersTrend": "+12 người dùng mới hôm nay",
                "premiumUsers": 326,
                "premiumTrend": "Chiếm 26.1% tổng user",
                "totalTransactions": 8932,
                "transactionsTrend": "+18.4% so với tháng trước",
                "revenue": 4580000,
                "revenueTrend": "32 giao dịch thanh toán mới",
            },
            "aiModelStats": {
                "activeModel": "Logistic Regression",
                "accuracy": 87.5,
                "totalTrained": 2450,
                "lastTrained": "04/06/2026",
                "totalClassifiedToday": 586,
                "averageConfidence": 82.0,
            },
            "systemAlerts": [
                {
                    "id": 1,
                    "title": "12 giao dịch có AI confidence thấp",
                    "level": "warning",
                },
                {
                    "id": 2,
                    "title": "3 user Premium sắp hết hạn",
                    "level": "info",
                },
                {
                    "id": 3,
                    "title": "1 lỗi chatbot trong hôm nay",
                    "level": "danger",
                },
                {
                    "id": 4,
                    "title": "5 giao dịch chưa được phân loại chính xác",
                    "level": "warning",
                },
            ],
            "charts": {
                "userGrowth": {
                    "labels": ["Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6"],
                    "users": [450, 620, 780, 920, 1100, 1248],
                    "premiumUsers": [100, 150, 200, 240, 290, 326],
                },
                "userPremiumRatio": {
                    "labels": ["USER", "PREMIUM"],
                    "values": [74, 26],
                },
            },
            "usersList": [
                {
                    "id": 1,
                    "email": "admin@app.com",
                    "vaiTro": "ADMIN",
                    "trangThai": "ACTIVE",
                    "ngayTao": "2026-01-01",
                },
                {
                    "id": 2,
                    "email": "nguyenan@gmail.com",
                    "vaiTro": "USER",
                    "trangThai": "ACTIVE",
                    "ngayTao": "2026-05-15",
                },
                {
                    "id": 3,
                    "email": "leminh@yahoo.com",
                    "vaiTro": "PREMIUM",
                    "trangThai": "ACTIVE",
                    "ngayTao": "2026-05-18",
                },
            ],
            "transactionsList": [
                {
                    "id": 101,
                    "email": "nguyenan@gmail.com",
                    "danhMuc": "Ăn uống",
                    "loai": "CHI",
                    "soTien": 45000,
                    "ngayGiaoDich": "2026-06-01",
                    "phuongThuc": "MACHINE_LEARNING",
                    "doTinCay": 95.2,
                },
                {
                    "id": 102,
                    "email": "leminh@yahoo.com",
                    "danhMuc": "Lương",
                    "loai": "THU",
                    "soTien": 15000000,
                    "ngayGiaoDich": "2026-06-01",
                    "phuongThuc": "THU_CONG",
                    "doTinCay": 100.0,
                },
            ],
            "newUsersList": [
                {
                    "ten": "Nguyễn Văn A",
                    "email": "user01@gmail.com",
                    "vaiTro": "USER",
                    "time": "5 phút trước",
                },
                {
                    "ten": "Trần Minh B",
                    "email": "premium01@gmail.com",
                    "vaiTro": "PREMIUM",
                    "time": "20 phút trước",
                },
                {
                    "ten": "Lê Hoàng C",
                    "email": "user02@gmail.com",
                    "vaiTro": "USER",
                    "time": "1 giờ trước",
                },
            ],
            "recentTransactions": [
                {
                    "ten": "Nguyễn Văn A",
                    "loai": "CHI",
                    "danhMuc": "Ăn uống",
                    "soTien": 120000,
                    "ngay": "Hôm nay",
                    "trangThai": "Thành công",
                },
                {
                    "ten": "Trần Minh B",
                    "loai": "THU",
                    "danhMuc": "Lương",
                    "soTien": 8000000,
                    "ngay": "Hôm nay",
                    "trangThai": "Thành công",
                },
                {
                    "ten": "Lê Hoàng C",
                    "loai": "CHI",
                    "danhMuc": "Di chuyển",
                    "soTien": 75000,
                    "ngay": "Hôm qua",
                    "trangThai": "Thành công",
                },
            ],
            "chatbotLogs": [
                {
                    "email": "user01@gmail.com",
                    "cauHoi": "Tháng này tôi chi nhiều nhất vào đâu?",
                    "time": "10 phút trước",
                    "trangThai": "Đã trả lời",
                },
                {
                    "email": "premium01@gmail.com",
                    "cauHoi": "Dự đoán chi tiêu tháng sau",
                    "time": "25 phút trước",
                    "trangThai": "Đã trả lời",
                },
                {
                    "email": "user02@gmail.com",
                    "cauHoi": "Làm sao tiết kiệm hơn?",
                    "time": "1 giờ trước",
                    "trangThai": "Đã trả lời",
                },
            ],
        }

        try:
            # Attempt to query database
            # 1. Total users
            totalUsersResult = db.session.execute(
                text("SELECT COUNT(*) FROM tai_khoan")
            ).scalar()
            if totalUsersResult is not None:
                mock_data["stats"]["totalUsers"] = totalUsersResult

            # 2. Total premium
            premiumUsersResult = db.session.execute(
                text(
                    "SELECT COUNT(DISTINCT tai_khoan_id) FROM goi_premium WHERE trang_thai = 'ACTIVE'"
                )
            ).scalar()
            if premiumUsersResult is not None:
                mock_data["stats"]["premiumUsers"] = premiumUsersResult

            # 3. Total transactions
            totalTransactionsResult = db.session.execute(
                text("SELECT COUNT(*) FROM giao_dich")
            ).scalar()
            if totalTransactionsResult is not None:
                mock_data["stats"]["totalTransactions"] = totalTransactionsResult

            # 4. Total revenue
            revenueResult = db.session.execute(
                text(
                    "SELECT SUM(so_tien) FROM thanh_toan WHERE trang_thai_thanh_toan = 'SUCCESS'"
                )
            ).scalar()
            if revenueResult is not None:
                mock_data["stats"]["revenue"] = float(revenueResult)

            # 5. Fetch actual users list
            usersResult = db.session.execute(
                text(
                    "SELECT id, email, vai_tro, trang_thai, ngay_tao FROM tai_khoan ORDER BY ngay_tao DESC LIMIT 10"
                )
            ).fetchall()
            if usersResult:
                actualUsersList = []
                for row in usersResult:
                    actualUsersList.append(
                        {
                            "id": row[0],
                            "email": row[1],
                            "vaiTro": row[2],
                            "trangThai": row[3],
                            "ngayTao": (
                                row[4].strftime("%Y-%m-%d")
                                if row[4]
                                else "N/A"
                            ),
                        }
                    )
                mock_data["usersList"] = actualUsersList

            # 6. Fetch actual transactions list
            transactionsResult = db.session.execute(
                text(
                    """
                    SELECT gd.id, tk.email, dm.ten_danh_muc, gd.loai, gd.so_tien, gd.ngay_giao_dich, gd.phuong_thuc_phan_loai, gd.do_tin_cay 
                    FROM giao_dich gd
                    LEFT JOIN tai_khoan tk ON gd.tai_khoan_id = tk.id
                    LEFT JOIN danh_muc dm ON gd.danh_muc_id = dm.id
                    ORDER BY gd.ngay_giao_dich DESC, gd.id DESC LIMIT 10
                """
                )
            ).fetchall()
            if transactionsResult:
                actualTransactionsList = []
                for row in transactionsResult:
                    actualTransactionsList.append(
                        {
                            "id": row[0],
                            "email": row[1] or "N/A",
                            "danhMuc": row[2] or "N/A",
                            "loai": row[3],
                            "soTien": float(row[4]),
                            "ngayGiaoDich": (
                                row[5].strftime("%Y-%m-%d")
                                if row[5]
                                else "N/A"
                            ),
                            "phuongThuc": row[6],
                            "doTinCay": (
                                float(row[7]) if row[7] is not None else 100.0
                            ),
                        }
                    )
                mock_data["transactionsList"] = actualTransactionsList

            # 7. Fetch user growth trend (signups per month)
            try:
                userGrowthResult = db.session.execute(
                    text("""
                        SELECT DATE_FORMAT(ngay_tao, '%m/%Y') as m, COUNT(*) 
                        FROM tai_khoan 
                        GROUP BY m 
                        ORDER BY MIN(ngay_tao) ASC 
                        LIMIT 6
                    """)
                ).fetchall()
                if userGrowthResult:
                    mock_data["charts"]["userGrowth"] = {
                        "labels": [row[0] for row in userGrowthResult],
                        "users": [row[1] for row in userGrowthResult]
                    }
            except Exception as e_growth:
                print(f"[Warning] Failed to query user growth trend: {str(e_growth)}")

            # 8. Fetch actual user premium ratio
            try:
                totalCount = db.session.execute(
                    text("SELECT COUNT(*) FROM tai_khoan")
                ).scalar() or 0
                premiumCount = db.session.execute(
                    text("SELECT COUNT(DISTINCT tai_khoan_id) FROM goi_premium WHERE trang_thai = 'ACTIVE'")
                ).scalar() or 0
                normalCount = max(0, totalCount - premiumCount)
                
                mock_data["charts"]["userPremiumRatio"] = {
                    "labels": ["Normal User", "Premium User"],
                    "values": [normalCount, premiumCount]
                }
            except Exception as e_ratio:
                print(f"[Warning] Failed to query premium user ratio: {str(e_ratio)}")

        except Exception as db_err:
            # If database does not exist or fails, fall back to mock_data gracefully
            print(f"[Warning] Admin Dashboard DB Query failed: {str(db_err)}")

        return mock_data
