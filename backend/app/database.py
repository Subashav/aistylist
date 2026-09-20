from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)
    try:
        with engine.connect() as conn:
            insp = inspect(engine)
            if "saved_results" in insp.get_table_names():
                cols = [c["name"] for c in insp.get_columns("saved_results")]
                if "personalized_analysis" not in cols:
                    conn.execute(text("ALTER TABLE saved_results ADD COLUMN personalized_analysis TEXT"))
                    conn.commit()
    except Exception:
        pass

init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
