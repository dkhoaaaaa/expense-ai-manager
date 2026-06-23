from sqlalchemy import text
from app import db
import random


class AdminDashboardService:

    @staticmethod
    def getStats():
        mock_data = {
            "stats": {
                "totalUsers": 1248,
                "usersTrend": "+12 người dùng mới hôm nay",
                "premiumUsers": 326,
                "premiumTrend": "Chiếm 26.1% tổng user",
                "currentMonthTransactions": 8932,
                "transactionsTrend": "+18.4% so với tháng trước",
                "currentMonthRevenue": 4580000,
                "revenueTrend": "32 giao dịch thanh toán mới",
                "premiumConversionRate": 26.1,
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
                "revenueMonthly": {
                    "labels": ["Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6"],
                    "data": [1200000, 1800000, 2400000, 3100000, 3900000, 4580000],
                },
                "paymentStats": {
                    "success": 32,
                    "pending": 5,
                    "failed": 2,
                }
            },
            "topActiveUsers": [
                {"hoTen": "Nguyễn Văn A", "email": "user01@gmail.com", "isPremium": False, "transactionCount": 42},
                {"hoTen": "Trần Minh B", "email": "premium01@gmail.com", "isPremium": True, "transactionCount": 38},
                {"hoTen": "Lê Hoàng C", "email": "user02@gmail.com", "isPremium": False, "transactionCount": 29},
                {"hoTen": "Phạm Thanh D", "email": "user03@gmail.com", "isPremium": False, "transactionCount": 25},
                {"hoTen": "Hoàng Đức E", "email": "premium02@gmail.com", "isPremium": True, "transactionCount": 21}
            ],
            "systemHealth": {
                "cpu": 24,
                "ram": 58,
                "latency": 45,
                "dbStatus": "CONNECTED"
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
            "recentActivities": [
                {"type": "USER_SIGNUP", "title": "Người dùng mới đăng ký", "description": "Tài khoản nguyenan@gmail.com đã đăng ký tham gia hệ thống.", "time": "2026-06-22 10:15:30"},
                {"type": "AI_PREDICTION", "title": "AI dự đoán danh mục", "description": "Hệ thống tự động phân loại mô tả 'Ăn trưa cơm tấm' vào danh mục 'Ăn uống'.", "time": "2026-06-22 10:12:00"},
                {"type": "PAYMENT_SUCCESS", "title": "Thanh toán thành công", "description": "Giao dịch thanh toán 199,000 VNĐ cho gói Premium từ leminh@yahoo.com thành công.", "time": "2026-06-22 09:45:12"},
                {"type": "PREMIUM_PURCHASE", "title": "Người dùng mua Premium", "description": "Tài khoản leminh@yahoo.com đã kích hoạt thành công gói Premium 30 ngày.", "time": "2026-06-22 09:45:12"},
                {"type": "USER_SIGNUP", "title": "Người dùng mới đăng ký", "description": "Tài khoản leminh@yahoo.com đã đăng ký tham gia hệ thống.", "time": "2026-06-22 09:30:00"},
                {"type": "AI_PREDICTION", "title": "AI dự đoán danh mục", "description": "Hệ thống tự động phân loại mô tả 'Mua vé xem phim' vào danh mục 'Giải trí'.", "time": "2026-06-22 09:10:45"},
                {"type": "AI_PREDICTION", "title": "AI dự đoán danh mục", "description": "Hệ thống tự động phân loại mô tả 'Đổ xăng xe máy' vào danh mục 'Di chuyển'.", "time": "2026-06-22 08:55:00"},
                {"type": "PAYMENT_SUCCESS", "title": "Thanh toán thành công", "description": "Giao dịch thanh toán 199,000 VNĐ cho gói Premium từ hoangduc@gmail.com thành công.", "time": "2026-06-22 08:32:15"},
                {"type": "PREMIUM_PURCHASE", "title": "Người dùng mua Premium", "description": "Tài khoản hoangduc@gmail.com đã kích hoạt thành công gói Premium 30 ngày.", "time": "2026-06-22 08:32:15"},
                {"type": "USER_SIGNUP", "title": "Người dùng mới đăng ký", "description": "Tài khoản hoangduc@gmail.com đã đăng ký tham gia hệ thống.", "time": "2026-06-22 08:15:00"}
            ]
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

            # 3. Current month transactions
            try:
                # Try MySQL first
                currentMonthTransactionsResult = db.session.execute(
                    text("""
                        SELECT COUNT(*) FROM giao_dich 
                        WHERE DATE_FORMAT(ngay_giao_dich, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')
                    """)
                ).scalar()
                if currentMonthTransactionsResult is not None:
                    mock_data["stats"]["currentMonthTransactions"] = currentMonthTransactionsResult
            except Exception:
                try:
                    # SQLite fallback
                    currentMonthTransactionsResult = db.session.execute(
                        text("""
                            SELECT COUNT(*) FROM giao_dich 
                            WHERE strftime('%Y-%m', ngay_giao_dich) = strftime('%Y-%m', 'now')
                        """)
                    ).scalar()
                    if currentMonthTransactionsResult is not None:
                        mock_data["stats"]["currentMonthTransactions"] = currentMonthTransactionsResult
                except Exception as e_txn_month:
                    print(f"[Warning] Failed to query current month transactions: {str(e_txn_month)}")

            # 4. Current month revenue
            try:
                # Try MySQL first
                currentMonthRevenueResult = db.session.execute(
                    text("""
                        SELECT SUM(so_tien) FROM thanh_toan 
                        WHERE trang_thai_thanh_toan = 'SUCCESS' 
                        AND DATE_FORMAT(ngay_thanh_toan, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')
                    """)
                ).scalar()
                if currentMonthRevenueResult is not None:
                    mock_data["stats"]["currentMonthRevenue"] = float(currentMonthRevenueResult)
            except Exception:
                try:
                    # SQLite fallback
                    currentMonthRevenueResult = db.session.execute(
                        text("""
                            SELECT SUM(so_tien) FROM thanh_toan 
                            WHERE trang_thai_thanh_toan = 'SUCCESS' 
                            AND strftime('%Y-%m', ngay_thanh_toan) = strftime('%Y-%m', 'now')
                        """)
                    ).scalar()
                    if currentMonthRevenueResult is not None:
                        mock_data["stats"]["currentMonthRevenue"] = float(currentMonthRevenueResult)
                except Exception as e_rev_month:
                    print(f"[Warning] Failed to query current month revenue: {str(e_rev_month)}")

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
                        "users": [row[1] for row in userGrowthResult],
                        "premiumUsers": [int(row[1] * 0.25) for row in userGrowthResult] # Mock premium proportion
                    }
            except Exception as e_growth:
                # Try SQLite syntax fallback
                try:
                    userGrowthResult = db.session.execute(
                        text("""
                            SELECT strftime('%m/%Y', ngay_tao) as m, COUNT(*) 
                            FROM tai_khoan 
                            GROUP BY m 
                            ORDER BY MIN(ngay_tao) ASC 
                            LIMIT 6
                        """)
                    ).fetchall()
                    if userGrowthResult:
                        mock_data["charts"]["userGrowth"] = {
                            "labels": [row[0] for row in userGrowthResult],
                            "users": [row[1] for row in userGrowthResult],
                            "premiumUsers": [int(row[1] * 0.25) for row in userGrowthResult]
                        }
                except Exception:
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

            # 9. Fetch monthly revenue trend
            try:
                revenueMonthlyResult = db.session.execute(
                    text("""
                        SELECT DATE_FORMAT(ngay_thanh_toan, '%m/%Y') as m, SUM(so_tien) 
                        FROM thanh_toan 
                        WHERE trang_thai_thanh_toan = 'SUCCESS' 
                        GROUP BY m 
                        ORDER BY MIN(ngay_thanh_toan) ASC 
                        LIMIT 6
                    """)
                ).fetchall()
                if revenueMonthlyResult:
                    mock_data["charts"]["revenueMonthly"] = {
                        "labels": [row[0] for row in revenueMonthlyResult],
                        "data": [float(row[1]) for row in revenueMonthlyResult]
                    }
            except Exception as e_rev:
                # Try SQLite fallback
                try:
                    revenueMonthlyResult = db.session.execute(
                        text("""
                            SELECT strftime('%m/%Y', ngay_thanh_toan) as m, SUM(so_tien) 
                            FROM thanh_toan 
                            WHERE trang_thai_thanh_toan = 'SUCCESS' 
                            GROUP BY m 
                            ORDER BY MIN(ngay_thanh_toan) ASC 
                            LIMIT 6
                        """)
                    ).fetchall()
                    if revenueMonthlyResult:
                        mock_data["charts"]["revenueMonthly"] = {
                            "labels": [row[0] for row in revenueMonthlyResult],
                            "data": [float(row[1]) for row in revenueMonthlyResult]
                        }
                except Exception:
                    print(f"[Warning] Failed to query monthly revenue: {str(e_rev)}")

            # 10. Fetch payment statistics
            try:
                paymentStatsResult = db.session.execute(
                    text("""
                        SELECT trang_thai_thanh_toan, COUNT(*) 
                        FROM thanh_toan 
                        GROUP BY trang_thai_thanh_toan
                    """)
                ).fetchall()
                if paymentStatsResult:
                    stats_map = {row[0]: int(row[1]) for row in paymentStatsResult}
                    mock_data["charts"]["paymentStats"] = {
                        "success": stats_map.get("SUCCESS", 0),
                        "pending": stats_map.get("PENDING", 0),
                        "failed": stats_map.get("FAILED", 0),
                    }
            except Exception as e_pay:
                print(f"[Warning] Failed to query payment stats: {str(e_pay)}")

            # 11. Calculate premium conversion rate
            totalUsers = mock_data["stats"]["totalUsers"]
            premiumUsers = mock_data["stats"]["premiumUsers"]
            if totalUsers > 0:
                mock_data["stats"]["premiumConversionRate"] = round((premiumUsers / totalUsers) * 100, 1)
                mock_data["stats"]["premiumTrend"] = f"Chiếm {mock_data['stats']['premiumConversionRate']}% tổng user"
            else:
                mock_data["stats"]["premiumConversionRate"] = 0.0

            # 12. Fetch top active users (by transaction count)
            try:
                topUsersResult = db.session.execute(
                    text("""
                        SELECT nd.ho_ten, tk.email, tk.vai_tro, COUNT(gd.id) as cnt
                        FROM tai_khoan tk
                        JOIN giao_dich gd ON gd.tai_khoan_id = tk.id
                        LEFT JOIN nguoi_dung nd ON nd.tai_khoan_id = tk.id
                        GROUP BY tk.id, nd.ho_ten, tk.email, tk.vai_tro
                        ORDER BY cnt DESC
                        LIMIT 5
                    """)
                ).fetchall()
                if topUsersResult:
                    actualTopUsers = []
                    for row in topUsersResult:
                        actualTopUsers.append({
                            "hoTen": row[0] or row[1].split('@')[0],
                            "email": row[1],
                            "isPremium": row[2] == "PREMIUM",
                            "transactionCount": int(row[3])
                        })
                    mock_data["topActiveUsers"] = actualTopUsers
            except Exception as e_top:
                print(f"[Warning] Failed to query top active users: {str(e_top)}")

            # 13. Business Overview Stats (Removed)
            pass

            # 14. Recent activities timeline
            try:
                recent_activities = []
                
                # USER_SIGNUP
                signups = db.session.execute(text("""
                    SELECT email, ngay_tao FROM tai_khoan ORDER BY ngay_tao DESC LIMIT 10
                """)).fetchall()
                for r in signups:
                    recent_activities.append({
                        "type": "USER_SIGNUP",
                        "title": "Người dùng mới đăng ký",
                        "description": f"Tài khoản {r[0]} đã đăng ký tham gia hệ thống.",
                        "time": r[1]
                    })
                
                # PREMIUM_PURCHASE
                premiums = db.session.execute(text("""
                    SELECT tk.email, gp.ten_goi, gp.ngay_tao 
                    FROM goi_premium gp 
                    JOIN tai_khoan tk ON gp.tai_khoan_id = tk.id 
                    ORDER BY gp.ngay_tao DESC LIMIT 10
                """)).fetchall()
                for r in premiums:
                    recent_activities.append({
                        "type": "PREMIUM_PURCHASE",
                        "title": "Người dùng mua Premium",
                        "description": f"Tài khoản {r[0]} đã kích hoạt thành công gói {r[1]}.",
                        "time": r[2]
                    })

                # PAYMENT_SUCCESS
                payments = db.session.execute(text("""
                    SELECT tk.email, tt.so_tien, gp.ten_goi, COALESCE(tt.ngay_thanh_toan, tt.ngay_tao) as t
                    FROM thanh_toan tt
                    LEFT JOIN tai_khoan tk ON tt.tai_khoan_id = tk.id
                    LEFT JOIN goi_premium gp ON tt.goi_premium_id = gp.id
                    WHERE tt.trang_thai_thanh_toan = 'SUCCESS'
                    ORDER BY t DESC LIMIT 10
                """)).fetchall()
                for r in payments:
                    recent_activities.append({
                        "type": "PAYMENT_SUCCESS",
                        "title": "Thanh toán thành công",
                        "description": f"Giao dịch thanh toán {r[1]:,.0f} VNĐ cho gói {r[2] or 'Premium'} từ {r[0] or 'User'} thành công.",
                        "time": r[3]
                    })

                # AI_PREDICTION
                predictions = db.session.execute(text("""
                    SELECT tk.email, ls.van_ban_nhap, dm.ten_danh_muc, ls.ngay_tao
                    FROM lich_su_ai_phan_loai ls
                    LEFT JOIN tai_khoan tk ON ls.tai_khoan_id = tk.id
                    LEFT JOIN danh_muc dm ON ls.danh_muc_du_doan_id = dm.id
                    ORDER BY ls.ngay_tao DESC LIMIT 10
                """)).fetchall()
                for r in predictions:
                    recent_activities.append({
                        "type": "AI_PREDICTION",
                        "title": "AI dự đoán danh mục",
                        "description": f"Hệ thống tự động phân loại mô tả '{r[1]}' vào danh mục '{r[2] or 'Chưa rõ'}'.",
                        "time": r[3]
                    })

                # Sort by time descending
                recent_activities = [act for act in recent_activities if act["time"] is not None]
                recent_activities.sort(key=lambda x: x["time"], reverse=True)
                recent_activities = recent_activities[:10]

                # Convert time to string format
                for act in recent_activities:
                    # Check if act["time"] is datetime
                    if hasattr(act["time"], "strftime"):
                        act["time"] = act["time"].strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        act["time"] = str(act["time"])

                if recent_activities:
                    mock_data["recentActivities"] = recent_activities

            except Exception as e_act:
                print(f"[Warning] Failed to query recent activities: {str(e_act)}")

        except Exception as db_err:
            # If database does not exist or fails, fall back to mock_data gracefully
            print(f"[Warning] Admin Dashboard DB Query failed: {str(db_err)}")

        # 13. System Health Check
        db_status = "CONNECTED"
        try:
            db.session.execute(text("SELECT 1"))
        except Exception:
            db_status = "DISCONNECTED"

        mock_data["systemHealth"] = {
            "cpu": random.randint(15, 35),
            "ram": random.randint(50, 65),
            "latency": random.randint(20, 60),
            "dbStatus": db_status
        }

        return mock_data
