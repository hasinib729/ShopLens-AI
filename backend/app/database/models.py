import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from app.database.db import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")  # "user" or "admin"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    brand = Column(String, index=True, nullable=True)
    category = Column(String, index=True, nullable=True)
    price = Column(Float, index=True, nullable=False)
    image_url = Column(String, nullable=True)
    rating = Column(Float, default=0.0)
    reviews_count = Column(Integer, default=0)
    features = Column(JSON, nullable=True)  # dict for color, size, specification metadata
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    device = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

class UserActivity(Base):
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    event_type = Column(String, nullable=False)  # "view", "click", "cart", "purchase"
    dwell_time = Column(Integer, default=0)  # dwell time in seconds (for views)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class SearchSession(Base):
    __tablename__ = "search_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    query_count = Column(Integer, default=0)
    avg_latency = Column(Float, default=0.0)
    click_count = Column(Integer, default=0)
    conversion = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class SearchLog(Base):
    __tablename__ = "search_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    query_text = Column(String, nullable=True)
    image_path = Column(String, nullable=True)
    search_type = Column(String, nullable=False)  # "text", "image", "hybrid"
    parsed_category = Column(String, nullable=True)
    parsed_color = Column(String, nullable=True)
    parsed_brand = Column(String, nullable=True)
    parsed_price_max = Column(Float, nullable=True)
    latency_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class SearchMetric(Base):
    __tablename__ = "search_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    recall_at_10 = Column(Float, default=0.0)
    precision_at_10 = Column(Float, default=0.0)
    ndcg_at_10 = Column(Float, default=0.0)
    mrr = Column(Float, default=0.0)
    query_coverage = Column(Float, default=0.0)
    zero_result_rate = Column(Float, default=0.0)
    logged_date = Column(DateTime, default=datetime.datetime.utcnow)

class RecMetric(Base):
    __tablename__ = "rec_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    map = Column(Float, default=0.0)
    hit_rate = Column(Float, default=0.0)
    ctr = Column(Float, default=0.0)
    logged_date = Column(DateTime, default=datetime.datetime.utcnow)

class ABExperiment(Base):
    __tablename__ = "ab_experiments"
    
    id = Column(Integer, primary_key=True, index=True)
    experiment_name = Column(String, unique=True, index=True, nullable=False)
    model_a_name = Column(String, nullable=False)
    model_b_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ABExperimentLog(Base):
    __tablename__ = "ab_experiment_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    experiment_name = Column(String, index=True, nullable=False)
    session_id = Column(String, index=True, nullable=False)
    group_name = Column(String, nullable=False)  # "A" or "B"
    query_text = Column(String, nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    is_clicked = Column(Boolean, default=False)
    is_purchased = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
