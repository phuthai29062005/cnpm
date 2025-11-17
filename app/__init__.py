from flask import Flask
from .models import (
    db, TaiKhoan, NhanKhau, HoKhau, NhanKhauHoKhau, TamTru, TamVang, 
    LoaiPhi, GiaoDich, ThuChi, LichSuHoKhau, ChiSoDienNuoc, BienLai, ThongBao, YeuCau
)
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from werkzeug.security import generate_password_hash
import click 
from sqlalchemy import text 
from datetime import datetime, date 

login_manager = LoginManager()

# --- HÀM NỘI BỘ ---

def _create_admin():
    """Hàm nội bộ: Tạo tài khoản admin."""
    print("--- Tạo tài khoản Admin ---")
    if not TaiKhoan.query.filter_by(role='admin').first():
        new_admin = TaiKhoan(username='admin', password_hash=generate_password_hash('123456'), ho_ten='Administrator', role='admin')
        db.session.add(new_admin)
        db.session.commit()
        print("Đã tạo admin/123456")
    else:
        print("Admin đã tồn tại.")

def _seed_fees():
    """Hàm nội bộ: Gieo mầm phí."""
    print("--- Gieo mầm phí ---")
    fees = [
        ("Phí vệ sinh môi trường", True, 60000, "VND/Hộ"),
        ("Phí điện", True, 3000, "VND/kWh"),
        ("Phí nước sinh hoạt", True, 10000, "VND/m3"),
        ("Phí quản lý chung cư", True, 5000, "VND/m2")
    ]
    count = 0
    for name, bb, gia, dv in fees:
        fee = LoaiPhi.query.filter_by(ten_phi=name).first()
        if not fee:
            db.session.add(LoaiPhi(ten_phi=name, bat_buoc=bb, don_gia=gia, don_vi=dv))
            count += 1
        else:
            fee.don_gia = gia
            fee.don_vi = dv
    
    # [FIX] Di dời lệnh commit ra khỏi 'if count > 0'
    # để đảm bảo các bản cập nhật giá (else) cũng được lưu.
    db.session.commit()
    
    print(f"Đã cập nhật {len(fees)} loại phí.")


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    Migrate(app, db, render_as_batch=True)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return TaiKhoan.query.get(int(user_id))

    from .admin_views import MyAdminIndexView
    admin = Admin(app, name='Quản lý Dân cư', index_view=MyAdminIndexView(name='Home', url='/admin'))
    
    from .auth import auth
    app.register_blueprint(auth)

    from .main import main
    app.register_blueprint(main)

    from .crud_routes import crud
    app.register_blueprint(crud)

    # --- CLI COMMAND ---

    @app.cli.command("seed-data")
    def seed_data():
        """[CLEANUP] Xóa sạch và Tạo mới 3 hộ gia đình (Dữ liệu thực tế)."""
        print("--- BƯỚC 1: ĐANG DỌN SẠCH DATABASE ---")
        
        # 1. Xóa ThuChi
        db.session.query(ThuChi).delete()
        
        # 2. Xóa GiaoDich
        GiaoDich.query.update({
            GiaoDich.bien_lai_id: None,
            GiaoDich.thong_bao_id: None
        })
        db.session.commit()
        db.session.query(GiaoDich).delete()

        # 3. Xóa các bảng con/phụ thuộc khác
        db.session.query(BienLai).delete()
        db.session.query(ThongBao).delete()
        db.session.query(LichSuHoKhau).delete()
        db.session.query(ChiSoDienNuoc).delete()
        db.session.query(NhanKhauHoKhau).delete()
        db.session.query(TamTru).delete()
        db.session.query(TamVang).delete()
        db.session.query(YeuCau).delete()
        
        # 4. Xóa TaiKhoan
        TaiKhoan.query.update({TaiKhoan.nhan_khau_id: None})
        db.session.commit()
        db.session.query(TaiKhoan).delete()

        # 5. Xóa HoKhau và NhanKhau
        NhanKhau.query.update({NhanKhau.id_ho_khau: None})
        HoKhau.query.update({HoKhau.chu_ho_id: None})
        db.session.commit()
        
        db.session.query(HoKhau).delete()
        db.session.query(NhanKhau).delete()
        
        db.session.commit()
        print("--- ĐÃ DỌN SẠCH ---")

        print("--- BƯỚC 2: Đang tạo dữ liệu mẫu thực tế ---")
        _seed_fees()
        _create_admin()

        # === HỘ 1: Gia đình Nguyễn Văn Hùng ===
        nk1_hung = NhanKhau(ho_ten="Nguyễn Văn Hùng", ngay_sinh=date(1980, 5, 15), gioi_tinh="Nam", so_cccd="001080001234", nghe_nghiep="Kỹ sư")
        nk1_lan = NhanKhau(ho_ten="Trần Thị Lan", ngay_sinh=date(1982, 8, 30), gioi_tinh="Nữ", so_cccd="001182004567", nghe_nghiep="Kế toán")
        nk1_anh = NhanKhau(ho_ten="Nguyễn Tuấn Anh", ngay_sinh=date(2010, 1, 10), gioi_tinh="Nam", nghe_nghiep="Học sinh")
        db.session.add_all([nk1_hung, nk1_lan, nk1_anh])
        db.session.commit()

        hk1 = HoKhau(ma_so_ho_khau="HM-DK-001", chu_ho_id=nk1_hung.id, 
                     so_nha="Số 10, ngõ 5", duong_pho="Phố Đại Từ", 
                     phuong_xa="Đại Kim", quan_huyen="Hoàng Mai", 
                     so_dien=100, so_nuoc=50)
        db.session.add(hk1)
        db.session.commit()

        # Link HK1
        nk1_hung.id_ho_khau = hk1.id
        db.session.add(NhanKhauHoKhau(nhan_khau_id=nk1_hung.id, ho_khau_id=hk1.id, quan_he_chu_ho="Chủ hộ"))
        db.session.add(TaiKhoan(username="001080001234", password_hash=generate_password_hash("1"), ho_ten=nk1_hung.ho_ten, role="resident", nhan_khau_id=nk1_hung.id))
        
        nk1_lan.id_ho_khau = hk1.id
        db.session.add(NhanKhauHoKhau(nhan_khau_id=nk1_lan.id, ho_khau_id=hk1.id, quan_he_chu_ho="Vợ"))
        db.session.add(TaiKhoan(username="001182004567", password_hash=generate_password_hash("1"), ho_ten=nk1_lan.ho_ten, role="resident", nhan_khau_id=nk1_lan.id))

        nk1_anh.id_ho_khau = hk1.id
        db.session.add(NhanKhauHoKhau(nhan_khau_id=nk1_anh.id, ho_khau_id=hk1.id, quan_he_chu_ho="Con trai"))

        # === HỘ 2: Gia đình Lê Minh Bình ===
        nk2_binh = NhanKhau(ho_ten="Lê Minh Bình", ngay_sinh=date(1975, 2, 20), gioi_tinh="Nam", so_cccd="001075007890", nghe_nghiep="Tài xế")
        nk2_mai = NhanKhau(ho_ten="Phạm Thị Mai", ngay_sinh=date(1977, 11, 12), gioi_tinh="Nữ", so_cccd="001177001122", nghe_nghiep="Nội trợ")
        db.session.add_all([nk2_binh, nk2_mai])
        db.session.commit()

        hk2 = HoKhau(ma_so_ho_khau="HM-DK-002", chu_ho_id=nk2_binh.id, 
                     so_nha="Số 15, ngõ 5", duong_pho="Phố Đại Từ", 
                     phuong_xa="Đại Kim", quan_huyen="Hoàng Mai", 
                     so_dien=200, so_nuoc=80)
        db.session.add(hk2)
        db.session.commit()

        # Link HK2
        nk2_binh.id_ho_khau = hk2.id
        db.session.add(NhanKhauHoKhau(nhan_khau_id=nk2_binh.id, ho_khau_id=hk2.id, quan_he_chu_ho="Chủ hộ"))
        db.session.add(TaiKhoan(username="001075007890", password_hash=generate_password_hash("1"), ho_ten=nk2_binh.ho_ten, role="resident", nhan_khau_id=nk2_binh.id))
        
        nk2_mai.id_ho_khau = hk2.id
        db.session.add(NhanKhauHoKhau(nhan_khau_id=nk2_mai.id, ho_khau_id=hk2.id, quan_he_chu_ho="Vợ"))
        db.session.add(TaiKhoan(username="001177001122", password_hash=generate_password_hash("1"), ho_ten=nk2_mai.ho_ten, role="resident", nhan_khau_id=nk2_mai.id))

        # === HỘ 3: Độc thân Hoàng Trung Dũng ===
        nk3_dung = NhanKhau(ho_ten="Hoàng Trung Dũng", ngay_sinh=date(1995, 9, 9), gioi_tinh="Nam", so_cccd="001095003344", nghe_nghiep="Lập trình viên")
        db.session.add(nk3_dung)
        db.session.commit()

        hk3 = HoKhau(ma_so_ho_khau="HM-DK-003", chu_ho_id=nk3_dung.id, 
                     so_nha="Số 20, ngách 15/7", duong_pho="Phố Đại Từ", 
                     phuong_xa="Đại Kim", quan_huyen="Hoàng Mai", 
                     so_dien=50, so_nuoc=10)
        db.session.add(hk3)
        db.session.commit()

        # Link HK3
        nk3_dung.id_ho_khau = hk3.id
        db.session.add(NhanKhauHoKhau(nhan_khau_id=nk3_dung.id, ho_khau_id=hk3.id, quan_he_chu_ho="Chủ hộ"))
        db.session.add(TaiKhoan(username="001095003344", password_hash=generate_password_hash("1"), ho_ten=nk3_dung.ho_ten, role="resident", nhan_khau_id=nk3_dung.id))

        db.session.commit()
        print("--- THÀNH CÔNG: Đã tạo 3 hộ khẩu chuẩn tại Đại Từ, Hoàng Mai ---")


    return app