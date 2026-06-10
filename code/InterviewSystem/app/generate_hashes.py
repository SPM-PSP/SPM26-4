import sys
import os

    # 确保能够导入 utils 模块
    # 将项目根目录添加到 Python 路径，以便导入 interview 包
    # 假设 generate_hashes.py 和 interview 文件夹在同一级
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.services.OrdServices.security import hash_password
# 您希望为测试用户设置的明文密码
test_passwords = {
        "user001": "password123", # 示例明文密码
        "user002": "securepass",
        "user003": "mysecret",
        "company001": "comp1pass",
        "company002": "comp2pass"
}

print("--- 生成的真实哈希密码 ---")
for account, plain_pass in test_passwords.items():
    hashed_pass = hash_password(plain_pass)
    print(f"'{account}' 的明文密码 '{plain_pass}' 对应的哈希值是:")
    print(f"'{hashed_pass}'")
    print("-" * 30)

    