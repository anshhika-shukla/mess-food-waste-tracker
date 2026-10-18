from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict


# ==========================================
# Student Schemas
# ==========================================
class StudentBase(BaseModel):
    student_id: str = Field(..., max_length=20, examples=["STU101"])
    full_name: str = Field(..., max_length=100, examples=["Aarav Sharma"])
    hostel_block: str = Field(..., max_length=50, examples=["Block A"])
    room_no: str = Field(..., max_length=20, examples=["104"])
    is_active: bool = True


class StudentCreate(StudentBase):
    pass


class StudentResponse(StudentBase):
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Meal Menu Schemas
# ==========================================
class MealMenuBase(BaseModel):
    meal_date: date
    meal_session: str = Field(..., examples=["Lunch"])
    menu_items: str = Field(..., examples=["Rajma Masala, Rice, Phulka, Boondi Raita"])

    @field_validator("meal_session")
    @classmethod
    def validate_session(cls, v: str) -> str:
        valid_sessions = {"Breakfast", "Lunch", "Snacks", "Dinner"}
        capitalized = v.strip().capitalize()
        if capitalized not in valid_sessions:
            raise ValueError(f"meal_session must be one of {valid_sessions}")
        return capitalized


class MealMenuCreate(MealMenuBase):
    pass


class MealMenuResponse(MealMenuBase):
    menu_id: int
    model_config = ConfigDict(from_attributes=True)


class TodayMenuStatusResponse(BaseModel):
    menu_id: int
    meal_date: date
    meal_session: str
    menu_items: str
    is_swiped: bool = False
    attendance_id: Optional[int] = None
    feedback_submitted: bool = False
    submitted_rating: Optional[int] = None


# ==========================================
# Attendance Schemas
# ==========================================
class DailyMealAttendanceCreate(BaseModel):
    student_id: str
    menu_id: int


class DailyMealAttendanceResponse(BaseModel):
    attendance_id: int
    student_id: str
    menu_id: int
    swiped_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Feedback Category Schemas
# ==========================================
class FeedbackCategoryResponse(BaseModel):
    category_id: int
    category_name: str
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Student Feedback Schemas
# ==========================================
class StudentFeedbackCreate(BaseModel):
    attendance_id: int
    category_id: Optional[int] = None
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 (terrible) to 5 (excellent)")
    comments: Optional[str] = None


class StudentFeedbackResponse(BaseModel):
    feedback_id: int
    attendance_id: int
    category_id: Optional[int] = None
    rating: int
    comments: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Daily Waste Log Schemas
# ==========================================
class DailyWasteLogCreate(BaseModel):
    menu_id: int
    prepared_weight_kg: float = Field(..., ge=0.0)
    unconsumed_kitchen_waste_kg: float = Field(..., ge=0.0)
    plate_scrap_waste_kg: float = Field(..., ge=0.0)

    @field_validator("plate_scrap_waste_kg")
    @classmethod
    def validate_total_waste(cls, v: float, info) -> float:
        values = info.data
        prep = values.get("prepared_weight_kg")
        kitchen = values.get("unconsumed_kitchen_waste_kg")
        if prep is not None and kitchen is not None:
            if (kitchen + v) > prep:
                raise ValueError("Total waste (kitchen + plate scrap) cannot exceed prepared food weight.")
        return v


class DailyWasteLogResponse(BaseModel):
    log_id: int
    menu_id: int
    prepared_weight_kg: float
    unconsumed_kitchen_waste_kg: float
    plate_scrap_waste_kg: float
    total_waste_kg: float
    waste_percentage: float
    recorded_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Analytics & Dashboard Schemas
# ==========================================
class DashboardMetrics(BaseModel):
    total_swipes: int
    avg_rating: float
    total_prepared_kg: float
    total_waste_kg: float
    avg_waste_pct: float
    top_complaint: str


class WasteCorrelationPoint(BaseModel):
    menu_id: int
    date: str
    session: str
    menu_items: str
    avg_rating: Optional[float] = None
    waste_percentage: Optional[float] = None
    total_waste_kg: Optional[float] = None
    prepared_kg: Optional[float] = None


class CategoryBreakdownItem(BaseModel):
    category_name: str
    count: int


class LowestRatedMealItem(BaseModel):
    menu_id: int
    meal_date: str
    meal_session: str
    menu_items: str
    avg_rating: float
    review_count: int
    waste_percentage: float
    action_recommendation: str
