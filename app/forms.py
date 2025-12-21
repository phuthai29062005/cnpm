from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, DecimalField, SubmitField, TextAreaField, RadioField, IntegerField, PasswordField
from wtforms.validators import DataRequired, Optional, ValidationError, EqualTo, Length
from wtforms_sqlalchemy.fields import QuerySelectField 
from .models import NhanKhau, HoKhau, LoaiPhi
from datetime import date

def nhan_khau_choices(): 
    return NhanKhau.query.filter(NhanKhau.tinh_trang == 'Bình thường').all()

def ho_khau_choices(): 
    return HoKhau.query.all()

def loai_phi_choices(): 
    return LoaiPhi.query.order_by(LoaiPhi.ten_phi).all()

# --- FORM TÌM KIẾM ---
class SearchForm(FlaskForm):
    search_term = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Tìm')

# --- FORM NHÂN KHẨU ---
class NhanKhauForm(FlaskForm):
    ho_ten = StringField('Họ tên', validators=[DataRequired(), Length(max=100)])
    bi_danh = StringField('Bí danh', validators=[Optional(), Length(max=50)])
    ngay_sinh = DateField('Ngày sinh', validators=[DataRequired()])
    gioi_tinh = SelectField('Giới tính', choices=[('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Khác', 'Khác')], validators=[DataRequired()])
    nguyen_quan = StringField('Nguyên quán', validators=[DataRequired(), Length(max=255)])
    dan_toc = StringField('Dân tộc', validators=[DataRequired(), Length(max=50)])
    nghe_nghiep = StringField('Nghề nghiệp', validators=[Optional(), Length(max=100)])
    noi_lam_viec = StringField('Nơi làm việc', validators=[Optional(), Length(max=100)])
    so_cccd = StringField('Số CCCD', validators=[Optional(), Length(max=12)])
    ngay_cap = DateField('Ngày cấp CCCD', validators=[Optional()])
    noi_cap = StringField('Nơi cấp CCCD', validators=[Optional(), Length(max=100)])
    noi_thuong_tru = StringField('Nơi thường trú', validators=[DataRequired(), Length(max=255)])
    tinh_trang = SelectField('Tình trạng', choices=[('Bình thường', 'Bình thường'), ('Tạm trú', 'Tạm trú'), ('Tạm vắng', 'Tạm vắng')], default='Bình thường')
    submit = SubmitField('Lưu')

    def check_age_requirement(self, field, field_name):
        if self.ngay_sinh.data:
            today = date.today()
            age = today.year - self.ngay_sinh.data.year - ((today.month, today.day) < (self.ngay_sinh.data.month, self.ngay_sinh.data.day))
            if age >= 16 and not field.data:
                raise ValidationError(f"Công dân từ 16 tuổi trở lên bắt buộc phải điền {field_name}.")

    def validate_so_cccd(form, field): form.check_age_requirement(field, "Số CCCD")
    def validate_ngay_cap(form, field): form.check_age_requirement(field, "Ngày cấp CCCD")
    def validate_noi_cap(form, field): form.check_age_requirement(field, "Nơi cấp CCCD")

# --- FORM HỘ KHẨU ---
class HoKhauForm(FlaskForm):
    ma_so_ho_khau = StringField('Mã Hộ khẩu', validators=[DataRequired()])
    # [FIX] Thêm CCCD vào label
    chu_ho = QuerySelectField('Chủ hộ', query_factory=nhan_khau_choices, 
                              get_label=lambda x: f"{x.ho_ten} - CCCD: {x.so_cccd if x.so_cccd else 'N/A'}", 
                              allow_blank=True)
    so_nha = StringField('Số nhà', validators=[DataRequired()])
    duong_pho = StringField('Đường/Phố', validators=[DataRequired()])
    phuong_xa = StringField('Phường/Xã', default='Đại Kim')
    quan_huyen = StringField('Quận/Huyện', default='Hoàng Mai')
    ghi_chu = TextAreaField('Ghi chú')
    submit = SubmitField('Lưu')

class NhanKhauHoKhauForm(FlaskForm):
    # [FIX] Thêm CCCD và Địa chỉ
    nhan_khau = QuerySelectField('Nhân khẩu', query_factory=nhan_khau_choices, 
                                 get_label=lambda x: f"{x.ho_ten} - CCCD: {x.so_cccd if x.so_cccd else 'N/A'}")
    ho_khau = QuerySelectField('Hộ khẩu', query_factory=ho_khau_choices, 
                               get_label=lambda x: f"{x.ma_so_ho_khau} - {x.so_nha} {x.duong_pho}")
    quan_he_chu_ho = StringField('Quan hệ với chủ hộ', validators=[DataRequired()])
    submit = SubmitField('Thêm vào Hộ')

class TachKhauForm(FlaskForm):
    # [FIX] Thêm CCCD và Địa chỉ
    nhan_khau = QuerySelectField('Người tách', query_factory=nhan_khau_choices, 
                                 get_label=lambda x: f"{x.ho_ten} - CCCD: {x.so_cccd if x.so_cccd else 'N/A'}", 
                                 allow_blank=False)
    loai_tach = SelectField('Hình thức', choices=[('new', 'Lập hộ mới'), ('existing', 'Chuyển sang Hộ khác')], default='new')
    ho_khau_dich = QuerySelectField('Hộ đích (Nếu chuyển)', query_factory=ho_khau_choices, 
                                    get_label=lambda x: f"{x.ma_so_ho_khau} - {x.so_nha} {x.duong_pho}", allow_blank=True)
    quan_he_moi = StringField('Quan hệ với chủ hộ mới')
    dia_chi_moi = StringField('Địa chỉ mới (Nếu lập hộ mới)')
    submit = SubmitField('Thực hiện Tách')

class KhaiSinhForm(FlaskForm):
    ho_ten = StringField('Họ tên trẻ', validators=[DataRequired()])
    gioi_tinh = SelectField('Giới tính', choices=[('Nam', 'Nam'), ('Nữ', 'Nữ')], validators=[DataRequired()])
    ngay_sinh = DateField('Ngày sinh', validators=[DataRequired()], default=date.today)
    # [FIX] Thêm Địa chỉ
    ho_khau = QuerySelectField('Thuộc Hộ khẩu', query_factory=ho_khau_choices, 
                               get_label=lambda x: f"{x.ma_so_ho_khau} - {x.so_nha} {x.duong_pho}", allow_blank=False)
    quan_he_chu_ho = StringField('Quan hệ với chủ hộ', validators=[DataRequired()], default="Con")
    nguyen_quan = StringField('Nguyên quán', validators=[DataRequired()])
    dan_toc = StringField('Dân tộc', default='Kinh', validators=[DataRequired()])
    submit = SubmitField('Khai Sinh')

class KhaiTuForm(FlaskForm):
    # [FIX] Thêm CCCD
    nhan_khau = QuerySelectField('Người mất', query_factory=nhan_khau_choices, 
                                 get_label=lambda x: f"{x.ho_ten} - CCCD: {x.so_cccd if x.so_cccd else 'N/A'}")
    ngay_mat = DateField('Ngày mất', validators=[DataRequired()], default=date.today)
    ly_do = TextAreaField('Lý do mất', validators=[DataRequired()])
    submit = SubmitField('Xác nhận Khai Tử')

class ThongBaoForm(FlaskForm):
    noi_dung = TextAreaField('Nội dung thông báo', validators=[DataRequired()])
    submit = SubmitField('Gửi Thông Báo')

class GhiDienNuocForm(FlaskForm):
    # [FIX] Thêm Địa chỉ
    ho_khau = QuerySelectField('Hộ khẩu', query_factory=ho_khau_choices, 
                               get_label=lambda x: f"{x.ma_so_ho_khau} - {x.so_nha} {x.duong_pho}", allow_blank=False)
    thang = StringField('Tháng (YYYY-MM)', validators=[DataRequired()])
    chi_so_dien_moi = IntegerField('Điện Mới', validators=[DataRequired()])
    chi_so_nuoc_moi = IntegerField('Nước Mới', validators=[DataRequired()])
    submit = SubmitField('Tính tiền')

class LoaiPhiForm(FlaskForm):
    ten_phi = StringField('Tên phí', validators=[DataRequired()])
    don_gia = DecimalField('Đơn giá', validators=[DataRequired()])
    don_vi = StringField('Đơn vị', validators=[DataRequired()])
    bat_buoc = SelectField('Tính chất', choices=[('1', 'Bắt buộc'), ('0', 'Tự nguyện')])
    submit = SubmitField('Cập nhật')

class GiaoDichForm(FlaskForm):
    # [FIX] Thêm CCCD và Địa chỉ
    nhan_khau = QuerySelectField('Người nộp', query_factory=nhan_khau_choices, 
                                 get_label=lambda x: f"{x.ho_ten} - CCCD: {x.so_cccd if x.so_cccd else 'N/A'}")
    ho_khau = QuerySelectField('Hộ khẩu', query_factory=ho_khau_choices, 
                               get_label=lambda x: f"{x.ma_so_ho_khau} - Địa chỉ: {x.so_nha} {x.duong_pho}")
    loai_phi = QuerySelectField('Loại phí', query_factory=loai_phi_choices, get_label='ten_phi')
    so_tien = DecimalField('Tiền')
    phuong_thuc = SelectField('Cách nộp', choices=[('Tiền mặt', 'Tiền mặt'), ('Chuyển khoản', 'CK')])
    submit = SubmitField('Lưu')

class TamTruForm(FlaskForm):
    # [FIX] Thêm CCCD
    resident = QuerySelectField('Người ĐK', query_factory=nhan_khau_choices, 
                                get_label=lambda x: f"{x.ho_ten} - CCCD: {x.so_cccd if x.so_cccd else 'N/A'}")
    noi_tam_tru = StringField('Nơi tạm trú', validators=[DataRequired()])
    ngay_bat_dau = DateField('Từ ngày', validators=[DataRequired()])
    ngay_ket_thuc = DateField('Đến ngày', validators=[DataRequired()])
    ly_do = TextAreaField('Lý do')
    submit = SubmitField('Đăng ký')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Mật khẩu hiện tại', validators=[DataRequired()])
    new_password = PasswordField('Mật khẩu mới', validators=[DataRequired(), Length(min=1)])
    confirm_password = PasswordField('Nhập lại mật khẩu mới', validators=[DataRequired(), EqualTo('new_password', message='Mật khẩu không khớp')])
    submit = SubmitField('Lưu thay đổi')

class YeuCauForm(FlaskForm):
    loai_yeu_cau = SelectField('Loại yêu cầu', 
                               choices=[('sửa chữa', 'Sửa chữa'), ('khiếu nại', 'Khiếu nại'), ('đề xuất', 'Đề xuất'), ('khác', 'Khác'),
                                        ('Tách khẩu', 'Xin Tách khẩu'), ('Chuyển hộ', 'Xin Chuyển hộ'),
                                        ('Tạm trú', 'Đăng ký Tạm trú'), ('Tạm vắng', 'Đăng ký Tạm vắng')],
                               validators=[DataRequired(), Length(max=50)])
    noi_dung = TextAreaField('Nội dung chi tiết', validators=[DataRequired()])
    submit = SubmitField('Gửi Yêu Cầu')