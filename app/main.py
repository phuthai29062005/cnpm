from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from .models import NhanKhau, HoKhau, ThongBao, NhanKhauHoKhau, GiaoDich, db, BienLai, LoaiPhi, TaiKhoan, YeuCau
from .forms import ChangePasswordForm, YeuCauForm
from datetime import datetime
import uuid

main = Blueprint("main", __name__)

@main.route("/")
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin.index'))
    
    elif current_user.role == 'resident':
        nhan_khau = NhanKhau.query.get(current_user.nhan_khau_id)
        ho_khau = None
        thanh_vien_links = [] 
        hoa_don_list = [] 
        
        if nhan_khau and nhan_khau.id_ho_khau:
            ho_khau = HoKhau.query.get(nhan_khau.id_ho_khau)
            if ho_khau:
                thanh_vien_links = NhanKhauHoKhau.query.filter_by(ho_khau_id=ho_khau.id).all()
                hoa_don_list = GiaoDich.query.filter_by(ho_khau_id=ho_khau.id, trang_thai='Đang chờ').all()

        thong_bao_list = ThongBao.query.filter_by(nguoi_nhan_id=current_user.id).order_by(ThongBao.ngay_tao.desc()).all()
        
        return render_template('resident_dashboard.html',
                               user=nhan_khau,
                               hokhau=ho_khau,
                               thanh_vien=thanh_vien_links, 
                               thong_bao_list=thong_bao_list,
                               hoa_don_list=hoa_don_list
                               )
    else:
        return "Unknown Role"

# [CẬP NHẬT] Trang xem Biên lai
@main.route("/receipts")
@login_required
def receipts():
    if current_user.role != 'resident':
        abort(403)
        
    nhan_khau = NhanKhau.query.get(current_user.nhan_khau_id)
    if not nhan_khau or not nhan_khau.id_ho_khau:
        flash("Bạn chưa thuộc hộ khẩu nào để xem biên lai.", "warning")
        return redirect(url_for('main.dashboard'))
    
    # 1. Lấy danh sách giao dịch đã trả tiền
    paid_transactions = GiaoDich.query.filter(
        GiaoDich.ho_khau_id == nhan_khau.id_ho_khau,
        GiaoDich.bien_lai_id != None
    ).order_by(GiaoDich.ngay_nop.desc()).all()
    
    # 2. Lấy danh sách biên lai
    all_receipts = [gd.bien_lai for gd in paid_transactions if gd.bien_lai]
    
    # 3. [MỚI] Tính toán các số liệu thống kê
    total_paid = 0
    if all_receipts:
        # Dùng decimal=True để đảm bảo tính toán chính xác với kiểu Numeric/Decimal
        total_paid = sum(r.tong_tien for r in all_receipts if r.tong_tien)
    
    count = len(all_receipts)
    average_receipt = (total_paid / count) if count > 0 else 0
    
    latest_receipt_date = "Chưa có"
    if all_receipts:
        latest_receipt_date = all_receipts[0].ngay_thanh_toan.strftime('%d/%m/%Y')

    # 4. Gửi dữ liệu ra template
    return render_template('receipts.html', 
                           receipts=all_receipts,
                           total_paid=total_paid,
                           average_receipt=average_receipt,
                           latest_receipt_date=latest_receipt_date
                           )

# Trang gửi Yêu cầu
@main.route("/request/send", methods=["GET", "POST"])
@login_required
def send_request():
    if current_user.role != 'resident':
        return redirect(url_for('main.dashboard'))
        
    form = YeuCauForm()
    if form.validate_on_submit():
        new_req = YeuCau(
            nguoi_gui_id=current_user.id,
            loai_yeu_cau=form.loai_yeu_cau.data,
            noi_dung=form.noi_dung.data
        )
        db.session.add(new_req)
        db.session.commit()
        flash("Đã gửi yêu cầu thành công!", "success")
        return redirect(url_for('main.dashboard'))
        
    return render_template('resident_request.html', form=form)

# Trang thanh toán Online
@main.route("/pay/online/<int:bill_id>", methods=["GET"])
@login_required
def pay_online(bill_id):
    bill = GiaoDich.query.get_or_404(bill_id)
    me = NhanKhau.query.get(current_user.nhan_khau_id)
    
    if not me or bill.ho_khau_id != me.id_ho_khau:
        abort(403) 

    if bill.trang_thai == 'Đã thanh toán':
        flash("Hóa đơn này đã được thanh toán.", "info")
        return redirect(url_for('main.dashboard'))

    try:
        bill.trang_thai = 'Đã thanh toán'
        bill.ngay_nop = datetime.now()
        bill.phuong_thuc = 'Online Banking'
        
        rec = BienLai(
            ma_bien_lai=f"BL-ONLINE-{uuid.uuid4().hex[:6].upper()}",
            nguoi_thanh_toan=current_user.ho_ten,
            ho_khau_info=bill.ho_khau.ma_so_ho_khau,
            tong_tien=bill.so_tien,
            chi_tiet=f"Thanh toán Online: {bill.loai_phi.ten_phi}"
        )
        db.session.add(rec)
        db.session.flush()
        bill.bien_lai_id = rec.id
        
        nk_ids = [nk.id for nk in NhanKhau.query.filter_by(id_ho_khau=bill.ho_khau_id).all()]
        if nk_ids:
            acc_ids = [tk.id for tk in TaiKhoan.query.filter(TaiKhoan.nhan_khau_id.in_(nk_ids)).all()]
            if acc_ids:
                ThongBao.query.filter(
                    ThongBao.nguoi_nhan_id.in_(acc_ids),
                    ThongBao.loai_thong_bao == 'Hóa đơn'
                ).delete(synchronize_session=False)
        
        db.session.commit()
        flash(f"Thanh toán thành công!", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Lỗi giao dịch: {str(e)}", "danger")

    return redirect(url_for('main.dashboard'))

@main.route("/notification/delete/<int:id>")
@login_required
def delete_notification(id):
    # Chỉ cho phép resident thực hiện
    if current_user.role != 'resident':
        abort(403)
        
    # Tìm thông báo theo ID
    noti = ThongBao.query.get_or_404(id)
    
    # Bảo mật: Kiểm tra xem thông báo này có đúng là của người đang đăng nhập không
    if noti.nguoi_nhan_id != current_user.id:
        flash("Bạn không có quyền xóa thông báo này.", "danger")
        return redirect(url_for('main.dashboard'))
        
    try:
        db.session.delete(noti)
        db.session.commit()
        flash("Đã xóa thông báo.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Lỗi khi xóa: {str(e)}", "danger")
        
    return redirect(url_for('main.dashboard'))