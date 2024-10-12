import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from dotenv import load_dotenv

# 从 .env 文件加载环境变量
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 创建 SQLAlchemy 引擎
engine = create_engine(DATABASE_URL)

# 创建一个配置好的“Session”类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明性模型的基类
Base = declarative_base()

# 定义 Prompt 模型
class Prompt(Base):
    __tablename__ = "prompts"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    responses = relationship("Response", back_populates="prompt")

# 定义 Response 模型
class Response(Base):
    __tablename__ = "responses"
    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), index=True, nullable=False)
    content = Column(Text, nullable=False)
    model_version = Column(String, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    prompt = relationship("Prompt", back_populates="responses")
    feedback = relationship("Feedback", back_populates="response")

# 定义 Feedback 模型
class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("responses.id"), index=True, nullable=False)
    user_rating = Column(Integer, nullable=False)  # 例如，1-5 星级
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    response = relationship("Response", back_populates="feedback")

# 创建所有表
def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    print("数据库表创建成功。")

