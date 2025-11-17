from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from .forms import (
    NhanKhauForm, HoKhauForm, GiaoDichForm, TamTruForm, 
    NhanKhauHoKhauForm, ThongBaoForm, GhiDienNuocForm, TachKhauForm, LoaiPhiForm
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
            db.session.commit()
            if new_nk.so_cccd:
                tk = TaiKhoan(username=new_nk.so_cccd, password_hash=generate_password_hash("1"), ho_ten=new_nk.ho_ten, role='resident', nhan_khau_id=new_nk.id)
                db.session.add(tk)
                db.session.commit()
                flash(f'Đã tạo TK cho {new_nk.ho_ten} (Pass: 1)', 'success')
            return redirect(url_for('admin.index'))
        except Exception as e:
            db.session.rollback()
            flash(str(e), 'danger')
    return render_template('admin/create_form.html', form=form, title='Thêm Nhân khẩu')

@crud.route('/nhankhau/edit/<int:id>', methods=['GET', 'POST'])
def edit_nhankhau(id):
    nk = NhanKhau.query.get_or_404(id)
    form = NhanKhauForm(obj=nk)
    if form.validate_on_submit():
        form.populate_obj(nk)
        db.session.commit()
        flash('Cập nhật thành công', 'success')
        return redirect(url_for('admin.index'))
    return render_template('admin/create_form.html', form=form, title='Sửa Nhân khẩu')

@crud.route('/nhankhau/delete/<int:id>', methods=['GET'])
def delete_nhankhau(id):
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

# --- HỘ KHẨU ---
@crud.route('/hokhau/add', methods=['GET', 'POST'])
def add_hokhau():
    form = HoKhauForm()
    if form.validate_on_submit():
        hk = HoKhau()
        form.populate_obj(hk)
        hk.chu_ho = form.chu_ho.data
        db.session.add(hk)
        db.session.commit()
        flash('Thêm hộ khẩu thành công', 'success')
        return redirect(url_for('admin.index'))
    return render_template('admin/create_form.html', form=form, title='Thêm Hộ khẩu')

@crud.route('/hokhau/edit/<int:id>', methods=['GET', 'POST'])
def edit_hokhau(id):
    hk = HoKhau.query.get_or_404(id)
    form = HoKhauForm(obj=hk)
    if form.validate_on_submit():
        form.populate_obj(hk)
        hk.chu_ho = form.chu_ho.data
        db.session.commit()
        flash('Cập nhật hộ khẩu thành công', 'success')
        return redirect(url_for('admin.index'))
    return render_template('admin/create_form.html', form=form, title='Sửa Hộ khẩu')

@crud.route('/hokhau/delete/<int:id>', methods=['GET'])
def delete_hokhau(id):
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
    if form.validate_on_submit():
        nk = NhanKhau.query.get(form.nhan_khau.data.id)
        if nk.id_ho_khau:
            flash(f'Lỗi: {nk.ho_ten} đang thuộc hộ khác!', 'danger')
            return redirect(url_for('admin.index'))
        
        link = NhanKhauHoKhau(nhan_khau_id=nk.id, ho_khau_id=form.ho_khau.data.id, quan_he_chu_ho=form.quan_he_chu_ho.data)
        db.session.add(link)
        nk.id_ho_khau = form.ho_khau.data.id
        db.session.add(LichSuHoKhau(ho_khau_id=form.ho_khau.data.id, noi_dung=f"Thêm thành viên: {nk.ho_ten} ({form.quan_he_chu_ho.data})"))
        db.session.commit()
        flash('Đã thêm thành viên', 'success')
        return redirect(url_for('admin.index'))
    return render_template('admin/create_form.html', form=form, title='Thêm thành viên')

@crud.route('/hokhau/split', methods=['GET', 'POST'])
def split_household():
    form = TachKhauForm()
    if form.validate_on_submit():
        nk = form.nhan_khau.data
        if GiaoDich.query.filter_by(nhan_khau_id=nk.id, trang_thai='Đang chờ').first():
            flash('Đang nợ phí, không thể tách!', 'danger')
            return redirect(url_for('admin.index'))
        try:
            old_hk_id = nk.id_ho_khau
            if form.loai_tach.data == 'new':
                new_hk = HoKhau(ma_so_ho_khau=f"NEW-{datetime.now().timestamp()}", chu_ho_id=nk.id, so_nha=form.dia_chi_moi.data, duong_pho="...", phuong_xa="...", quan_huyen="...")
                db.session.add(new_hk)
                db.session.commit()
                nk.id_ho_khau = new_hk.id
                db.session.add(LichSuHoKhau(ho_khau_id=new_hk.id, noi_dung=f"Tách khẩu lập hộ mới. Chủ hộ: {nk.ho_ten}"))
            else:
                target = form.ho_khau_dich.data
                nk.id_ho_khau = target.id
                db.session.add(NhanKhauHoKhau(nhan_khau_id=nk.id, ho_khau_id=target.id, quan_he_chu_ho=form.quan_he_moi.data))
                db.session.add(LichSuHoKhau(ho_khau_id=target.id, noi_dung=f"Nhập khẩu: {nk.ho_ten}"))
            
            if old_hk_id:
                db.session.add(LichSuHoKhau(ho_khau_id=old_hk_id, noi_dung=f"Thành viên {nk.ho_ten} chuyển đi."))
            
            db.session.commit()
            flash('Tách khẩu thành công', 'success')
            return redirect(url_for('admin.index'))
        except Exception as e:
            db.session.rollback()
            flash(str(e), 'danger')
    return render_template('admin/create_form.html', form=form, title='Tách Khẩu')

# --- THANH TOÁN ---
@crud.route('/billing/record', methods=['GET', 'POST'])
def record_indices():
    form = GhiDienNuocForm()
    if request.method == 'GET': form.thang.data = datetime.now().strftime('%Y-%m')
    if form.validate_on_submit():
        hk = form.ho_khau.data
        dien_moi, nuoc_moi = form.chi_so_dien_moi.data, form.chi_so_nuoc_moi.data
        
        if dien_moi < (hk.so_dien or 0) or nuoc_moi < (hk.so_nuoc or 0):
            flash('Chỉ số mới không được nhỏ hơn chỉ số cũ!', 'danger')
            return render_template('admin/create_form.html', form=form, title='Ghi Điện Nước')
        
        try:
            db.session.add(ChiSoDienNuoc(ho_khau_id=hk.id, thang=form.thang.data, chi_so_dien_cu=hk.so_dien, chi_so_dien_moi=dien_moi, chi_so_nuoc_cu=hk.so_nuoc, chi_so_nuoc_moi=nuoc_moi))
            
            phi_dien = LoaiPhi.query.filter_by(ten_phi="Phí điện").first()
            phi_nuoc = LoaiPhi.query.filter_by(ten_phi="Phí nước sinh hoạt").first()
            
            if phi_dien and (dien_moi - hk.so_dien) > 0:
                amt = (dien_moi - hk.so_dien) * float(phi_dien.don_gia)
                db.session.add(GiaoDich(nhan_khau_id=hk.chu_ho_id, ho_khau_id=hk.id, loai_phi_id=phi_dien.id, so_tien=amt, so_luong_tieu_thu=(dien_moi - hk.so_dien), don_gia_ap_dung=phi_dien.don_gia, phuong_thuc='Chưa nộp'))
            
            if phi_nuoc and (nuoc_moi - hk.so_nuoc) > 0:
                amt = (nuoc_moi - hk.so_nuoc) * float(phi_nuoc.don_gia)
                db.session.add(GiaoDich(nhan_khau_id=hk.chu_ho_id, ho_khau_id=hk.id, loai_phi_id=phi_nuoc.id, so_tien=amt, so_luong_tieu_thu=(nuoc_moi - hk.so_nuoc), don_gia_ap_dung=phi_nuoc.don_gia, phuong_thuc='Chưa nộp'))

            hk.so_dien, hk.so_nuoc = dien_moi, nuoc_moi
            
            # Thông báo cho cả hộ
            nk_ids = [nk.id for nk in NhanKhau.query.filter_by(id_ho_khau=hk.id).all()]
            if nk_ids:
                acc_ids = [tk.id for tk in TaiKhoan.query.filter(TaiKhoan.nhan_khau_id.in_(nk_ids)).all()]
                for acc_id in acc_ids:
                    db.session.add(ThongBao(nguoi_nhan_id=acc_id, noi_dung=f"Hóa đơn tháng {form.thang.data}", loai_thong_bao="Hóa đơn"))
            
            db.session.commit()
            flash('Đã tạo hóa đơn', 'success')
            return redirect(url_for('admin.index'))
        except Exception as e:
            db.session.rollback()
            flash(str(e), 'danger')
    return render_template('admin/create_form.html', form=form, title='Ghi Điện Nước')

@crud.route('/billing/pay/<int:gd_id>', methods=['GET'])
def pay_bill(gd_id):
    gd = GiaoDich.query.get_or_404(gd_id)
    if gd.trang_thai == 'Đã thanh toán': return redirect(url_for('admin.index'))
    try:
        gd.trang_thai = 'Đã thanh toán'
        gd.ngay_nop = datetime.now()
        rec = BienLai(ma_bien_lai=f"BL-{uuid.uuid4().hex[:6].upper()}", nguoi_thanh_toan=gd.nguoi_nop.ho_ten, ho_khau_info=gd.ho_khau.ma_so_ho_khau, tong_tien=gd.so_tien, chi_tiet=f"Thu {gd.loai_phi.ten_phi}")
        db.session.add(rec)
        db.session.flush()
        gd.bien_lai_id = rec.id
        
        # Xóa thông báo cả hộ
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
        form.populate_obj(fee)
        fee.bat_buoc = (form.bat_buoc.data == '1')
        db.session.commit()
        flash('Cập nhật giá thành công', 'success')
        return redirect(url_for('crud.list_loaiphi'))
    return render_template('admin/create_form.html', form=form, title='Sửa Giá')

@crud.route('/tamtru/add', methods=['GET', 'POST'])
def add_tamtru():
    form = TamTruForm()
    if form.validate_on_submit():
        if form.ngay_ket_thuc.data < form.ngay_bat_dau.data:
            flash('Ngày kết thúc không hợp lệ', 'danger')
            return render_template('admin/create_form.html', form=form, title='Đăng ký Tạm trú')
        db.session.add(TamTru(resident_id=form.resident.data.id, noi_tam_tru=form.noi_tam_tru.data, ngay_bat_dau=form.ngay_bat_dau.data, ngay_ket_thuc=form.ngay_ket_thuc.data, ly_do=form.ly_do.data))
        nk = NhanKhau.query.get(form.resident.data.id)
        nk.tinh_trang = 'Tạm trú'
        db.session.commit()
        flash('Đã đăng ký tạm trú', 'success')
        return redirect(url_for('admin.index'))
    return render_template('admin/create_form.html', form=form, title='Đăng ký Tạm trú')

@crud.route('/giaodich/add', methods=['GET', 'POST'])
def add_giaodich():
    form = GiaoDichForm()
    if form.validate_on_submit():
        new_gd = GiaoDich(nhan_khau_id=form.nhan_khau.data.id, ho_khau_id=form.ho_khau.data.id, loai_phi_id=form.loai_phi.data.id, so_tien=form.so_tien.data, phuong_thuc=form.phuong_thuc.data, trang_thai='Đã xác nhận')
        db.session.add(new_gd)
        db.session.commit()
        flash('Thêm giao dịch thành công', 'success')
        return redirect(url_for('admin.index'))
    return render_template('admin/create_form.html', form=form, title='Thêm Giao dịch')

@crud.route('/giaodich/delete/<int:id>', methods=['GET'])
def delete_giaodich(id):
    db.session.delete(GiaoDich.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('admin.index'))

@crud.route('/tamtru/delete/<int:id>', methods=['GET'])
def delete_tamtru(id):
    tt = TamTru.query.get_or_404(id)
    nk = NhanKhau.query.get(tt.resident_id)
    if nk: nk.tinh_trang = 'Bình thường'
    db.session.delete(tt)
    db.session.commit()
    return redirect(url_for('admin.index'))

# [CẬP NHẬT] Gửi thông báo cho TẤT CẢ CƯ DÂN
@crud.route('/thongbao/add', methods=['GET', 'POST'])
def add_thongbao():
    form = ThongBaoForm()
    if form.validate_on_submit():
        if form.loai_thong_bao.data == 'Thông tin':
            all_residents = TaiKhoan.query.filter_by(role='resident').all()
            if not all_residents:
                flash("Không tìm thấy cư dân nào để gửi!", "warning")
                return redirect(url_for('admin.index'))
            
            count = 0
            for res in all_residents:
                db.session.add(ThongBao(
                    nguoi_nhan_id=res.id,
                    noi_dung=form.noi_dung.data,
                    loai_thong_bao='Hệ thống'
                ))
                count += 1
            
            db.session.commit()
            flash(f"Đã gửi thông báo cho {count} cư dân.", "success")
            return redirect(url_for('admin.index'))
        else:
            flash("Chức năng gửi Hóa đơn hàng loạt nên dùng 'Ghi Điện Nước'.", "info")
            return redirect(url_for('crud.record_indices'))

    return render_template('admin/create_form.html', form=form, title='Gửi Thông Báo Chung')

# Trang duyệt yêu cầu
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
    return redirect(url_for('crud.list_requests'))