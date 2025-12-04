from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError, DataError
from .forms import (
    NhanKhauForm, HoKhauForm, GiaoDichForm, TamTruForm, 
    NhanKhauHoKhauForm, ThongBaoForm, GhiDienNuocForm, TachKhauForm, LoaiPhiForm,
    KhaiSinhForm, KhaiTuForm
)
from .models import (
    db, NhanKhau, HoKhau, GiaoDich, TamTru, NhanKhauHoKhau, 
    TaiKhoan, ThongBao, LoaiPhi, ChiSoDienNuoc, LichSuHoKhau, BienLai, YeuCau
)
from werkzeug.security import generate_password_hash
from datetime import datetime
import uuid

crud = Blueprint('crud', __name__, url_prefix='/admin')

@crud.before_request
@login_required
def check_admin():
    if current_user.role != 'admin': abort(403)

# --- NHÂN KHẨU ---
@crud.route('/nhankhau/add', methods=['GET', 'POST'])
def add_nhankhau():
    form = NhanKhauForm()
    if form.validate_on_submit():
        new_nk = NhanKhau()
        form.populate_obj(new_nk)
        try:
            db.session.add(new_nk)
            db.session.flush()
            
            msg = ""
            if new_nk.so_cccd:
                # Kiểm tra trùng username
                if TaiKhoan.query.filter_by(username=new_nk.so_cccd).first():
                    raise ValueError(f"Tài khoản username '{new_nk.so_cccd}' đã tồn tại.")
                tk = TaiKhoan(username=new_nk.so_cccd, password_hash=generate_password_hash("1"), ho_ten=new_nk.ho_ten, role='resident', nhan_khau_id=new_nk.id)
                db.session.add(tk)
                msg = f'Đã thêm {new_nk.ho_ten} và tạo TK (Pass: 1)'
            else:
                msg = f'Đã thêm {new_nk.ho_ten} (Chưa tạo TK do thiếu CCCD)'
            
            db.session.commit()
            flash(msg, 'success')
            # [FIX] Giữ nguyên trang để hiện thông báo
            return redirect(request.url)

        except IntegrityError as e:
            db.session.rollback()
            err_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if 'UNIQUE KEY' in err_msg or 'duplicate key' in err_msg:
                flash(f'Lỗi: Số CCCD "{new_nk.so_cccd}" đã tồn tại.', 'danger')
            else:
                flash(f'Lỗi dữ liệu: {err_msg}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi hệ thống: {str(e)}', 'danger')
    
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                field_label = getattr(form, field).label.text if hasattr(form, field) else field
                flash(f'Lỗi ở ô "{field_label}": {error}', 'warning')

    return render_template('admin/create_form.html', form=form, title='Thêm Nhân khẩu')

@crud.route('/nhankhau/edit/<int:id>', methods=['GET', 'POST'])
def edit_nhankhau(id):
    nk = NhanKhau.query.get_or_404(id)
    form = NhanKhauForm(obj=nk)
    if form.validate_on_submit():
        try:
            form.populate_obj(nk)
            db.session.commit()
            flash('Cập nhật thành công', 'success')
            # [FIX] Giữ nguyên trang
            return redirect(request.url)
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi cập nhật: {str(e)}', 'danger')
            
    return render_template('admin/create_form.html', form=form, title='Sửa Nhân khẩu')

@crud.route('/nhankhau/delete/<int:id>', methods=['GET'])
def delete_nhankhau(id):
    # [NOTE] Xóa xong thì bắt buộc phải về danh sách (Dashboard), không thể ở lại trang của người đã xóa
    nk = NhanKhau.query.get_or_404(id)
    if GiaoDich.query.filter_by(nhan_khau_id=id, trang_thai='Đang chờ').first():
        flash('Không thể xóa vì còn nợ phí!', 'danger')
        return redirect(url_for('admin.index'))
    try:
        TaiKhoan.query.filter_by(nhan_khau_id=id).delete()
        NhanKhauHoKhau.query.filter_by(nhan_khau_id=id).delete()
        db.session.delete(nk)
        db.session.commit()
        flash('Đã xóa thành công', 'success')
    except Exception as e:
        db.session.rollback()
        flash(str(e), 'danger')
    return redirect(url_for('admin.index'))

# --- KHAI SINH & KHAI TỬ ---
@crud.route('/nhankhau/khaisinh', methods=['GET', 'POST'])
def khaisinh():
    form = KhaiSinhForm()
    if form.validate_on_submit():
        try:
            nk = NhanKhau(
                ho_ten=form.ho_ten.data, ngay_sinh=form.ngay_sinh.data,
                gioi_tinh=form.gioi_tinh.data, nguyen_quan=form.nguyen_quan.data,
                dan_toc=form.dan_toc.data, id_ho_khau=form.ho_khau.data.id,
                tinh_trang='Bình thường',
                noi_thuong_tru=form.ho_khau.data.so_nha + ", " + form.ho_khau.data.duong_pho
            )
            db.session.add(nk)
            db.session.commit()

            link = NhanKhauHoKhau(nhan_khau_id=nk.id, ho_khau_id=form.ho_khau.data.id, 
                                  quan_he_chu_ho=form.quan_he_chu_ho.data, ngay_bat_dau=form.ngay_sinh.data)
            db.session.add(link)
            db.session.add(LichSuHoKhau(ho_khau_id=form.ho_khau.data.id, noi_dung=f"Khai sinh: {nk.ho_ten}"))
            
            db.session.commit()
            flash(f'Đã khai sinh cho bé {nk.ho_ten}', 'success')
            # [FIX] Giữ nguyên trang
            return redirect(request.url)
        except Exception as e:
            db.session.rollback()
            flash(str(e), 'danger')

    return render_template('admin/create_form.html', form=form, title='Khai Sinh')

@crud.route('/nhankhau/khaitu', methods=['GET', 'POST'])
def khaitu():
    form = KhaiTuForm()
    if form.validate_on_submit():
        try:
            nk = form.nhan_khau.data
            hk_id = nk.id_ho_khau
            
            nk.tinh_trang = 'Qua đời'
            nk.ghi_chu = f"Mất ngày {form.ngay_mat.data}. Lý do: {form.ly_do.data}"
            nk.id_ho_khau = None
            
            NhanKhauHoKhau.query.filter_by(nhan_khau_id=nk.id).delete()
            if hk_id:
                db.session.add(LichSuHoKhau(ho_khau_id=hk_id, noi_dung=f"Thành viên {nk.ho_ten} qua đời."))
            TaiKhoan.query.filter_by(nhan_khau_id=nk.id).delete()

            db.session.commit()
            flash(f'Đã khai tử cho {nk.ho_ten}', 'success')
            # [FIX] Giữ nguyên trang
            return redirect(request.url)
        except Exception as e:
            db.session.rollback()
            flash(str(e), 'danger')
            
    return render_template('admin/create_form.html', form=form, title='Khai Tử')

# --- HỘ KHẨU ---
@crud.route('/hokhau/add', methods=['GET', 'POST'])
def add_hokhau():
    form = HoKhauForm()
    if form.validate_on_submit():
        try:
            hk = HoKhau()
            form.populate_obj(hk)
            hk.chu_ho = form.chu_ho.data
            db.session.add(hk)
            db.session.commit()
            
            if hk.chu_ho:
                hk.chu_ho.id_ho_khau = hk.id
                link = NhanKhauHoKhau(nhan_khau_id=hk.chu_ho_id, ho_khau_id=hk.id, quan_he_chu_ho="Chủ hộ")
                db.session.add(link)
                db.session.commit()

            flash('Thêm hộ khẩu thành công', 'success')
            # [FIX] Giữ nguyên trang
            return redirect(request.url)
        except Exception as e:
            db.session.rollback()
            flash(str(e), 'danger')
            
    return render_template('admin/create_form.html', form=form, title='Thêm Hộ khẩu')

@crud.route('/hokhau/edit/<int:id>', methods=['GET', 'POST'])
def edit_hokhau(id):
    hk = HoKhau.query.get_or_404(id)
    form = HoKhauForm(obj=hk)
    if form.validate_on_submit():
        try:
            form.populate_obj(hk)
            db.session.commit()
            flash('Cập nhật hộ khẩu thành công', 'success')
            # [FIX] Giữ nguyên trang
            return redirect(request.url)
        except Exception as e:
            db.session.rollback()
            flash(str(e), 'danger')
            
    return render_template('admin/create_form.html', form=form, title='Sửa Hộ khẩu')

@crud.route('/hokhau/delete/<int:id>', methods=['GET'])
def delete_hokhau(id):
    # [NOTE] Xóa xong thì về Dashboard
    hk = HoKhau.query.get_or_404(id)
    if GiaoDich.query.filter_by(ho_khau_id=id, trang_thai='Đang chờ').first():
        flash('Hộ này còn nợ phí, không thể xóa!', 'danger')
        return redirect(url_for('admin.index'))
    try:
        NhanKhau.query.filter_by(id_ho_khau=id).update({'id_ho_khau': None})
        db.session.delete(hk)
        db.session.commit()
        flash('Đã xóa hộ khẩu', 'success')
    except Exception as e:
        db.session.rollback()
        flash(str(e), 'danger')
    return redirect(url_for('admin.index'))

@crud.route('/hokhau/add_member', methods=['GET', 'POST'])
def add_member_to_hokhau():
    form = NhanKhauHoKhauForm()
    # Nhận tham số hokhau_id từ URL nếu có (để auto select khi bấm từ Dashboard)
    if request.method == 'GET' and request.args.get('hokhau_id'):
        hk = HoKhau.query.get(request.args.get('hokhau_id'))
        if hk: form.ho_khau.data = hk

    if form.validate_on_submit():
        try:
            nk = form.nhan_khau.data
            hk = form.ho_khau.data
            
            if nk.id_ho_khau:
                if nk.id_ho_khau == hk.id:
                    flash(f'{nk.ho_ten} đã ở trong hộ này rồi!', 'warning')
                    return redirect(request.url)
                else:
                    flash(f'Lỗi: {nk.ho_ten} đang thuộc hộ khác. Phải tách khẩu trước!', 'danger')
                    return redirect(request.url)
            
            link = NhanKhauHoKhau(nhan_khau_id=nk.id, ho_khau_id=hk.id, quan_he_chu_ho=form.quan_he_chu_ho.data)
            db.session.add(link)
            nk.id_ho_khau = hk.id
            db.session.add(LichSuHoKhau(ho_khau_id=hk.id, noi_dung=f"Thêm thành viên: {nk.ho_ten}"))
            
            db.session.commit()
            flash(f'Đã thêm {nk.ho_ten} vào hộ {hk.ma_so_ho_khau}', 'success')
            # [FIX] Giữ nguyên trang
            return redirect(request.url)
        except Exception as e:
            db.session.rollback()
            flash(str(e), 'danger')
            
    return render_template('admin/create_form.html', form=form, title='Thêm thành viên vào Hộ')

@crud.route('/hokhau/split', methods=['GET', 'POST'])
def split_household():
    form = TachKhauForm()
    
    if form.validate_on_submit():
        try:
            nk = form.nhan_khau.data
            old_hk_id = nk.id_ho_khau
            
            if GiaoDich.query.filter_by(nhan_khau_id=nk.id, trang_thai='Đang chờ').first():
                flash('Người này đang nợ phí cá nhân, không thể tách!', 'danger')
                return redirect(request.url)
            
            NhanKhauHoKhau.query.filter_by(nhan_khau_id=nk.id).delete()
            new_hk = None
            if form.loai_tach.data == 'new':
                new_hk = HoKhau(
                    ma_so_ho_khau=f"NEW-{datetime.now().timestamp()}", 
                    chu_ho_id=nk.id, 
                    so_nha=form.dia_chi_moi.data or "Chưa rõ", 
                    duong_pho="...", phuong_xa="...", quan_huyen="..."
                )
                db.session.add(new_hk)
                db.session.commit()
                target_hk_id = new_hk.id
                quan_he = "Chủ hộ"
                msg = f"Tách khẩu lập hộ mới. Chủ hộ: {nk.ho_ten}"
            else:
                if not form.ho_khau_dich.data:
                    flash('Vui lòng chọn Hộ đích!', 'danger')
                    return redirect(request.url)
                target_hk_id = form.ho_khau_dich.data.id
                quan_he = form.quan_he_moi.data or "Thành viên"
                msg = f"Chuyển đến từ hộ cũ."

            db.session.add(NhanKhauHoKhau(nhan_khau_id=nk.id, ho_khau_id=target_hk_id, quan_he_chu_ho=quan_he))
            nk.id_ho_khau = target_hk_id
            
            if old_hk_id: db.session.add(LichSuHoKhau(ho_khau_id=old_hk_id, noi_dung=f"Thành viên {nk.ho_ten} đã tách khẩu."))
            db.session.add(LichSuHoKhau(ho_khau_id=target_hk_id, noi_dung=f"Nhập khẩu: {nk.ho_ten}. {msg}"))
            
            db.session.commit()
            flash('Tách khẩu thành công', 'success')
            # [FIX] Giữ nguyên trang
            return redirect(request.url)
        except Exception as e:
            db.session.rollback()
            flash(str(e), 'danger')
            
    return render_template('admin/create_form.html', form=form, title='Tách Khẩu / Chuyển Khẩu')

# --- THÔNG BÁO & GIAO DỊCH ---
@crud.route('/thongbao/add', methods=['GET', 'POST'])
def add_thongbao():
    form = ThongBaoForm()
    choices = [(0, "--- Không (Tin tức) ---")] + [(f.id, f.ten_phi) for f in LoaiPhi.query.all()]
    form.loai_phi.choices = choices

    if form.validate_on_submit():
        if form.loai_thong_bao.data == 'Thông tin':
            all_residents = TaiKhoan.query.filter_by(role='resident').all()
            if not all_residents:
                flash("Chưa có cư dân nào để gửi!", "warning")
            else:
                for res in all_residents:
                    db.session.add(ThongBao(nguoi_nhan_id=res.id, noi_dung=form.noi_dung.data, loai_thong_bao='Hệ thống'))
                db.session.commit()
                flash(f"Đã gửi tin tức cho {len(all_residents)} cư dân.", "success")
            # [FIX] Giữ nguyên trang
            return redirect(request.url)
        else:
            flash("Vui lòng dùng chức năng 'Ghi Điện/Nước' hoặc 'Thêm Giao dịch' để thu phí.", "info")
            return redirect(url_for('crud.record_indices'))

    return render_template('admin/create_form.html', form=form, title='Gửi Thông Báo Chung')

@crud.route('/billing/record', methods=['GET', 'POST'])
def record_indices():
    form = GhiDienNuocForm()
    if request.method == 'GET': form.thang.data = datetime.now().strftime('%Y-%m')
    if form.validate_on_submit():
        try:
            hk = form.ho_khau.data
            dien_moi, nuoc_moi = form.chi_so_dien_moi.data, form.chi_so_nuoc_moi.data
            
            if dien_moi < (hk.so_dien or 0) or nuoc_moi < (hk.so_nuoc or 0):
                flash('Chỉ số mới không được nhỏ hơn chỉ số cũ!', 'danger')
                return redirect(request.url)
            
            db.session.add(ChiSoDienNuoc(ho_khau_id=hk.id, thang=form.thang.data, chi_so_dien_cu=hk.so_dien, chi_so_dien_moi=dien_moi, chi_so_nuoc_cu=hk.so_nuoc, chi_so_nuoc_moi=nuoc_moi))
            
            phi_dien = LoaiPhi.query.filter_by(ten_phi="Phí điện").first()
            phi_nuoc = LoaiPhi.query.filter_by(ten_phi="Phí nước sinh hoạt").first()
            
            if not phi_dien: flash('Cảnh báo: Không tìm thấy "Phí điện".', 'warning')
            if not phi_nuoc: flash('Cảnh báo: Không tìm thấy "Phí nước sinh hoạt".', 'warning')

            if phi_dien and (dien_moi - hk.so_dien) > 0:
                amt = (dien_moi - hk.so_dien) * float(phi_dien.don_gia or 0)
                db.session.add(GiaoDich(nhan_khau_id=hk.chu_ho_id, ho_khau_id=hk.id, loai_phi_id=phi_dien.id, so_tien=amt, so_luong_tieu_thu=(dien_moi - hk.so_dien), don_gia_ap_dung=phi_dien.don_gia, phuong_thuc='Chưa nộp'))
            
            if phi_nuoc and (nuoc_moi - hk.so_nuoc) > 0:
                amt = (nuoc_moi - hk.so_nuoc) * float(phi_nuoc.don_gia or 0)
                db.session.add(GiaoDich(nhan_khau_id=hk.chu_ho_id, ho_khau_id=hk.id, loai_phi_id=phi_nuoc.id, so_tien=amt, so_luong_tieu_thu=(nuoc_moi - hk.so_nuoc), don_gia_ap_dung=phi_nuoc.don_gia, phuong_thuc='Chưa nộp'))

            hk.so_dien, hk.so_nuoc = dien_moi, nuoc_moi
            
            members = NhanKhau.query.filter_by(id_ho_khau=hk.id).all()
            member_ids = [m.id for m in members]
            accounts = TaiKhoan.query.filter(TaiKhoan.nhan_khau_id.in_(member_ids)).all()
            
            for acc in accounts:
                db.session.add(ThongBao(nguoi_nhan_id=acc.id, noi_dung=f"Đã có hóa đơn tháng {form.thang.data}.", loai_thong_bao="Hóa đơn"))
            
            db.session.commit()
            flash('Đã ghi chỉ số và tạo hóa đơn thành công', 'success')
            # [FIX] Giữ nguyên trang
            return redirect(request.url)
        except Exception as e:
            db.session.rollback()
            flash(str(e), 'danger')
            
    return render_template('admin/create_form.html', form=form, title='Ghi Điện Nước')

@crud.route('/billing/pay/<int:gd_id>', methods=['GET'])
def pay_bill(gd_id):
    # [NOTE] Thanh toán xong thì phải về Dashboard để xem list hóa đơn
    gd = GiaoDich.query.get_or_404(gd_id)
    if gd.trang_thai == 'Đã thanh toán': return redirect(url_for('admin.index'))
    try:
        gd.trang_thai = 'Đã thanh toán'
        gd.ngay_nop = datetime.now()
        rec = BienLai(ma_bien_lai=f"BL-{uuid.uuid4().hex[:6].upper()}", nguoi_thanh_toan=gd.nguoi_nop.ho_ten, ho_khau_info=gd.ho_khau.ma_so_ho_khau, tong_tien=gd.so_tien, chi_tiet=f"Thu {gd.loai_phi.ten_phi}")
        db.session.add(rec)
        db.session.flush()
        gd.bien_lai_id = rec.id
        
        # Xóa thông báo nợ
        nk_ids = [nk.id for nk in NhanKhau.query.filter_by(id_ho_khau=gd.ho_khau_id).all()]
        if nk_ids:
            acc_ids = [tk.id for tk in TaiKhoan.query.filter(TaiKhoan.nhan_khau_id.in_(nk_ids)).all()]
            if acc_ids:
                ThongBao.query.filter(ThongBao.nguoi_nhan_id.in_(acc_ids), ThongBao.loai_thong_bao == 'Hóa đơn').delete(synchronize_session=False)

        db.session.commit()
        flash('Thanh toán thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(str(e), 'danger')
    return redirect(url_for('admin.index'))

@crud.route('/loaiphi', methods=['GET'])
def list_loaiphi():
    return render_template('admin/list_loaiphi.html', fees=LoaiPhi.query.all())

@crud.route('/loaiphi/edit/<int:id>', methods=['GET', 'POST'])
def edit_loaiphi(id):
    fee = LoaiPhi.query.get_or_404(id)
    form = LoaiPhiForm(obj=fee)
    if request.method == 'GET': form.bat_buoc.data = '1' if fee.bat_buoc else '0'
    if form.validate_on_submit():
        try:
            form.populate_obj(fee)
            fee.bat_buoc = (form.bat_buoc.data == '1')
            db.session.commit()
            flash('Cập nhật giá thành công', 'success')
            # [FIX] Giữ nguyên trang để sửa tiếp nếu cần
            return redirect(request.url)
        except Exception as e:
            db.session.rollback()
            flash(str(e), 'danger')
    return render_template('admin/create_form.html', form=form, title='Sửa Giá')

@crud.route('/tamtru/add', methods=['GET', 'POST'])
def add_tamtru():
    form = TamTruForm()
    if form.validate_on_submit():
        try:
            if form.ngay_ket_thuc.data < form.ngay_bat_dau.data:
                flash('Ngày kết thúc không hợp lệ', 'danger')
                return redirect(request.url)
            db.session.add(TamTru(resident_id=form.resident.data.id, noi_tam_tru=form.noi_tam_tru.data, ngay_bat_dau=form.ngay_bat_dau.data, ngay_ket_thuc=form.ngay_ket_thuc.data, ly_do=form.ly_do.data))
            nk = NhanKhau.query.get(form.resident.data.id)
            nk.tinh_trang = 'Tạm trú'
            db.session.commit()
            flash('Đã đăng ký tạm trú', 'success')
            # [FIX] Giữ nguyên trang
            return redirect(request.url)
        except Exception as e:
            db.session.rollback()
            flash(str(e), 'danger')
    return render_template('admin/create_form.html', form=form, title='Đăng ký Tạm trú')

@crud.route('/giaodich/add', methods=['GET', 'POST'])
def add_giaodich():
    form = GiaoDichForm()
    if form.validate_on_submit():
        try:
            new_gd = GiaoDich(nhan_khau_id=form.nhan_khau.data.id, ho_khau_id=form.ho_khau.data.id, loai_phi_id=form.loai_phi.data.id, so_tien=form.so_tien.data, phuong_thuc=form.phuong_thuc.data, trang_thai='Đã xác nhận')
            db.session.add(new_gd)
            db.session.commit()
            flash('Thêm giao dịch thành công', 'success')
            # [FIX] Giữ nguyên trang
            return redirect(request.url)
        except Exception as e:
            db.session.rollback()
            flash(str(e), 'danger')
    return render_template('admin/create_form.html', form=form, title='Thêm Giao dịch')

@crud.route('/giaodich/delete/<int:id>', methods=['GET'])
def delete_giaodich(id):
    # [NOTE] Xóa xong về Dashboard
    db.session.delete(GiaoDich.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('admin.index'))

@crud.route('/tamtru/delete/<int:id>', methods=['GET'])
def delete_tamtru(id):
    # [NOTE] Xóa xong về Dashboard
    tt = TamTru.query.get_or_404(id)
    nk = NhanKhau.query.get(tt.resident_id)
    if nk: nk.tinh_trang = 'Bình thường'
    db.session.delete(tt)
    db.session.commit()
    return redirect(url_for('admin.index'))

@crud.route('/requests', methods=['GET'])
def list_requests():
    requests = YeuCau.query.order_by(YeuCau.ngay_gui.desc()).all()
    return render_template('admin/list_requests.html', requests=requests)

@crud.route('/requests/update/<int:id>/<string:action>', methods=['GET'])
def update_request(id, action):
    req = YeuCau.query.get_or_404(id)
    if action == 'approve':
        req.trang_thai = 'Đã xử lý'
        db.session.add(ThongBao(nguoi_nhan_id=req.nguoi_gui_id, noi_dung=f"Yêu cầu '{req.loai_yeu_cau}' đã được xử lý.", loai_thong_bao="Hệ thống"))
        flash('Đã đánh dấu xử lý.', 'success')
    elif action == 'reject':
        req.trang_thai = 'Từ chối'
        db.session.add(ThongBao(nguoi_nhan_id=req.nguoi_gui_id, noi_dung=f"Yêu cầu '{req.loai_yeu_cau}' bị từ chối.", loai_thong_bao="Hệ thống"))
        flash('Đã từ chối.', 'warning')
    db.session.commit()
    # [FIX] Vẫn ở trang danh sách yêu cầu
    return redirect(url_for('crud.list_requests'))