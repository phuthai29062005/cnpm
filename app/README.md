Hướng dẫn Cài đặt & Chạy Ứng dụng Quản lý Dân cư (Flask)

Đây là dự án Web Quản lý Dân cư, Hộ khẩu và Thu phí, được xây dựng bằng Flask và Microsoft SQL Server.

1. Yêu cầu Môi trường

Trước khi bắt đầu, bạn cần cài đặt:

Python (Khuyến nghị 3.10 trở lên)

Microsoft SQL Server (Bản Express, Developer, hoặc Standard) và SQL Server Management Studio (SSMS).

ODBC Driver 18 for SQL Server: Đây là driver bắt buộc để Python kết nối với SQL Server. Bạn có thể tải tại trang chủ của Microsoft.

2. Hướng dẫn Cài đặt

Bước 1: Tải Code và Cài đặt Môi trường

Tải toàn bộ code này về máy của bạn.

Mở Terminal (hoặc Command Prompt) và trỏ đến thư mục gốc của dự án.

Tạo một môi trường ảo (virtual environment) để tránh xung đột thư viện:

python -m venv venv


Kích hoạt môi trường ảo:

Windows: venv\Scripts\activate

macOS/Linux: source venv/bin/activate

Bước 2: Cài đặt Thư viện

Đảm bảo bạn đã ở trong môi trường ảo (Thấy (venv) ở đầu dòng Terminal).

Cài đặt tất cả các thư viện cần thiết bằng file requirements.txt:

pip install -r requirements.txt


Bước 3: Cấu hình Database (Quan trọng)

Ứng dụng này sẽ KHÔNG TỰ TẠO database. Bạn phải tạo nó thủ công.

Mở SSMS (SQL Server Management Studio) và đăng nhập vào Server của bạn.

Nhấn chuột phải vào "Databases" -> "New Database...".

Đặt tên cho database là project1 (hoặc tên khác nếu muốn). Nhấn OK.

Mở file config.py trong thư mục code.

Cập nhật lại class Config với thông tin SQL Server của bạn (SERVER, USERNAME, PASSWORD, và DATABASE nếu bạn đặt tên khác project1).

class Config:
    SECRET_KEY = "key-cua-ban"

    DRIVER = "ODBC Driver 18 for SQL Server"
    SERVER = "TEN-SERVER-CUA-BAN"  # VD: 127.0.0.1,1433 hoặc MY-PC\SQLEXPRESS
    DATABASE = "project1"
    USERNAME = "sa"               # Tên đăng nhập SQL của bạn
    PASSWORD = "MatKhauCuaBan"    # Mật khẩu SQL của bạn

    # (Các dòng khác giữ nguyên)


Bước 4: Khởi tạo Bảng và Nạp Dữ liệu (CLEAN INSTALL)

Đây là bước quan trọng nhất để khởi chạy ứng dụng sạch. Hãy chạy 3 lệnh này theo đúng thứ tự trong Terminal:

(Tùy chọn) Nếu bạn chưa có thư mục migrations, chạy lệnh sau (Chỉ chạy 1 lần duy nhất):

flask db init


Tạo file Migration: Lệnh này sẽ quét các Model và tạo file kịch bản nâng cấp.

flask db migrate -m "Khoi tao database"


Nâng cấp Database: Lệnh này sẽ đọc file kịch bản và tạo tất cả các bảng (NhanKhau, HoKhau, BienLai, YeuCau...) vào database project1 của bạn.

flask db upgrade


Nạp Dữ liệu Mẫu: Lệnh này sẽ dọn sạch và nạp dữ liệu mẫu (Admin, 3 hộ khẩu, giá tiền điện nước).

flask seed-data


Bước 5: Chạy Ứng dụng

Nếu tất cả các bước trên thành công, chạy lệnh sau:

flask run


Mở trình duyệt và truy cập: http://127.0.0.1:5000

3. Tài khoản Đăng nhập

Sau khi chạy flask seed-data, hệ thống sẽ có các tài khoản sau:

Admin

Username: admin

Password: 123456

Cư dân (Mật khẩu: 1)

Hộ 1: 001080001234 (Nguyễn Văn Hùng)

Hộ 1: 001182004567 (Trần Thị Lan)

Hộ 2: 001075007890 (Lê Minh Bình)

Hộ 2: 001177001122 (Phạm Thị Mai)

Hộ 3: 001095003344 (Hoàng Trung Dũng)