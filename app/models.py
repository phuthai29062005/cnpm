from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import CheckConstraint

db = SQLAlchemy()

# --- 1. Hộ khẩu - Nhân khẩu ---

class NhanKhau(db.Model):
    __tablename__ = "Nhan_khau"
    id = db.Column(db.Integer, primary_key=True)
    ho_ten = db.Column(db.Unicode(100), nullable=False)
    bi_danh = db.Column(db.Unicode(50))
    ngay_sinh = db.Column(db.Date, nullable=False)
    gioi_tinh = db.Column(db.Unicode(10), nullable=False) 
    nguyen_quan = db.Column(db.Unicode(255))
    dan_toc = db.Column(db.Unicode(50))
    nghe_nghiep = db.Column(db.Unicode(100))
    noi_lam_viec = db.Column(db.Unicode(100))
    so_cccd = db.Column(db.String(12), unique=True, nullable=True) 
    ngay_cap = db.Column(db.Date)
    noi_cap = db.Column(db.Unicode(100))
    id_ho_khau = db.Column(db.Integer, db.ForeignKey("Ho_khau.id"))
    ngay_dang_ky_thuong_tru = db.Column(db.Date)
    noi_thuong_tru = db.Column(db.Unicode(255), default="Mới sinh")
    tinh_trang = db.Column(db.Unicode(20), default="Bình thường") 
    ngay_cap_nhat = db.Column(db.DateTime, default=datetime.utcnow)

    ho_khau = db.relationship("HoKhau", back_populates="thanh_vien", foreign_keys=[id_ho_khau])
    ho_khau_lam_chu = db.relationship("HoKhau", back_populates="chu_ho", foreign_keys="HoKhau.chu_ho_id")
    giao_dich = db.relationship("GiaoDich", back_populates="nguoi_nop")
    ho_khau_links = db.relationship("NhanKhauHoKhau", back_populates="nhan_khau", cascade="all, delete-orphan")
    tam_tru = db.relationship("TamTru", back_populates="resident", cascade="all, delete-orphan")
    tam_vang = db.relationship("TamVang", back_populates="resident", cascade="all, delete-orphan")

class HoKhau(db.Model):
    __tablename__ = "Ho_khau"
    id = db.Column(db.Integer, primary_key=True)
    ma_so_ho_khau = db.Column(db.String(50), unique=True, nullable=False) 
    chu_ho_id = db.Column(db.Integer, db.ForeignKey("Nhan_khau.id"))
    so_nha = db.Column(db.Unicode(50), nullable=False) 
    duong_pho = db.Column(db.Unicode(100), nullable=False)
    phuong_xa = db.Column(db.Unicode(100), nullable=False)
    quan_huyen = db.Column(db.Unicode(100), nullable=False)
    ngay_tao = db.Column(db.Date, default=datetime.utcnow)
    ghi_chu = db.Column(db.UnicodeText) 
    so_dien = db.Column(db.Integer, default=0)
    so_nuoc = db.Column(db.Integer, default=0)

    chu_ho = db.relationship("NhanKhau", back_populates="ho_khau_lam_chu", foreign_keys=[chu_ho_id])
    thanh_vien = db.relationship("NhanKhau", back_populates="ho_khau", lazy="dynamic", foreign_keys="NhanKhau.id_ho_khau")
    giao_dich = db.relationship("GiaoDich", back_populates="ho_khau", cascade="all, delete-orphan")
    member_links = db.relationship("NhanKhauHoKhau", back_populates="ho_khau", cascade="all, delete-orphan")
    lich_su = db.relationship("LichSuHoKhau", back_populates="ho_khau", cascade="all, delete-orphan")
    chiso_diennuoc = db.relationship("ChiSoDienNuoc", back_populates="ho_khau", cascade="all, delete-orphan")
    thuchi = db.relationship("ThuChi", back_populates="ho_khau")

class NhanKhauHoKhau(db.Model):
    __tablename__ = "nhan_khau_ho_khau"
    id = db.Column(db.Integer, primary_key=True)
    ho_khau_id = db.Column(db.Integer, db.ForeignKey("Ho_khau.id"), nullable=False)
    nhan_khau_id = db.Column(db.Integer, db.ForeignKey("Nhan_khau.id"), nullable=False)
    quan_he_chu_ho = db.Column(db.Unicode(50), nullable=False)
    ngay_bat_dau = db.Column(db.Date, default=datetime.utcnow)
    ngay_ket_thuc = db.Column(db.Date)
    trang_thai = db.Column(db.Unicode(100), default="Bình thường")
    ghi_chu = db.Column(db.UnicodeText) 

    ho_khau = db.relationship("HoKhau", back_populates="member_links")
    nhan_khau = db.relationship("NhanKhau", back_populates="ho_khau_links")

class LichSuHoKhau(db.Model):
    __tablename__ = "LichSuHoKhau"
    id = db.Column(db.Integer, primary_key=True)
    ho_khau_id = db.Column(db.Integer, db.ForeignKey("Ho_khau.id"), nullable=True)
    noi_dung = db.Column(db.UnicodeText, nullable=False) 
    ngay_thuc_hien = db.Column(db.DateTime, default=datetime.utcnow)
    nguoi_thuc_hien = db.Column(db.Unicode(50), default="Admin") 
    ho_khau = db.relationship("HoKhau", back_populates="lich_su")

# --- 2. Cư trú & Tài khoản ---

class TamTru(db.Model):
    __tablename__ = "tam_tru"
    id = db.Column(db.Integer, primary_key=True)
    resident_id = db.Column(db.Integer, db.ForeignKey("Nhan_khau.id"), nullable=False)
    noi_tam_tru = db.Column(db.Unicode(255), nullable=False)
    ngay_bat_dau = db.Column(db.Date, nullable=False)
    ngay_ket_thuc = db.Column(db.Date, nullable=False)
    ly_do = db.Column(db.UnicodeText)
    status = db.Column(db.Unicode(20), default="Approved")
    resident = db.relationship("NhanKhau", back_populates="tam_tru")

class TamVang(db.Model):
    __tablename__ = "tam_vang"
    id = db.Column(db.Integer, primary_key=True)
    resident_id = db.Column(db.Integer, db.ForeignKey("Nhan_khau.id"), nullable=False)
    noi_den = db.Column(db.Unicode(255), nullable=False)
    ngay_bat_dau = db.Column(db.Date, nullable=False)
    ngay_ket_thuc = db.Column(db.Date)
    ly_do = db.Column(db.UnicodeText)
    resident = db.relationship("NhanKhau", back_populates="tam_vang")

class TaiKhoan(UserMixin, db.Model):
    __tablename__ = "tai_khoan"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    ho_ten = db.Column(db.Unicode(100))
    ngay_tao = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(20), default="resident")
    nhan_khau_id = db.Column(db.Integer, db.ForeignKey("Nhan_khau.id"))

class YeuCau(db.Model):
    __tablename__ = "yeu_cau"
    id = db.Column(db.Integer, primary_key=True)
    nguoi_gui_id = db.Column(db.Integer, db.ForeignKey("tai_khoan.id"), nullable=False)
    loai_yeu_cau = db.Column(db.Unicode(50), nullable=False)
    noi_dung = db.Column(db.UnicodeText, nullable=False)
    ngay_gui = db.Column(db.DateTime, default=datetime.utcnow)
    trang_thai = db.Column(db.Unicode(50), default="Chờ xử lý")
    phan_hoi = db.Column(db.UnicodeText)
    nguoi_gui = db.relationship("TaiKhoan", backref="cac_yeu_cau")

# --- 3. Thu phí & Hóa đơn ---

class LoaiPhi(db.Model):
    __tablename__ = "LoaiPhi"
    id = db.Column(db.Integer, primary_key=True)
    ten_phi = db.Column(db.Unicode(100), nullable=False)
    don_gia = db.Column(db.Numeric(12,2), default=0) 
    don_vi = db.Column(db.Unicode(20), default="VND")
    bat_buoc = db.Column(db.Boolean, default=True)

class ChiSoDienNuoc(db.Model):
    __tablename__ = "ChiSoDienNuoc"
    id = db.Column(db.Integer, primary_key=True)
    ho_khau_id = db.Column(db.Integer, db.ForeignKey("Ho_khau.id"), nullable=False)
    thang = db.Column(db.String(7), nullable=False)
    chi_so_dien_cu = db.Column(db.Integer, default=0)
    chi_so_dien_moi = db.Column(db.Integer, nullable=False)
    chi_so_nuoc_cu = db.Column(db.Integer, default=0)
    chi_so_nuoc_moi = db.Column(db.Integer, nullable=False)
    ngay_ghi = db.Column(db.DateTime, default=datetime.utcnow)
    ho_khau = db.relationship("HoKhau", back_populates="chiso_diennuoc")

class GiaoDich(db.Model):
    __tablename__ = "Giao_dich"
    id = db.Column(db.Integer, primary_key=True)
    nhan_khau_id = db.Column(db.Integer, db.ForeignKey("Nhan_khau.id"), nullable=False)
    ho_khau_id = db.Column(db.Integer, db.ForeignKey("Ho_khau.id", ondelete="SET NULL"))
    loai_phi_id = db.Column(db.Integer, db.ForeignKey("LoaiPhi.id"), nullable=False)
    so_luong_tieu_thu = db.Column(db.Integer, default=0)
    don_gia_ap_dung = db.Column(db.Numeric(12,2), default=0)
    so_tien = db.Column(db.Numeric(12,2), nullable=False)
    phuong_thuc = db.Column(db.Unicode(50), nullable=False)
    ngay_nop = db.Column(db.DateTime, default=datetime.utcnow)
    trang_thai = db.Column(db.Unicode(50), default="Đang chờ")
    thong_bao_id = db.Column(db.Integer, db.ForeignKey("thong_bao.id"), nullable=True)
    bien_lai_id = db.Column(db.Integer, db.ForeignKey("BienLai.id"), nullable=True)

    nguoi_nop = db.relationship("NhanKhau", back_populates="giao_dich")
    loai_phi = db.relationship("LoaiPhi")
    ho_khau = db.relationship("HoKhau", back_populates="giao_dich")
    thuchi = db.relationship("ThuChi", back_populates="giao_dich", uselist=False)

class BienLai(db.Model):
    __tablename__ = "BienLai"
    id = db.Column(db.Integer, primary_key=True)
    ma_bien_lai = db.Column(db.String(50), unique=True, nullable=False) 
    ngay_thanh_toan = db.Column(db.DateTime, default=datetime.utcnow) 
    ho_khau_info = db.Column(db.Unicode(255)) 
    nguoi_thanh_toan = db.Column(db.Unicode(100))
    tong_tien = db.Column(db.Numeric(15,2), nullable=False) 
    chi_tiet = db.Column(db.UnicodeText) 
    giao_dichs = db.relationship("GiaoDich", backref="bien_lai")

class ThongBao(db.Model):
    __tablename__ = "thong_bao"
    id = db.Column(db.Integer, primary_key=True)
    nguoi_nhan_id = db.Column(db.Integer, db.ForeignKey("tai_khoan.id"), nullable=False)
    noi_dung = db.Column(db.UnicodeText, nullable=False)
    ngay_tao = db.Column(db.DateTime, default=datetime.utcnow)
    da_doc = db.Column(db.Boolean, default=False)
    loai_thong_bao = db.Column(db.Unicode(20), default="Hệ thống") 
    loai_phi_id = db.Column(db.Integer, db.ForeignKey("LoaiPhi.id"), nullable=True) 
    loai_phi = db.relationship("LoaiPhi")
    so_tien = db.Column(db.Numeric(12,2), nullable=True) 
    hinh_thuc_thu = db.Column(db.Unicode(20), nullable=True)

class ThuChi(db.Model):
    __tablename__ = "ThuChi"
    id = db.Column(db.Integer, primary_key=True)
    ho_khau_id = db.Column(db.Integer, db.ForeignKey("Ho_khau.id", ondelete="SET NULL"))
    loai_giao_dich = db.Column(db.Unicode(10), nullable=False)
    so_tien = db.Column(db.Numeric(15,2), nullable=False)
    hinh_thuc = db.Column(db.Unicode(50))
    ngay_giao_dich = db.Column(db.DateTime, default=datetime.utcnow)
    giao_dich_id = db.Column(db.Integer, db.ForeignKey("Giao_dich.id"))
    ghi_chu = db.Column(db.UnicodeText) 
    
    giao_dich = db.relationship("GiaoDich", back_populates="thuchi")
    ho_khau = db.relationship("HoKhau", back_populates="thuchi")