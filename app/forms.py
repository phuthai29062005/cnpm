from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, DecimalField, SubmitField, TextAreaField, RadioField, IntegerField, PasswordField
from wtforms.validators import DataRequired, Optional, ValidationError, EqualTo, Length
from wtforms_sqlalchemy.fields import QuerySelectField 
from .models import NhanKhau, HoKhau, LoaiPhi
from datetime import date

# Factory
def nhan_khau_choices(): return NhanKhau.query.all()
def ho_khau_choices(): return HoKhau.query.all()
def loai_phi_choices(): return LoaiPhi.query.order_by(LoaiPhi.ten_phi).all()

# Form Tìm kiếm (Dùng chung)
class SearchForm(FlaskForm):
    search_term = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Tìm')

class NhanKhauForm(FlaskForm):
    ho_ten = StringField('Họ tên', validators=[DataRequired()])
    bi_danh = StringField('Bí danh', validators=[Optional()])
    ngay_sinh = DateField('Ngày sinh', validators=[DataRequired()])
    gioi_tinh = SelectField('Giới tính', choices=[('Nam', 'Nam'), ('Nữ', 'Nữ')], validators=[DataRequired()])
    nguyen_quan = StringField('Nguyên quán')
    dan_toc = StringField('Dân tộc')
    nghe_nghiep = StringField('Nghề nghiệp')
    noi_lam_viec = StringField('Nơi làm việc')
    so_cccd = StringField('Số CCCD', validators=[Optional()])
    ngay_cap = DateField('Ngày cấp CCCD', validators=[Optional()])
    noi_cap = StringField('Nơi cấp CCCD')
    noi_thuong_tru = StringField('Nơi thường trú')
    tinh_trang = SelectField('Tình trạng', choices=[('Bình thường', 'Bình thường'), ('Tạm trú', 'Tạm trú'), ('Tạm vắng', 'Tạm vắng')], default='Bình thường')
    
    def validate_so_cccd(form, field):
        if form.ngay_sinh.data:
            age = (date.today() - form.ngay_sinh.data).days // 365
            if age >= 16 and not field.data:
                raise ValidationError("Trên 16 tuổi phải có CCCD")
    submit = SubmitField('Lưu')

class HoKhauForm(FlaskForm):
    ma_so_ho_khau = StringField('Mã Hộ khẩu', validators=[DataRequired()])
    chu_ho = QuerySelectField('Chủ hộ', query_factory=nhan_khau_choices, get_label='ho_ten', allow_blank=True, get_pk=lambda x: x.id)
    so_nha = StringField('Số nhà', validators=[DataRequired()])
    duong_pho = StringField('Đường/Phố', validators=[DataRequired()])
    phuong_xa = StringField('Phường/Xã', default='Đại Kim')
    quan_huyen = StringField('Quận/Huyện', default='Hoàng Mai')
    ghi_chu = TextAreaField('Ghi chú')
    submit = SubmitField('Lưu')

class NhanKhauHoKhauForm(FlaskForm):
    nhan_khau = QuerySelectField('Nhân khẩu', query_factory=nhan_khau_choices, get_label='ho_ten', allow_blank=False)
    ho_khau = QuerySelectField('Hộ khẩu', query_factory=ho_khau_choices, get_label='ma_so_ho_khau', allow_blank=False)
    quan_he_chu_ho = StringField('Quan hệ với chủ hộ', validators=[DataRequired()])
    submit = SubmitField('Thêm')

class GhiDienNuocForm(FlaskForm):
    ho_khau = QuerySelectField('Hộ khẩu', query_factory=ho_khau_choices, get_label='ma_so_ho_khau', allow_blank=False)
    thang = StringField('Tháng (YYYY-MM)', validators=[DataRequired()])
    chi_so_dien_moi = IntegerField('Điện Mới', validators=[DataRequired()])
    chi_so_nuoc_moi = IntegerField('Nước Mới', validators=[DataRequired()])
    submit = SubmitField('Tính tiền')

class TachKhauForm(FlaskForm):
    nhan_khau = QuerySelectField('Người tách', query_factory=nhan_khau_choices, get_label='ho_ten', allow_blank=False)
    loai_tach = SelectField('Hình thức', choices=[('new', 'Lập hộ mới'), ('existing', 'Chuyển hộ')], default='new')
    ho_khau_dich = QuerySelectField('Hộ đích', query_factory=ho_khau_choices, get_label='ma_so_ho_khau', allow_blank=True)
    quan_he_moi = StringField('Quan hệ mới')
    dia_chi_moi = StringField('Địa chỉ mới')
    submit = SubmitField('Tách')

class LoaiPhiForm(FlaskForm):
    ten_phi = StringField('Tên phí', validators=[DataRequired()])
    don_gia = DecimalField('Đơn giá', validators=[DataRequired()])
    don_vi = StringField('Đơn vị', validators=[DataRequired()])
    bat_buoc = SelectField('Tính chất', choices=[('1', 'Bắt buộc'), ('0', 'Tự nguyện')])
    submit = SubmitField('Cập nhật')

class GiaoDichForm(FlaskForm):
    nhan_khau = QuerySelectField('Người nộp', query_factory=nhan_khau_choices, get_label='ho_ten')
    ho_khau = QuerySelectField('Hộ', query_factory=ho_khau_choices, get_label='ma_so_ho_khau')
    loai_phi = QuerySelectField('Loại phí', query_factory=loai_phi_choices, get_label='ten_phi')
    so_tien = DecimalField('Tiền')
    phuong_thuc = SelectField('Cách nộp', choices=[('Tiền mặt', 'Tiền mặt'), ('Chuyển khoản', 'CK')])
    submit = SubmitField('Lưu')

class TamTruForm(FlaskForm):
    resident = QuerySelectField('Người ĐK', query_factory=nhan_khau_choices, get_label='ho_ten')
    noi_tam_tru = StringField('Nơi tạm trú', validators=[DataRequired()])
    ngay_bat_dau = DateField('Từ ngày', validators=[DataRequired()])
    ngay_ket_thuc = DateField('Đến ngày', validators=[DataRequired()])
    ly_do = TextAreaField('Lý do')
    submit = SubmitField('Đăng ký')

class ThongBaoForm(FlaskForm):
    loai_thong_bao = RadioField('Loại', choices=[('Thông tin', 'Thông tin'), ('Hóa đơn', 'Hóa đơn')], default='Thông tin')
    noi_dung = TextAreaField('Nội dung', validators=[DataRequired()])
    loai_phi = SelectField('Loại phí', coerce=int, validators=[Optional()])
    submit = SubmitField('Gửi')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Mật khẩu hiện tại', validators=[DataRequired()])
    new_password = PasswordField('Mật khẩu mới', validators=[DataRequired(), Length(min=1)])
    confirm_password = PasswordField('Nhập lại mật khẩu mới', validators=[DataRequired(), EqualTo('new_password', message='Mật khẩu không khớp')])
    submit = SubmitField('Lưu thay đổi')

class YeuCauForm(FlaskForm):
    loai_yeu_cau = SelectField('Loại yêu cầu', 
                               choices=[('Tách khẩu', 'Xin Tách khẩu'), 
                                        ('Chuyển hộ', 'Xin Chuyển hộ'), 
                                        ('Tạm trú', 'Đăng ký Tạm trú'), 
                                        ('Tạm vắng', 'Đăng ký Tạm vắng'),
                                        ('Khác', 'Khác')],
                               validators=[DataRequired()])
    noi_dung = TextAreaField('Nội dung chi tiết', validators=[DataRequired()])
    submit = SubmitField('Gửi Yêu Cầu')