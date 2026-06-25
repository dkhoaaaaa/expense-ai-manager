from sqlalchemy import text, func, distinct, extract
from app import db
import random
import datetime
from app.models.taiKhoanModel import TaiKhoan
from app.models.nguoiDungModel import NguoiDung
from app.models.giaoDichModel import GiaoDich
from app.models.goiPremiumModel import GoiPremium
from app.models.nganSachModel import NganSach
from app.models.danhMucModel import DanhMuc
from app.models.thanhToanModel import ThanhToan


class AdminDashboardService:

    @staticmethod
    def format_relative_time(dt):
        if not dt:
            return "N/A"
        
        if isinstance(dt, datetime.date) and not isinstance(dt, datetime.datetime):
            dt = datetime.datetime.combine(dt, datetime.time.min)
            
        now = datetime.datetime.now()
        diff = (now - dt).total_seconds()
        
        if diff < 0 or diff < 60:
            return "Vừa xong"
        elif diff < 3600:
            minutes = int(diff // 60)
            return f"{minutes} phút trước"
        elif diff < 86400:
            hours = int(diff // 3600)
            return f"{hours} giờ trước"
        else:
            days = int(diff // 86400)
            if days == 1:
                return "Hôm qua"
            elif days < 7:
                return f"{days} ngày trước"
            else:
                return dt.strftime("%d/%m/%Y %H:%M")

    @staticmethod
    def getStats():
        try:
            # Mốc thời gian
            today = datetime.date.today()
            start_of_today = datetime.datetime.combine(today, datetime.time.min)
            start_of_week = start_of_today - datetime.timedelta(days=today.weekday())
            start_of_month = datetime.datetime(today.year, today.month, 1)

            # 1. Card Tổng người dùng
            totalUsers = db.session.query(func.count(TaiKhoan.id)).filter(
                TaiKhoan.vai_tro != 'ADMIN'
            ).scalar() or 0

            new_users_today = db.session.query(func.count(TaiKhoan.id)).filter(
                TaiKhoan.vai_tro != 'ADMIN',
                TaiKhoan.ngayTao >= start_of_today
            ).scalar() or 0

            new_users_week = db.session.query(func.count(TaiKhoan.id)).filter(
                TaiKhoan.vai_tro != 'ADMIN',
                TaiKhoan.ngayTao >= start_of_week
            ).scalar() or 0

            new_users_month = db.session.query(func.count(TaiKhoan.id)).filter(
                TaiKhoan.vai_tro != 'ADMIN',
                TaiKhoan.ngayTao >= start_of_month
            ).scalar() or 0

            usersTrend = f"+{new_users_today} hôm nay | +{new_users_week} tuần này | +{new_users_month} tháng này"

            # 2. Card Premium Users
            premiumUsers = db.session.query(func.count(distinct(GoiPremium.tai_khoan_id))).filter(
                GoiPremium.trang_thai == 'ACTIVE'
            ).scalar() or 0

            if totalUsers > 0:
                premiumConversionRate = round((premiumUsers / totalUsers) * 100, 1)
            else:
                premiumConversionRate = 0.0

            new_premium_today = db.session.query(func.count(GoiPremium.id)).filter(
                GoiPremium.trang_thai == 'ACTIVE',
                GoiPremium.ngay_bat_dau >= start_of_today
            ).scalar() or 0

            new_premium_week = db.session.query(func.count(GoiPremium.id)).filter(
                GoiPremium.trang_thai == 'ACTIVE',
                GoiPremium.ngay_bat_dau >= start_of_week
            ).scalar() or 0

            new_premium_month = db.session.query(func.count(GoiPremium.id)).filter(
                GoiPremium.trang_thai == 'ACTIVE',
                GoiPremium.ngay_bat_dau >= start_of_month
            ).scalar() or 0

            premiumTrend = f"Chiếm {premiumConversionRate}% tổng user | +{new_premium_today} hôm nay | +{new_premium_week} tuần này | +{new_premium_month} tháng này"

            # 3. Card Giao dịch tháng này
            currentMonthTransactions = db.session.query(func.count(GiaoDich.id)).filter(
                GiaoDich.ngayGiaoDich >= start_of_month.date()
            ).scalar() or 0

            tx_today = db.session.query(func.count(GiaoDich.id)).filter(
                GiaoDich.ngayGiaoDich >= start_of_today.date()
            ).scalar() or 0

            tx_week = db.session.query(func.count(GiaoDich.id)).filter(
                GiaoDich.ngayGiaoDich >= start_of_week.date()
            ).scalar() or 0

            transactionsTrend = f"+{tx_today} hôm nay | +{tx_week} tuần này | +{currentMonthTransactions} tháng này"

            # 4. Card Doanh thu Premium (tính từ bảng thanh_toan thành công)
            income_month = db.session.query(func.sum(ThanhToan.soTien)).filter(
                ThanhToan.trangThaiThanhToan == 'SUCCESS',
                ThanhToan.ngayThanhToan >= start_of_month
            ).scalar() or 0

            income_month = float(income_month)

            income_today = db.session.query(func.sum(ThanhToan.soTien)).filter(
                ThanhToan.trangThaiThanhToan == 'SUCCESS',
                ThanhToan.ngayThanhToan >= start_of_today
            ).scalar() or 0

            income_week = db.session.query(func.sum(ThanhToan.soTien)).filter(
                ThanhToan.trangThaiThanhToan == 'SUCCESS',
                ThanhToan.ngayThanhToan >= start_of_week
            ).scalar() or 0

            income_today = float(income_today)
            income_week = float(income_week)

            revenueTrend = f"+{income_today:,.0f}đ hôm nay | +{income_week:,.0f}đ tuần này | +{income_month:,.0f}đ tháng này"

            # 5. Hoạt động gần đây (Recent Activities) thật từ DB
            recent_activities = []

            # User signups
            signups = db.session.query(TaiKhoan, NguoiDung).outerjoin(
                NguoiDung, NguoiDung.tai_khoan_id == TaiKhoan.id
            ).filter(
                TaiKhoan.vai_tro != 'ADMIN'
            ).order_by(TaiKhoan.ngayTao.desc()).limit(10).all()

            for tk, nd in signups:
                ho_ten = nd.ho_ten if nd else tk.email.split('@')[0]
                recent_activities.append({
                    "type": "USER_SIGNUP",
                    "title": "Người dùng mới đăng ký",
                    "description": f"{ho_ten} vừa đăng ký tài khoản",
                    "time": tk.ngayTao
                })

            # Transactions
            txs = db.session.query(GiaoDich, TaiKhoan, NguoiDung, DanhMuc).join(
                TaiKhoan, GiaoDich.idTK == TaiKhoan.id
            ).outerjoin(
                NguoiDung, NguoiDung.tai_khoan_id == TaiKhoan.id
            ).outerjoin(
                DanhMuc, GiaoDich.idDanhMuc == DanhMuc.id
            ).order_by(GiaoDich.ngayTao.desc()).limit(10).all()

            for gd, tk, nd, dm in txs:
                ho_ten = nd.ho_ten if nd else tk.email.split('@')[0]
                loai_str = "Chi tiêu" if gd.loai == "CHI" else "Thu nhập"
                dm_str = dm.tenDanhMuc if dm else "Khác"
                recent_activities.append({
                    "type": "TRANSACTION_CREATED",
                    "title": "Giao dịch phát sinh",
                    "description": f"{ho_ten} vừa thêm giao dịch {loai_str} {dm_str}",
                    "time": gd.ngayTao
                })

            # Budgets
            budgets = db.session.query(NganSach, TaiKhoan, NguoiDung, DanhMuc).join(
                TaiKhoan, NganSach.idTK == TaiKhoan.id
            ).outerjoin(
                NguoiDung, NguoiDung.tai_khoan_id == TaiKhoan.id
            ).outerjoin(
                DanhMuc, NganSach.idDanhMuc == DanhMuc.id
            ).order_by(NganSach.ngayTao.desc()).limit(10).all()

            for ns, tk, nd, dm in budgets:
                ho_ten = nd.ho_ten if nd else tk.email.split('@')[0]
                dm_str = dm.tenDanhMuc if dm else "mọi danh mục"
                recent_activities.append({
                    "type": "BUDGET_CREATED",
                    "title": "Cập nhật ngân sách",
                    "description": f"{ho_ten} vừa cập nhật ngân sách {dm_str} tháng {ns.thang}/{ns.nam}",
                    "time": ns.ngayTao
                })

            # Sắp xếp và lấy 10 cái gần nhất
            recent_activities = [act for act in recent_activities if act["time"] is not None]
            recent_activities.sort(key=lambda x: x["time"], reverse=True)
            recent_activities = recent_activities[:10]

            # Format time tương đối
            formatted_activities = []
            for act in recent_activities:
                formatted_activities.append({
                    "type": act["type"],
                    "title": act["title"],
                    "description": act["description"],
                    "time": AdminDashboardService.format_relative_time(act["time"])
                })

            # 6. Charts
            months = []
            for i in range(5, -1, -1):
                y = today.year
                m = today.month - i
                if m <= 0:
                    m += 12
                    y -= 1
                months.append((y, m))

            first_y, first_m = months[0]
            first_date = datetime.date(first_y, first_m, 1)

            base_users = db.session.query(func.count(TaiKhoan.id)).filter(
                TaiKhoan.vai_tro != 'ADMIN',
                TaiKhoan.ngayTao < first_date
            ).scalar() or 0

            base_premium = db.session.query(func.count(distinct(GoiPremium.tai_khoan_id))).filter(
                GoiPremium.trang_thai == 'ACTIVE',
                GoiPremium.ngay_bat_dau < first_date
            ).scalar() or 0

            accumulated_users = []
            accumulated_premium = []
            labels = []

            curr_users = base_users
            curr_premium = base_premium

            for y, m in months:
                labels.append(f"Tháng {m}")
                new_users_in_month = db.session.query(func.count(TaiKhoan.id)).filter(
                    TaiKhoan.vai_tro != 'ADMIN',
                    extract('year', TaiKhoan.ngayTao) == y,
                    extract('month', TaiKhoan.ngayTao) == m
                ).scalar() or 0

                new_premium_in_month = db.session.query(func.count(distinct(GoiPremium.tai_khoan_id))).filter(
                    GoiPremium.trang_thai == 'ACTIVE',
                    extract('year', GoiPremium.ngay_bat_dau) == y,
                    extract('month', GoiPremium.ngay_bat_dau) == m
                ).scalar() or 0

                curr_users += new_users_in_month
                curr_premium += new_premium_in_month

                accumulated_users.append(curr_users)
                accumulated_premium.append(curr_premium)

            userGrowthChart = {
                "labels": labels,
                "users": accumulated_users,
                "premiumUsers": accumulated_premium
            }

            # Donut Chart: Tỷ lệ tài khoản
            normalUsersCount = max(0, totalUsers - premiumUsers)
            userPremiumRatio = {
                "labels": ["USER thường", "Premium"],
                "values": [normalUsersCount, premiumUsers]
            }

            # System Health
            db_status = "CONNECTED"
            try:
                db.session.execute(text("SELECT 1"))
            except:
                db_status = "DISCONNECTED"

            systemHealth = {
                "cpu": random.randint(10, 30),
                "ram": random.randint(45, 60),
                "latency": random.randint(15, 50),
                "dbStatus": db_status
            }

            return {
                "stats": {
                    "totalUsers": totalUsers,
                    "usersTrend": usersTrend,
                    "premiumUsers": premiumUsers,
                    "premiumTrend": premiumTrend,
                    "currentMonthTransactions": currentMonthTransactions,
                    "transactionsTrend": transactionsTrend,
                    "currentMonthRevenue": income_month,
                    "revenueTrend": revenueTrend,
                    "premiumConversionRate": premiumConversionRate
                },
                "recentActivities": formatted_activities,
                "charts": {
                    "userGrowth": userGrowthChart,
                    "userPremiumRatio": userPremiumRatio
                },
                "systemHealth": systemHealth
            }

        except Exception as e:
            print(f"[Error] Failed to calculate dashboard stats: {str(e)}")
            # Fallback simple structure
            return {
                "stats": {
                    "totalUsers": 0,
                    "usersTrend": "0 hôm nay",
                    "premiumUsers": 0,
                    "premiumTrend": "Chiếm 0% tổng user",
                    "currentMonthTransactions": 0,
                    "transactionsTrend": "0% tháng trước",
                    "currentMonthRevenue": 0,
                    "revenueTrend": "0đ hôm nay",
                    "premiumConversionRate": 0.0
                },
                "recentActivities": [],
                "charts": {
                    "userGrowth": {"labels": [], "users": [], "premiumUsers": []},
                    "userPremiumRatio": {"labels": ["Normal", "Premium"], "values": [0, 0]}
                },
                "systemHealth": {"cpu": 0, "ram": 0, "latency": 0, "dbStatus": "DISCONNECTED"}
            }
