
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    category = Column(String, default="General")
    status = Column(String, default="Pending")
    time_spent = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"

    def start_timer(self) -> None:
        if self.started_at is None:
            self.started_at = datetime.now(timezone.utc)
            self.status = "In Progress"

    def stop_timer(self) -> None:
        print(f"[Task.stop_timer] Before: started_at={self.started_at}")
        if self.started_at is not None:
            # Ensure started_at is timezone-aware before subtraction
            if self.started_at.tzinfo is None:
                started_at_aware = self.started_at.replace(tzinfo=timezone.utc)
            else:
                started_at_aware = self.started_at

            elapsed = datetime.now(timezone.utc) - started_at_aware
            self.time_spent += int(elapsed.total_seconds())
            self.started_at = None
            self.status = "Completed"
        print(f"[Task.stop_timer] After: started_at={self.started_at}")

    def reset_timer(self) -> None:
        self.time_spent = 0
        self.started_at = None
        self.status = "Pending"

    def get_current_session_time(self) -> int:
        if self.started_at is not None:
            # Ensure started_at is timezone-aware before subtraction
            if self.started_at.tzinfo is None:
                started_at_aware = self.started_at.replace(tzinfo=timezone.utc)
            else:
                started_at_aware = self.started_at

            elapsed = datetime.now(timezone.utc) - started_at_aware
            return int(elapsed.total_seconds())
        return 0

    def get_total_time_seconds(self) -> int:
        total = self.time_spent
        if self.started_at is not None:
            total += self.get_current_session_time()
        return total

    def total_time_str(self) -> str:
        total_seconds = self.get_total_time_seconds()
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @property
    def time_spent_human(self) -> str:
        return self.total_time_str()

    @property
    def is_running(self) -> bool:
        return self.started_at is not None
