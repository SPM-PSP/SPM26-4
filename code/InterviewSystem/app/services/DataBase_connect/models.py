"""
数据库模型定义模块

该模块定义了系统中所有实体的数据模型，使用SQLAlchemy ORM框架实现。
包含用户、企业、面试题目、视频、报告和岗位指标配置等核心业务实体，
并定义了它们之间的关系和约束。

主要功能：
- 用户和企业账户管理
- 面试题库管理（大数据、物联网、人工智能等领域）
- 面试视频和报告的存储与关联
- 岗位评价指标配置

表结构说明：
- users：存储用户基本信息和状态
- company：存储企业用户信息
- bigdata、internetofthings、ai：不同领域的面试题库
- video：存储用户面试视频信息
- rpg：存储面试报告数据
- vocation_signs：配置岗位评价核心指标

使用说明：
- 所有模型类继承自Base类
- 字段使用Column定义，包含类型、约束和注释
- 表间关系使用relationship定义
- 支持MySQL数据库特性（如注释、唯一约束）
"""

from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, UniqueConstraint, Text, \
    Boolean  # 导入 Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.services.DataBase_connect.database import Base


class User(Base):
    """
    用户表模型，存储系统用户的基本信息和状态。
    继承自Base类，映射到数据库中的"users"表。
    """
    __tablename__ = "users"

    accountID = Column(String(25), primary_key=True, comment='User account ID, unique identifier')
    password = Column(String(255), nullable=False, comment='Account password (will store hashed password)')
    nickName = Column(String(50), nullable=False, comment='User nickname')
    schoolName = Column(String(50), nullable=False, comment='School name')
    major = Column(String(50), nullable=False, comment='Major name')
    qualification = Column(Enum('高职', '本科', '研究生', '博士'), nullable=False, comment='Educational qualification')
    grade = Column(String(15), nullable=False, comment='Grade (e.g., 本科二年级)')
    birthday = Column(DateTime, comment='Birthday')
    avatar = Column(Boolean, default=False, nullable=False, comment='用户是否已上传头像')  # Added boolean field
    resume = Column(Boolean, default=False, nullable=False, comment='用户是否已上传简历')  # Added boolean field
    createTime = Column(DateTime, default=func.now(), comment='Account creation time')

    videos = relationship("Video", back_populates="user")
    reports = relationship("Rpg", back_populates="user")

    # 自定义打印格式，方便调试时查看用户基本信息
    def __repr__(self):
        return f"<User(accountID='{self.accountID}', nickName='{self.nickName}')>"


class Company(Base):
    """
    企业表模型，存储企业用户的注册信息和基本资料。
    继承自Base类，映射到数据库中的"company"表。
    """
    __tablename__ = "company"

    ID = Column(Integer, primary_key=True, index=True, autoincrement=True,
                comment='Auto-incrementing ID, no practical meaning')
    companyName = Column(String(50), nullable=False, comment='Company name')
    accountID = Column(String(25), nullable=False, comment='Company account ID')
    password = Column(String(255), nullable=False, comment='Account password (will store hashed password)')
    caption = Column(String(255), comment='Detailed company remarks')
    position = Column(String(255), nullable=False, comment='Company address')
    category = Column(String(255), nullable=False, comment='Company type (e.g.,新能源公司, 互联网企业)')
    introduction = Column(String(255), comment='Company introduction')
    avatar = Column(String(255), comment='Company avatar URL')
    detail = Column(String(255), comment='Company detailed introduction file URL')
    createTime = Column(DateTime, default=func.now(), comment='Account creation time')
    # 表级约束：企业名称和备注组合唯一
    __table_args__ = (
        UniqueConstraint('companyName', 'caption', name='UQ_Company_Name_Caption'),
        {'mysql_comment': 'Company table'}
    )

    def __repr__(self):
        return f"<Company(companyName='{self.companyName}', accountID='{self.accountID}')>"


class BigDataDEQuestion(Base):
    __tablename__ = "bigdata"
    ID = Column(Integer, primary_key=True, index=True, autoincrement=True,
                comment='Auto-incrementing ID, no practical meaning')
    degree = Column(Enum('简单', '中等', '困难'), nullable=False, comment='Question difficulty level')
    question = Column(String(255), nullable=False, comment='Question description')
    answer = Column(String(255), nullable=False, comment='Simple reference answer for the question')

    def __repr__(self):
        return f"<BigDataDEQuestion(ID={self.ID}, degree='{self.degree}')>"


class IoTSAAQuestion(Base):
    """
    人工智能岗位面试题模型，存储人工智能领域的面试题目及答案。
    继承自Base类，映射到数据库中的"ai"表。
    """
    __tablename__ = "internetofthings"

    ID = Column(Integer, primary_key=True, index=True, autoincrement=True,
                comment='Auto-incrementing ID, no practical meaning')
    degree = Column(Enum('简单', '中等', '困难'), nullable=False, comment='Question difficulty level')
    question = Column(String(255), nullable=False, comment='Question description')
    answer = Column(String(255), nullable=False, comment='Simple reference answer for the question')

    def __repr__(self):
        return f"<IoTSAAQuestion(ID={self.ID}, degree='{self.degree}')>"


class AIMSEQuestion(Base):
    __tablename__ = "ai"

    ID = Column(Integer, primary_key=True, index=True, autoincrement=True,
                comment='Auto-incrementing ID, no practical meaning')
    degree = Column(Enum('简单', '中等', '困难'), nullable=False, comment='Question difficulty level')
    question = Column(String(255), nullable=False, comment='Question description')
    answer = Column(String(255), nullable=False, comment='Simple reference answer for the question')

    def __repr__(self):
        return f"<AIMSEQuestion(ID={self.ID}, degree='{self.degree}')>"


class Video(Base):
    __tablename__ = "video"

    ID = Column(Integer, primary_key=True, index=True, autoincrement=True, comment='Auto-incrementing ID')
    accountID = Column(String(25), ForeignKey('users.accountID', ondelete='CASCADE'), nullable=False,
                       comment='User account ID')
    datetime = Column(DateTime, default=func.now(), comment='Video save time')
    video = Column(String(255), nullable=False, comment='Video storage path (e.g., accountID/videoID.ext)')

    user = relationship("User", back_populates="videos")
    reports = relationship("Rpg", back_populates="video")

    def __repr__(self):
        return f"<Video(ID={self.ID}, accountID='{self.accountID}')>"


class Rpg(Base):
    """
    视频表模型，存储用户面试视频的基本信息和存储路径。
    继承自Base类，映射到数据库中的"video"表。
    """
    __tablename__ = "rpg"

    ID = Column(Integer, primary_key=True, index=True, autoincrement=True, comment='Auto-incrementing ID')
    accountID = Column(String(25), ForeignKey('users.accountID', ondelete='CASCADE'), nullable=False,
                       comment='User account ID')
    datetime = Column(DateTime, default=func.now(), comment='Report creation and storage time')
    rpg = Column(Text, nullable=False, comment='Report data (JSON content)')
    job = Column(String(255), comment='Job role corresponding to the interview report')
    videoID = Column(Integer, ForeignKey('video.ID', ondelete='SET NULL'), comment='Associated video ID')

    user = relationship("User", back_populates="reports")
    video = relationship("Video", back_populates="reports")

    def __repr__(self):
        return f"<Rpg(ID={self.ID}, accountID='{self.accountID}')>"


class VocationSign(Base):
    """
    面试报告表模型，存储用户面试报告的详细数据。
    继承自Base类，映射到数据库中的"rpg"表。
    """
    __tablename__ = "vocation_signs"

    ID = Column(Integer, primary_key=True, index=True, autoincrement=True, comment='Auto-incrementing ID')
    domain = Column(String(20), nullable=False, comment='Interview positions that can be concurrently considered')
    vocation = Column(String(20), nullable=False, comment='Interview profession')
    sign1 = Column(String(15), comment='Core metric one')
    sign2 = Column(String(15), comment='Core metric two')
    sign3 = Column(String(15), comment='Core metric three')
    sign4 = Column(String(15), comment='Core metric four')
    sign5 = Column(String(15), comment='Core metric five')
    sign6 = Column(String(15), comment='Core metric six')

    __table_args__ = (
        UniqueConstraint('domain', 'vocation', name='UQ_Domain_Vocation'),
        {'mysql_comment': 'Interview position and core metrics configuration table'}
    )

    def __repr__(self):
        return f"<VocationSign(ID={self.ID}, domain='{self.domain}', vocation='{self.vocation}')>"

