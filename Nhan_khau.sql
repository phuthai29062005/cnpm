use project1;

---- 1. Nhan khau - Ho khau
CREATE TABLE Nhan_khau(
	id INT PRIMARY KEY IDENTITY(1,1),
	ho_ten NVARCHAR(100) NOT NULL,
	bi_danh NVARCHAR(50),
	ngay_sinh DATE NOT NULL CHECK (ngay_sinh <= CAST(GETDATE() AS DATE)),
	gioi_tinh NVARCHAR(3) CHECK (gioi_tinh IN (N'Nam', N'Nữ')) NOT NULL,
    nguyen_quan NVARCHAR(255),
    dan_toc NVARCHAR(50),
    nghe_nghiep NVARCHAR(100),
    noi_lam_viec NVARCHAR(100),
    so_cccd CHAR(12) UNIQUE,
    ngay_cap DATE ,
    noi_cap NVARCHAR(100),
    id_ho_khau INT,
    ngay_dang_ky_thuong_tru DATE CHECK(ngay_dang_ky_thuong_tru <= CAST(GETDATE() AS DATE)),
    noi_thuong_tru NVARCHAR(255) DEFAULT N'Mới sinh',
    tinh_trang NVARCHAR(20) CHECK (tinh_trang IN (N'Bình thường', N'Chuyển đi', N'Qua đời', N'Tạm trú', N'Tạm vắng')) DEFAULT N'Bình thường',
    ngay_cap_nhat DATETIME DEFAULT GETDATE()
);

CREATE TABLE Ho_khau(
	id INT PRIMARY KEY IDENTITY(1,1),
	ma_so_ho_khau NVARCHAR(20) UNIQUE NOT NULL,
	chu_ho_id INT,
	so_nha NVARCHAR(10) NOT NULL,
	duong_pho NVARCHAR(100) NOT NULL,
	phuong_xa NVARCHAR(100) NOT NULL,
	quan_huyen NVARCHAR(100) NOT NULL,
	ngay_tao DATE DEFAULT CAST(GETDATE() AS DATE),
	ghi_chu NVARCHAR(MAX),
	FOREIGN KEY (chu_ho_id) REFERENCES Nhan_khau(id)
	ON DELETE SET NULL
	ON UPDATE CASCADE

);

CREATE TABLE nhan_khau_ho_khau(
	id INT PRIMARY KEY IDENTITY(1,1),
	ho_khau_id INT NOT NULL,
	nhan_khau_id INT NOT NULL,
	quan_he_chu_ho NVARCHAR(50) NOT NULL,
	ngay_bat_dau DATE DEFAULT CAST(GETDATE() AS DATE),
	ngay_ket_thuc DATE DEFAULT NULL,
	trang_thai NVARCHAR(100) CHECK(trang_thai IN (N'Bình thường',N'Chuyển đi',N'Qua đời',N'Tạm trú',N'Tạm vắng'))  DEFAULT N'Bình thường',
	ghi_chu NVARCHAR(MAX),
	FOREIGN KEY (ho_khau_id) REFERENCES Ho_khau(id) ON DELETE CASCADE,
	FOREIGN KEY (nhan_khau_id) REFERENCES Nhan_Khau(id) ON DELETE CASCADE,
	CHECK (ngay_ket_thuc IS NULL OR ngay_ket_thuc >= ngay_bat_dau)
);
CREATE UNIQUE INDEX uniq_active_resident_per_household
ON nhan_khau_ho_khau(nhan_khau_id, trang_thai)
WHERE trang_thai = N'Đang cư trú';

----2. Khai bao tam tru tam vang
CREATE TABLE tam_tru(
	id INT PRIMARY KEY IDENTITY(1,1),
	resident_id INT NOT NULL,
	noi_tam_tru NVARCHAR(255) NOT NULL,
	ngay_bat_dau DATE NOT NULL,
	ngay_ket_thuc DATE,
	ly_do NVARCHAR(MAX),
	FOREIGN KEY (resident_id) REFERENCES Nhan_khau(id) ON DELETE CASCADE,
	CHECK(ngay_ket_thuc IS NULL OR ngay_ket_thuc >=ngay_bat_dau)
);

CREATE TABLE tam_vang(
	id INT PRIMARY KEY IDENTITY(1,1),
	resident_id INT NOT NULL,
	noi_den NVARCHAR(255) NOT NULL,
	ngay_bat_dau DATE NOT NULL,
	ngay_ket_thuc DATE,
	ly_do NVARCHAR(MAX),
	FOREIGN KEY (resident_id) REFERENCES Nhan_khau(id) ON DELETE CASCADE,
	CHECK(ngay_bat_dau IS NULL OR ngay_ket_thuc >= ngay_bat_dau)
);
-----3. Tai khoan
CREATE TABLE tai_khoan(
	id INT PRIMARY KEY IDENTITY(1,1),
	username NVARCHAR(20) NOT NULL UNIQUE,
	password_hash NVARCHAR(255) NOT NULL,
	ho_ten NVARCHAR(100) ,
    ngay_tao DATETIME DEFAULT GETDATE()
);

CREATE TABLE yeu_cau(
	id INT PRIMARY KEY IDENTITY(1,1),
	nguoi_gui_id INT NOT NULL,
	noi_dung NVARCHAR(MAX) NOT NULL,
	ngay_gui DATETIME DEFAULT GETDATE(),
	trang_thai NVARCHAR(100) CHECK(trang_thai IN (N'Chờ xử lý',N'Đã xử lý',N'Từ chối'))DEFAULT 'Chờ xử lý',
	FOREIGN KEY (nguoi_gui_id) REFERENCES tai_khoan(id)
       ON DELETE CASCADE
);

CREATE TABLE thong_bao(
	id INT PRIMARY KEY IDENTITY(1,1),
	nguoi_nhan_id INT NOT NULL,
	noi_dung NVARCHAR(MAX) NOT NULL,
	ngay_tao DATETIME DEFAULT GETDATE(),
	da_doc BIT DEFAULT 0,
	FOREIGN KEY (nguoi_nhan_id) REFERENCES tai_khoan(id) ON DELETE CASCADE
);
------4. Lich su ghi nhan
CREATE TABLE lich_su_nhan_khau(
	id INT PRIMARY KEY IDENTITY(1,1),
	id_duoc_thuc_hien INT NOT NULL,
	loai_chuyen NVARCHAR(100) NOT NULL CHECK(loai_chuyen IN(N'Thêm mới',N'Chuyển đi',N'Qua đời',N'Cập nhật thông tin',N'Tách hộ',N'Nhập hộ')),
	change_field NVARCHAR(100),
	cu NVARCHAR(255),
	moi NVARCHAR(255),
	ngay_th DATETIME DEFAULT GETDATE(),
	ng_thay_doi_id INT NOT NULL,
	ly_do NVARCHAR(MAX),
	FOREIGN KEY (id_duoc_thuc_hien) REFERENCES Nhan_khau(id) ON DELETE CASCADE, 
	FOREIGN KEY (ng_thay_doi_id) REFERENCES tai_khoan(id) ON DELETE NO ACTION
);

---5. Thu chi
CREATE TABLE LoaiPhi (
    id INT IDENTITY(1,1) PRIMARY KEY,
    ten_phi NVARCHAR(100) NOT NULL,
    bat_buoc BIT NOT NULL DEFAULT 1
);

CREATE TABLE Giao_dich (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nhan_khau_id INT NOT NULL,      -- ai nộp
    ho_khau_id INT NULL,            -- liên quan đến hộ
    loai_phi_id INT NOT NULL,       -- khóa ngoại đến LoaiPhi
    so_tien DECIMAL(12,2) NOT NULL CHECK (so_tien > 0),
    phuong_thuc NVARCHAR(50) NOT NULL,  -- Tiền mặt / Chuyển khoản / Ví điện tử
    ngay_nop DATETIME NOT NULL DEFAULT GETDATE(),
    trang_thai NVARCHAR(50) NOT NULL DEFAULT N'Đang chờ',

    -- khóa ngoại
    FOREIGN KEY (loai_phi_id) REFERENCES LoaiPhi(id) ON DELETE NO ACTION,
    FOREIGN KEY (nhan_khau_id) REFERENCES Nhan_khau(id) ON DELETE CASCADE,
    FOREIGN KEY (ho_khau_id) REFERENCES Ho_khau(id) ON DELETE NO ACTION
);


CREATE TABLE ThuChi (
    id INT IDENTITY(1,1) PRIMARY KEY,
    ho_khau_id INT NULL,               -- cho phép NULL nếu xóa hộ
    loai_giao_dich NVARCHAR(10) NOT NULL CHECK (loai_giao_dich IN ('Thu','Chi')),
    so_tien DECIMAL(15,2) NOT NULL CHECK (so_tien > 0),
    hinh_thuc NVARCHAR(50) NOT NULL DEFAULT N'Tiền mặt',
    ngay_giao_dich DATETIME NOT NULL DEFAULT GETDATE(),
    giao_dich_id INT NULL,             -- liên kết với Giao_dich nếu khoản thu từ người dân
    ghi_chu NVARCHAR(MAX) NULL,

    -- khóa ngoại
    FOREIGN KEY (ho_khau_id) REFERENCES Ho_khau(id) ON DELETE SET NULL,
    FOREIGN KEY (giao_dich_id) REFERENCES Giao_dich(id) ON DELETE SET NULL
);
