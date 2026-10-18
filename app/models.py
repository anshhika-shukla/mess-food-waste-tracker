from datetime import datetime, date
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    Text,
    Date,
    DateTime,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    func
)
from sqlalchemy.orm import relationship
from app.database import Base


class Student(Base):
    """Represents a registered college student eligible for mess dining."""
    __tablename__ = "students"

    student_id = Column(String(20), primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    hostel_block = Column(String(50), nullable=False)
    room_no = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    attendances = relationship("DailyMealAttendance", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student(id='{self.student_id}', name='{self.full_name}')>"


class MealMenu(Base):
    """Represents the scheduled mess menu for a given date and meal session."""
    __tablename__ = "meal_menus"

    menu_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    meal_date = Column(Date, nullable=False, index=True)
    meal_session = Column(String(20), nullable=False)
    menu_items = Column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint("meal_date", "meal_session", name="uq_meal_date_session"),
        CheckConstraint(
            "meal_session IN ('Breakfast', 'Lunch', 'Snacks', 'Dinner')",
            name="chk_valid_meal_session"
        ),
    )

    # Relationships
    attendances = relationship("DailyMealAttendance", back_populates="menu", cascade="all, delete-orphan")
    waste_log = relationship("DailyWasteLog", back_populates="menu", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MealMenu(id={self.menu_id}, date={self.meal_date}, session='{self.meal_session}')>"


class DailyMealAttendance(Base):
    """Tracks physical meal card swipes / check-ins before dining."""
    __tablename__ = "daily_meal_attendance"

    attendance_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    student_id = Column(
        String(20),
        ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    menu_id = Column(
        Integer,
        ForeignKey("meal_menus.menu_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    swiped_at = Column(DateTime, default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("student_id", "menu_id", name="uq_student_menu_attendance"),
    )

    # Relationships
    student = relationship("Student", back_populates="attendances")
    menu = relationship("MealMenu", back_populates="attendances")
    feedback = relationship("StudentFeedback", back_populates="attendance", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DailyMealAttendance(id={self.attendance_id}, student='{self.student_id}', menu={self.menu_id})>"


class FeedbackCategory(Base):
    """Standardized classification categories for food quality feedback."""
    __tablename__ = "feedback_categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    category_name = Column(String(50), nullable=False, unique=True)

    # Relationships
    feedbacks = relationship("StudentFeedback", back_populates="category")

    def __repr__(self):
        return f"<FeedbackCategory(id={self.category_id}, name='{self.category_name}')>"


class StudentFeedback(Base):
    """Verified student review submitted strictly after completing meal check-in."""
    __tablename__ = "student_feedback"

    feedback_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    attendance_id = Column(
        Integer,
        ForeignKey("daily_meal_attendance.attendance_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # Guarantees exactly 1 feedback per attendance swipe
        index=True
    )
    category_id = Column(
        Integer,
        ForeignKey("feedback_categories.category_id", ondelete="SET NULL"),
        nullable=True
    )
    rating = Column(Integer, nullable=False)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="chk_feedback_rating_range"),
    )

    # Relationships
    attendance = relationship("DailyMealAttendance", back_populates="feedback")
    category = relationship("FeedbackCategory", back_populates="feedbacks")

    def __repr__(self):
        return f"<StudentFeedback(id={self.feedback_id}, rating={self.rating})>"


class DailyWasteLog(Base):
    """Mess manager log quantifying food preparation and unconsumed/plate scrapings."""
    __tablename__ = "daily_waste_logs"

    log_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    menu_id = Column(
        Integer,
        ForeignKey("meal_menus.menu_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    prepared_weight_kg = Column(Float, nullable=False)
    unconsumed_kitchen_waste_kg = Column(Float, nullable=False)
    plate_scrap_waste_kg = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("prepared_weight_kg >= 0", name="chk_prep_weight_positive"),
        CheckConstraint("unconsumed_kitchen_waste_kg >= 0", name="chk_kitchen_waste_positive"),
        CheckConstraint("plate_scrap_waste_kg >= 0", name="chk_plate_scrap_positive"),
        CheckConstraint(
            "prepared_weight_kg >= (unconsumed_kitchen_waste_kg + plate_scrap_waste_kg)",
            name="chk_waste_less_than_prepared"
        ),
    )

    # Relationships
    menu = relationship("MealMenu", back_populates="waste_log")

    @property
    def total_waste_kg(self) -> float:
        return round(self.unconsumed_kitchen_waste_kg + self.plate_scrap_waste_kg, 2)

    @property
    def waste_percentage(self) -> float:
        if self.prepared_weight_kg <= 0:
            return 0.0
        return round((self.total_waste_kg / self.prepared_weight_kg) * 100, 2)

    def __repr__(self):
        return f"<DailyWasteLog(id={self.log_id}, menu={self.menu_id}, total_waste={self.total_waste_kg}kg)>"
