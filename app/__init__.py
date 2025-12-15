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
from datetime import datetime, date, timedelta
import random

login_manager = LoginManager()

def _create_admin():
    if not TaiKhoan.query.filter_by(role='admin').first():
        new_admin = TaiKhoan(username='admin', password_hash=generate_password_hash('123456'), ho_ten='Administrator', role='admin')
        db.session.add(new_admin)
        db.session.commit()
        print("Đã tạo admin/123456")

def _seed_fees():
    fees = [
        ("Phí vệ sinh môi trường", True, 60000, "VND/Hộ"),
        ("Phí điện", True, 3000, "VND/kWh"),
        ("Phí nước sinh hoạt", True, 10000, "VND/m3"),
        ("Phí quản lý chung cư", True, 5000, "VND/m2")
    ]
    for name, bb, gia, dv in fees:
        fee = LoaiPhi.query.filter_by(ten_phi=name).first()
        if not fee:
            db.session.add(LoaiPhi(ten_phi=name, bat_buoc=bb, don_gia=gia, don_vi=dv))
        else:
            fee.don_gia = gia
            fee.don_vi = dv
    db.session.commit()

def _random_dob(start_year, end_year):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

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

    @app.cli.command("seed-data")
    def seed_data():
        """[CLEANUP] Xóa sạch và Tạo mới 100 hộ + 10 tạm trú."""
        print("--- BƯỚC 1: DỌN SẠCH DATABASE ---")
        db.session.query(ThuChi).delete()
        GiaoDich.query.update({GiaoDich.bien_lai_id: None, GiaoDich.thong_bao_id: None})
        db.session.commit(); db.session.query(GiaoDich).delete()
        db.session.query(BienLai).delete(); db.session.query(ThongBao).delete()
        db.session.query(LichSuHoKhau).delete(); db.session.query(ChiSoDienNuoc).delete()
        db.session.query(NhanKhauHoKhau).delete(); db.session.query(TamTru).delete()
        db.session.query(TamVang).delete(); db.session.query(YeuCau).delete()
        TaiKhoan.query.update({TaiKhoan.nhan_khau_id: None}); db.session.commit(); db.session.query(TaiKhoan).delete()
        NhanKhau.query.update({NhanKhau.id_ho_khau: None}); HoKhau.query.update({HoKhau.chu_ho_id: None}); db.session.commit()
        db.session.query(HoKhau).delete(); db.session.query(NhanKhau).delete(); db.session.commit()

        print("--- BƯỚC 2: TẠO DỮ LIỆU ---")
        _seed_fees(); _create_admin()

        jobs = ["Kỹ sư", "Bác sĩ", "Giáo viên", "Công nhân", "Kinh doanh", "Nội trợ", "Học sinh", "Sinh viên", "Lập trình viên", "Kế toán", "Luật sư", "Tài xế", "Bảo vệ", "Hưu trí", "Buôn bán tự do"]
        last_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
        middle_names = ["Văn", "Thị", "Hữu", "Minh", "Ngọc", "Thanh", "Đức", "Quang", "Mạnh", "Thu", "Hồng"]
        first_names = ["Hùng", "Lan", "Anh", "Bình", "Mai", "Dũng", "Hoa", "Tuấn", "Hương", "Long", "Thảo", "Huy", "Trang", "Nam", "Linh"]

        def random_name(gender):
            ln = random.choice(last_names)
            mn = "Thị" if gender == "Nữ" else random.choice([m for m in middle_names if m != "Thị"])
            fn = random.choice(first_names)
            return f"{ln} {mn} {fn}"

        # Tạo 100 Hộ
        for i in range(1, 101):
            num_members = random.randint(1, 7)
            head_dob = _random_dob(1970, 1995)
            head_gender = random.choice(["Nam", "Nữ"])
            head_name = random_name(head_gender)
            head_cccd = f"001{head_dob.year}{i:05d}"

            chu_ho = NhanKhau(
                ho_ten=head_name, ngay_sinh=head_dob, gioi_tinh=head_gender, so_cccd=head_cccd, 
                nghe_nghiep=random.choice(jobs), nguyen_quan="Hà Nội", dan_toc="Kinh",
                noi_thuong_tru=f"Số {i}, Phố Đại Từ, Đại Kim, Hoàng Mai"
            )
            db.session.add(chu_ho); db.session.commit()

            hk = HoKhau(
                ma_so_ho_khau=f"HK-DK-{i:03d}", chu_ho_id=chu_ho.id, 
                so_nha=f"Số {i}", duong_pho="Phố Đại Từ", phuong_xa="Phường Đại Kim", quan_huyen="Quận Hoàng Mai", 
                so_dien=random.randint(100, 600), so_nuoc=random.randint(10, 50)
            )
            db.session.add(hk); db.session.commit()

            chu_ho.id_ho_khau = hk.id
            db.session.add(NhanKhauHoKhau(nhan_khau_id=chu_ho.id, ho_khau_id=hk.id, quan_he_chu_ho="Chủ hộ"))
            db.session.add(TaiKhoan(username=chu_ho.so_cccd, password_hash=generate_password_hash("1"), ho_ten=chu_ho.ho_ten, role="resident", nhan_khau_id=chu_ho.id))

            members_created = 1
            has_spouse = False
            while members_created < num_members:
                rel, mem_gender, mem_dob = "", "", date.today()
                if not has_spouse:
                    rel = "Vợ" if head_gender == "Nam" else "Chồng"
                    mem_gender = "Nữ" if head_gender == "Nam" else "Nam"
                    mem_dob = _random_dob(head_dob.year - 5, head_dob.year + 5)
                    has_spouse = True
                elif members_created < 5:
                    rel = "Con"
                    mem_gender = random.choice(["Nam", "Nữ"])
                    mem_dob = _random_dob(head_dob.year + 20, 2023)
                else:
                    rel = random.choice(["Bố", "Mẹ"])
                    mem_gender = "Nam" if rel == "Bố" else "Nữ"
                    mem_dob = _random_dob(head_dob.year - 30, head_dob.year - 20)

                mem_job = "Học sinh" if (2025 - mem_dob.year) < 18 else random.choice(jobs)
                mem_cccd = None
                if (2025 - mem_dob.year) >= 14:
                    mem_cccd = f"0{random.randint(10,99)}{mem_dob.year}{random.randint(10000,99999)}"

                mem = NhanKhau(
                    ho_ten=random_name(mem_gender), ngay_sinh=mem_dob, gioi_tinh=mem_gender, so_cccd=mem_cccd,
                    id_ho_khau=hk.id, nghe_nghiep=mem_job, nguyen_quan=chu_ho.nguyen_quan, dan_toc="Kinh",
                    noi_thuong_tru=chu_ho.noi_thuong_tru
                )
                db.session.add(mem); db.session.commit()
                db.session.add(NhanKhauHoKhau(nhan_khau_id=mem.id, ho_khau_id=hk.id, quan_he_chu_ho=rel))
                if mem.so_cccd:
                    db.session.add(TaiKhoan(username=mem.so_cccd, password_hash=generate_password_hash("1"), ho_ten=mem.ho_ten, role="resident", nhan_khau_id=mem.id))
                members_created += 1

        # Tạo 10 người tạm trú
        print("--- Tạo 10 người tạm trú ---")
        for k in range(1, 11):
            tmp_dob = _random_dob(1995, 2003)
            tmp_name = random_name("Nam" if k % 2 == 0 else "Nữ")
            tmp_cccd = f"099{tmp_dob.year}{random.randint(10000, 99999)}"
            
            tmp_nk = NhanKhau(
                ho_ten=tmp_name, ngay_sinh=tmp_dob, gioi_tinh=("Nam" if k % 2 == 0 else "Nữ"), so_cccd=tmp_cccd,
                nghe_nghiep="Lao động tự do", tinh_trang="Tạm trú", nguyen_quan="Nghệ An", noi_thuong_tru="Quê quán: Nghệ An"
            )
            db.session.add(tmp_nk); db.session.commit()

            tt = TamTru(
                resident_id=tmp_nk.id, noi_tam_tru=f"Số {random.randint(1,100)}, Phố Đại Từ, Đại Kim",
                ngay_bat_dau=date(2024, 1, 1), ngay_ket_thuc=date(2025, 12, 31), ly_do="Đi làm", status="Approved"
            )
            db.session.add(tt)
            db.session.add(TaiKhoan(username=tmp_cccd, password_hash=generate_password_hash("1"), ho_ten=tmp_name, role="resident", nhan_khau_id=tmp_nk.id))

        db.session.commit()
        print("--- THÀNH CÔNG: 100 hộ dân và 10 tạm trú đã được tạo ---")

    return app