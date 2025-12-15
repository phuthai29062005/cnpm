import pandas as pd
import random

# Tạo dữ liệu mẫu cho 10 hộ đầu tiên (HK-DK-001 đến HK-DK-010)
# Lưu ý: Trong seed_data, chỉ số điện cũ random(100, 600), nước random(10, 50).
# Để đảm bảo tính ra tiền, ta set chỉ số mới cao hơn hẳn.

data = []
for i in range(1, 101):
    ma_hk = f"HK-DK-{i:03d}" # VD: HK-DK-001
    
    # Chỉ số mới (đảm bảo > cũ)
    dien_moi = random.randint(700, 800) 
    nuoc_moi = random.randint(60, 80)
    
    data.append({
        "ma_ho_khau": ma_hk,
        "chi_so_dien_moi": dien_moi,
        "chi_so_nuoc_moi": nuoc_moi
    })

# Tạo DataFrame
df = pd.DataFrame(data)

# Xuất ra file Excel
file_name = "mau_dien_nuoc.xlsx"
df.to_excel(file_name, index=False)

print(f"✅ Đã tạo file '{file_name}' thành công!")
print("Nội dung file mẫu:")
print(df)