----6. Trigger cap nhat tu dong
--Nhan_khau ho khau
-- Khi thêm 1 người vào hộ mới, tự động cập nhật id_ho_khau
USE project1;
GO

CREATE TRIGGER trg_UpdateNhanKhauHoKhau
ON nhan_khau_ho_khau
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Cập nhật id_ho_khau trong Nhan_khau bằng ho_khau_id vừa thêm
    UPDATE nk
    SET nk.id_ho_khau = i.ho_khau_id
    FROM Nhan_khau nk
    INNER JOIN inserted i
        ON nk.id = i.nhan_khau_id
    WHERE i.trang_thai = N'Bình thường';  -- chỉ update nếu đang cư trú
END;
GO

----Thu chi
CREATE TRIGGER trg_InsertThuChi_Advanced
ON Giao_dich
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    -- Chỉ lấy các giao dịch bắt buộc từ LoaiPhi
    INSERT INTO ThuChi(ho_khau_id, loai_giao_dich, so_tien, hinh_thuc, ngay_giao_dich, giao_dich_id)
    SELECT 
        gd.ho_khau_id,
        'Thu',
        gd.so_tien,
        gd.phuong_thuc,
        gd.ngay_nop,
        gd.id
    FROM inserted gd
    INNER JOIN LoaiPhi lp
        ON gd.loai_phi_id = lp.id
    WHERE lp.bat_buoc = 1
      AND gd.trang_thai = N'Đang chờ';

    -- Cập nhật trạng thái Giao_dich đã tạo ThuChi
    UPDATE gd
    SET gd.trang_thai = N'Đã xác nhận'
    FROM Giao_dich gd
    INNER JOIN inserted i
        ON gd.id = i.id
    INNER JOIN LoaiPhi lp
        ON i.loai_phi_id = lp.id
    WHERE lp.bat_buoc = 1
      AND gd.trang_thai = N'Đang chờ';
END;
GO
