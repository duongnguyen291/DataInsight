import os

def print_folder_structure(folder_path, indent_level=0, exclude_folders=None):
    if exclude_folders is None:
        exclude_folders = []  # Khởi tạo danh sách folder cần loại trừ nếu không có

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        
        # Kiểm tra nếu item là folder và có trong danh sách loại trừ thì bỏ qua
        if os.path.isdir(item_path) and item in exclude_folders:
            continue

        # In tên file hoặc folder với mức thụt lề phù hợp
        print("    " * indent_level + "|-- " + item)
        
        # Nếu là folder và không bị loại trừ, đệ quy vào folder con
        if os.path.isdir(item_path):
            print_folder_structure(item_path, indent_level + 1, exclude_folders)

# Sử dụng hàm với đường dẫn folder và danh sách các folder cần loại trừ
folder_path = r"D:\github\DataInsight"
exclude_folders = ["black-dashboard",".git"]  # Thêm các folder bạn muốn bỏ qua
print_folder_structure(folder_path, exclude_folders=exclude_folders)
