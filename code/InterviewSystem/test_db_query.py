import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.DataBase_connect.database import get_db
from app.services.DataBase_connect import models

def test_db_query():
    db = next(get_db())
    
    # 测试查询所有报告
    print("=== 查询所有报告 ===")
    all_reports = db.query(models.Rpg).all()
    print(f"总共找到 {len(all_reports)} 条报告记录")
    
    # 测试查询特定用户
    print("\n=== 查询 testuser001 的报告 ===")
    account_id = "testuser001"
    reports = db.query(models.Rpg).filter(models.Rpg.accountID == account_id).all()
    print(f"为 accountID='{account_id}' 找到 {len(reports)} 条报告")
    
    # 打印找到的报告详情
    for i, report in enumerate(reports):
        print(f"\n报告 {i+1}:")
        print(f"  ID: {report.ID}")
        print(f"  accountID: {report.accountID}")
        print(f"  datetime: {report.datetime}")
        print(f"  job: {report.job}")
    
    # 测试用户表
    print("\n=== 查询用户表 ===")
    users = db.query(models.User).all()
    print(f"总共找到 {len(users)} 个用户")
    for user in users:
        print(f"  accountID: {user.accountID}, nickName: {user.nickName}")
    
    # 检查外键关系
    print("\n=== 检查外键约束 ===")
    user_reports = db.query(models.User).filter(models.User.accountID == account_id).first()
    if user_reports:
        print(f"用户 {account_id} 的报告数量: {len(user_reports.reports)}")
    
    db.close()

if __name__ == "__main__":
    try:
        test_db_query()
    except Exception as e:
        print(f"查询失败: {e}")
        import traceback
        traceback.print_exc()