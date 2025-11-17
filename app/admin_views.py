from flask_admin import AdminIndexView, expose
from flask_login import current_user
from flask import flash, redirect, url_for, request
from sqlalchemy import func, or_
from .models import db, NhanKhau, HoKhau, TamTru, TamVang, GiaoDich, YeuCau, LichSuHoKhau

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

            # Query Nhân khẩu (Có search)
            nhankhau_q = db.session.query(NhanKhau)
            if search_query:
                nhankhau_q = nhankhau_q.filter(
                    or_(
                        NhanKhau.ho_ten.ilike(f'%{search_query}%'),
                        NhanKhau.so_cccd.ilike(f'%{search_query}%')
                    )
                )
            all_nhankhau = nhankhau_q.order_by(NhanKhau.id.desc()).all()

            # Query Hộ khẩu (Có search)
            hokhau_q = db.session.query(HoKhau)
            if search_query:
                hokhau_q = hokhau_q.filter(HoKhau.ma_so_ho_khau.ilike(f'%{search_query}%'))
            all_hokhau = hokhau_q.order_by(HoKhau.id.desc()).all()

            all_giaodich = db.session.query(GiaoDich).order_by(GiaoDich.id.desc()).limit(20).all()
            all_tamtru = db.session.query(TamTru).order_by(TamTru.ngay_bat_dau.desc()).all()

            # Data 2 bảng lịch sử
            all_logs = db.session.query(LichSuHoKhau).order_by(LichSuHoKhau.ngay_thuc_hien.desc()).limit(50).all()
            all_requests = db.session.query(YeuCau).order_by(YeuCau.ngay_gui.desc()).limit(50).all()

        except Exception as e:
            flash(f"Lỗi tải Dashboard: {e}", "danger")
            total_nhankhau = total_hokhau = total_tamtru = total_tamvang = pending_bills = 0
            total_doanhthu = "0"
            all_nhankhau = all_hokhau = all_giaodich = all_tamtru = all_logs = all_requests = []
            search_query = ''
            
        return self.render('admin/custom_index.html',
                           total_nhankhau=total_nhankhau,
                           total_hokhau=total_hokhau,
                           total_tamtru=total_tamtru,
                           total_tamvang=total_tamvang,
                           total_doanhthu=total_doanhthu,
                           pending_bills=pending_bills,
                           all_nhankhau=all_nhankhau,
                           all_hokhau=all_hokhau,
                           all_tamtru=all_tamtru,
                           all_giaodich=all_giaodich,
                           all_logs=all_logs,
                           all_requests=all_requests,
                           search_query=search_query
                           )