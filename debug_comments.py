"""
调试评论数据
"""
import sys
sys.path.insert(0, 'e:\\YOYO\\backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import DiaryComment, User, TravelDiary

DB_PATH = 'e:\\YOYO\\backend\\data\\travel.db'
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def debug_data():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("数据库调试")
        print("=" * 60)
        
        # 1. 所有日记
        print("\n1. 所有日记:")
        diaries = db.query(TravelDiary).all()
        for d in diaries:
            print("   ID:{} 标题:{}".format(d.id, d.title[:40]))
        
        # 2. 所有评论
        print("\n2. 所有评论:")
        comments = db.query(DiaryComment).all()
        for c in comments:
            print("   ID:{} diary_id:{} user_id:{} 内容:{}".format(
                c.id, c.diary_id, c.user_id, c.content[:40]))
        
        # 3. 所有用户
        print("\n3. 所有用户:")
        users = db.query(User).all()
        for u in users:
            print("   ID:{} 用户名:{}".format(u.id, u.username))
        
        # 4. 按日记ID统计评论
        print("\n4. 各日记的评论数:")
        for d in diaries:
            count = db.query(DiaryComment).filter(DiaryComment.diary_id == d.id).count()
            print("   日记ID {}: {} 条评论".format(d.id, count))
        
        # 5. 测试 diary_id=5 的具体查询
        print("\n5. 日记ID=5 的评论 (OUTER JOIN):")
        result = db.query(DiaryComment, User.username).outerjoin(
            User, DiaryComment.user_id == User.id
        ).filter(DiaryComment.diary_id == 5).all()
        print("   找到 {} 条".format(len(result)))
        for c, u in result:
            print("   - ID:{} user_id:{} 用户名:{} 内容:{}".format(
                c.id, c.user_id, u, c.content[:30]))
        
    finally:
        db.close()

if __name__ == '__main__':
    debug_data()
