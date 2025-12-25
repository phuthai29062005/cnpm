from flask_admin import AdminIndexView, expose
from flask_login import current_user
from flask import flash, redirect, url_for, request
from sqlalchemy import func, or_
from .models import db, NhanKhau, HoKhau, TamTru, TamVang, GiaoDich, YeuCau, LichSuHoKhau
from datetime import date

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.dashboard'))
    
    @expose('/')
    def index(self):
        try:
            search_query = request.args.get('q', '')
            
            # Data Cards
            total_nhankhau = db.session.query(NhanKhau).count()
            total_hokhau = db.session.query(HoKhau).count()
            total_tamtru = db.session.query(TamTru).count()
            total_tamvang = db.session.query(TamVang).count()
            paid = db.session.query(func.sum(GiaoDich.so_tien)).filter_by(trang_thai='Đã thanh toán').scalar() or 0
            total_doanhthu = "{:,.0f}".format(paid)
            pending_bills = db.session.query(GiaoDich).filter_by(trang_thai='Đang chờ').count()

            # [MỚI] Thống kê Gender & Age
            all_nk_stats = db.session.query(NhanKhau.ngay_sinh, NhanKhau.gioi_tinh).all()
            stat_gender = {'Nam': 0, 'Nu': 0, 'Khac': 0}
            stat_age = {'TreEm': 0, 'LaoDong': 0, 'NghiHuu': 0} # <15, 15-60, >60
            
            today = date.today()
            for dob, gender in all_nk_stats:
                if gender == 'Nam': stat_gender['Nam'] += 1
                elif gender == 'Nữ': stat_gender['Nu'] += 1
                else: stat_gender['Khac'] += 1
                
                if dob:
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    if age < 15: stat_age['TreEm'] += 1
                    elif 15 <= age <= 60: stat_age['LaoDong'] += 1
                    else: stat_age['NghiHuu'] += 1

            # Query Search
            nhankhau_q = db.session.query(NhanKhau)
            if search_query:
                nhankhau_q = nhankhau_q.filter(or_(NhanKhau.ho_ten.ilike(f'%{search_query}%'), NhanKhau.so_cccd.ilike(f'%{search_query}%')))
            all_nhankhau = nhankhau_q.order_by(NhanKhau.id.desc()).all()

            hokhau_q = db.session.query(HoKhau)
            if search_query:
                hokhau_q = hokhau_q.filter(HoKhau.ma_so_ho_khau.ilike(f'%{search_query}%'))
            # [FIX] Xóa limit, lấy tất cả Hộ khẩu để tìm kiếm được hết
            all_hokhau = hokhau_q.order_by(HoKhau.id.desc()).all()

            # [FIX QUAN TRỌNG] Xóa .limit(20) ở dòng này để hiện đủ 300 giao dịch
            all_giaodich = db.session.query(GiaoDich).order_by(GiaoDich.id.desc()).all()
            
            # Tạm trú lấy hết (giữ nguyên hoặc xóa limit nếu có)
            all_tamtru = db.session.query(TamTru).order_by(TamTru.ngay_bat_dau.desc()).all()
            
            # Log và Yêu cầu có thể giữ limit 50 cho đỡ nặng, hoặc tăng lên 100 tùy bạn
            all_logs = db.session.query(LichSuHoKhau).order_by(LichSuHoKhau.ngay_thuc_hien.desc()).limit(100).all()
            all_requests = db.session.query(YeuCau).order_by(YeuCau.ngay_gui.desc()).all()

        except Exception as e:
            flash(f"Lỗi tải Dashboard: {e}", "danger")
            total_nhankhau = total_hokhau = total_tamtru = total_tamvang = pending_bills = 0
            total_doanhthu = "0"
            stat_gender = {'Nam': 0, 'Nu': 0, 'Khac': 0}
            stat_age = {'TreEm': 0, 'LaoDong': 0, 'NghiHuu': 0}
            all_nhankhau = all_hokhau = all_giaodich = all_tamtru = all_logs = all_requests = []
            search_query = ''
            
        return self.render('admin/custom_index.html',
                           total_nhankhau=total_nhankhau,
                           total_hokhau=total_hokhau,
                           total_tamtru=total_tamtru,
                           total_tamvang=total_tamvang,
                           total_doanhthu=total_doanhthu,
                           pending_bills=pending_bills,
                           stat_gender=stat_gender,
                           stat_age=stat_age,
                           all_nhankhau=all_nhankhau,
                           all_hokhau=all_hokhau,
                           all_tamtru=all_tamtru,
                           all_giaodich=all_giaodich,
                           all_logs=all_logs,
                           all_requests=all_requests,
                           search_query=search_query
                           )