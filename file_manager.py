import os
import sys
import json
import shutil
from colorama import init, Fore

init(autoreset=True)  # Initialize colorama

CONFIG_FILE = "config.json"

def load_config():
    """بارگیری تنظیمات از فایل پیکربندی | Load configuration from file"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "default_directory": os.getcwd(),
        "mobile_storage_paths": {
            "internal": "/storage/emulated/0",
            "external": "/storage"
        },
        "remember_path": True,
        "excluded_dirs": ["/proc", "/sys"]
    }

def save_config(config):
    """ذخیره تنظیمات در فایل | Save configuration to file"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def detect_platform():
    """تشخیص پلتفرم و مسیرهای ذخیره‌سازی | Detect OS platform and storage paths"""
    platform = sys.platform.lower()
    config = load_config()
    
    if os.path.exists("/data/data/com.termux/files/home"):
        # Android (Termux) environment
        config["is_mobile"] = True
        if not os.path.exists(config["mobile_storage_paths"]["internal"]):
            config["mobile_storage_paths"]["internal"] = os.getenv("EXTERNAL_STORAGE", "/sdcard")
    else:
        # Desktop environment
        config["is_mobile"] = False
        config["desktop_paths"] = {
            "documents": os.path.expanduser("~/Documents"),
            "downloads": os.path.expanduser("~/Downloads")
        }
    
    save_config(config)
    return config

def validate_path(path):
    """اعتبارسنجی مسیر و تصحیح خودکار | Validate and normalize path"""
    try:
        path = os.path.normpath(path)
        if not os.path.exists(path):
            raise FileNotFoundError
        if not os.access(path, os.R_OK):
            raise PermissionError
        return path
    except Exception as e:
        print(Fore.RED + f"خطای مسیر: {e}")
        return None

def search_files(directory, keyword, excluded_dirs):
    """جستجوی فایل با فیلتر پوشه‌های حذف شده | Search files with excluded dirs filter"""
    matches = []
    try:
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if os.path.join(root, d) not in excluded_dirs]
            for file in files:
                if keyword.lower() in file.lower():
                    full_path = os.path.join(root, file)
                    matches.append((full_path, os.path.getsize(full_path)))
    except Exception as e:
        print(Fore.RED + f"خطای جستجو: {e}")
    return matches

def format_size(size):
    """تبدیل حجم به فرمت خوانا | Convert size to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"

def file_operations(results, operation_type):
    """انجام عملیات روی فایل‌ها | Perform file operations"""
    if operation_type == "delete":
        for file in results:
            os.remove(file)
    elif operation_type == "copy":
        dest = input("مسیر مقصد: ")
        for file in results:
            shutil.copy2(file, dest)

def main():
    """تابع اصلی برنامه | Main application function"""
    config = detect_platform()
    print(Fore.GREEN + "FileFinder Pro - مدیریت فایل هوشمند")
    
    while True:
        directory = input("\nمسیر جستجو (یا exit برای خروج): ")
        if directory.lower() == 'exit':
            break
        
        validated_path = validate_path(directory)
        if not validated_path:
            continue
            
        keyword = input("کلمه کلیدی: ")
        results = search_files(validated_path, keyword, config["excluded_dirs"])
        
        if results:
            for i, (file, size) in enumerate(results, 1):
                print(f"{i}. {file} ({format_size(size)})")
            
            choice = input("\nعملیات (delete/copy/exit): ")
            if choice in ["delete", "copy"]:
                file_operations([f for f, _ in results], choice)

if __name__ == "__main__":
    main(
