import os
from datetime import date, datetime
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Request, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc

from app.database import engine, get_db, create_tables
from app.models import (
    Student,
    MealMenu,
    DailyMealAttendance,
    FeedbackCategory,
    StudentFeedback,
    DailyWasteLog
)
from app.schemas import (
    StudentResponse,
    MealMenuResponse,
    TodayMenuStatusResponse,
    DailyMealAttendanceCreate,
    DailyMealAttendanceResponse,
    FeedbackCategoryResponse,
    StudentFeedbackCreate,
    StudentFeedbackResponse,
    DailyWasteLogCreate,
    DailyWasteLogResponse,
    DashboardMetrics,
    WasteCorrelationPoint,
    CategoryBreakdownItem,
    LowestRatedMealItem
)
from app.seed_data import seed_database


# Lifespan context to ensure tables & seed data exist on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    # Check if DB has data; if empty, seed immediately
    db = next(get_db())
    try:
        if db.query(Student).count() == 0:
            print("Database empty on startup. Automatically seeding realistic demo data...")
            seed_database()
    finally:
        db.close()
    yield


app = FastAPI(
    title="Smart Mess Food Feedback & Waste Analytics Tracker",
    description="A production-grade college mess management and food waste reduction platform.",
    version="1.0.0",
    lifespan=lifespan
)

# Static files and Templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


# =========================================================================
# Web Frontend Routes
# =========================================================================

@app.get("/", response_class=RedirectResponse, include_in_schema=False)
def root():
    return RedirectResponse(url="/student")


@app.get("/student", response_class=HTMLResponse)
def student_portal_page(request: Request, db: Session = Depends(get_db)):
    students = db.query(Student).filter(Student.is_active == True).order_by(Student.student_id).all()
    categories = db.query(FeedbackCategory).order_by(FeedbackCategory.category_name).all()
    today_str = date.today().strftime("%A, %B %d, %Y")
    return templates.TemplateResponse(
        "student.html",
        {
            "request": request,
            "students": students,
            "categories": categories,
            "today_str": today_str,
            "active_page": "student"
        }
    )


@app.get("/manager", response_class=HTMLResponse)
def manager_dashboard_page(request: Request, db: Session = Depends(get_db)):
    # Recent menus for the waste entry select dropdown (past 7 days)
    menus = db.query(MealMenu).order_by(desc(MealMenu.meal_date), MealMenu.meal_session).limit(28).all()
    today_str = date.today().strftime("%A, %B %d, %Y")
    return templates.TemplateResponse(
        "manager.html",
        {
            "request": request,
            "menus": menus,
            "today_str": today_str,
            "active_page": "manager"
        }
    )


@app.get("/menu", response_class=HTMLResponse)
def menu_schedule_page(request: Request, db: Session = Depends(get_db)):
    # Fetch all menus ordered by date and session
    all_menus = db.query(MealMenu).order_by(desc(MealMenu.meal_date)).all()
    # Group menus by date
    grouped = {}
    for m in all_menus:
        d_str = m.meal_date.strftime("%Y-%m-%d")
        if d_str not in grouped:
            grouped[d_str] = {
                "date_obj": m.meal_date,
                "display": m.meal_date.strftime("%A, %b %d, %Y"),
                "sessions": {}
            }
        grouped[d_str]["sessions"][m.meal_session] = m

    return templates.TemplateResponse(
        "menu_schedule.html",
        {
            "request": request,
            "grouped_menus": grouped,
            "active_page": "menu"
        }
    )


# =========================================================================
# REST API Endpoints
# =========================================================================

@app.get("/api/students", response_model=List[StudentResponse], tags=["Students"])
def list_students(db: Session = Depends(get_db)):
    """Fetch list of all active registered students."""
    return db.query(Student).filter(Student.is_active == True).order_by(Student.student_id).all()


@app.get("/api/today-menu", response_model=List[TodayMenuStatusResponse], tags=["Menus"])
def get_today_menu(
    student_id: Optional[str] = Query(None, description="Optional student ID to verify attendance & feedback status"),
    target_date: Optional[date] = Query(None, description="Optional date filter (defaults to today)"),
    db: Session = Depends(get_db)
):
    """Retrieve scheduled meal menus for a date with student swipe verification status."""
    query_date = target_date or date.today()
    menus = db.query(MealMenu).filter(MealMenu.meal_date == query_date).all()

    # Pre-sort according to standard session order
    order = {"Breakfast": 1, "Lunch": 2, "Snacks": 3, "Dinner": 4}
    menus.sort(key=lambda m: order.get(m.meal_session, 5))

    results = []
    for m in menus:
        is_swiped = False
        att_id = None
        fb_submitted = False
        rating = None

        if student_id:
            attendance = db.query(DailyMealAttendance).filter_by(
                student_id=student_id, menu_id=m.menu_id
            ).first()
            if attendance:
                is_swiped = True
                att_id = attendance.attendance_id
                feedback = db.query(StudentFeedback).filter_by(attendance_id=attendance.attendance_id).first()
                if feedback:
                    fb_submitted = True
                    rating = feedback.rating

        results.append(TodayMenuStatusResponse(
            menu_id=m.menu_id,
            meal_date=m.meal_date,
            meal_session=m.meal_session,
            menu_items=m.menu_items,
            is_swiped=is_swiped,
            attendance_id=att_id,
            feedback_submitted=fb_submitted,
            submitted_rating=rating
        ))
    return results


@app.post("/api/attendance/swipe", response_model=DailyMealAttendanceResponse, status_code=status.HTTP_201_CREATED, tags=["Attendance"])
def swipe_meal_attendance(data: DailyMealAttendanceCreate, db: Session = Depends(get_db)):
    """Simulates physical NFC/RFID card swipe. Prevents double-swiping for the same meal."""
    # Verify student
    student = db.query(Student).filter_by(student_id=data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student '{data.student_id}' not found.")
    if not student.is_active:
        raise HTTPException(status_code=400, detail=f"Student account '{data.student_id}' is inactive.")

    # Verify menu
    menu = db.query(MealMenu).filter_by(menu_id=data.menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Meal menu not found.")

    # Check for existing swipe
    existing = db.query(DailyMealAttendance).filter_by(
        student_id=data.student_id, menu_id=data.menu_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Card already swiped for this {menu.meal_session} session at {existing.swiped_at.strftime('%H:%M:%S')}."
        )

    attendance = DailyMealAttendance(
        student_id=data.student_id,
        menu_id=data.menu_id,
        swiped_at=datetime.now()
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


@app.get("/api/feedback/categories", response_model=List[FeedbackCategoryResponse], tags=["Feedback"])
def list_feedback_categories(db: Session = Depends(get_db)):
    """Retrieve all standardized feedback categorization tags."""
    return db.query(FeedbackCategory).order_by(FeedbackCategory.category_id).all()


@app.post("/api/feedback", response_model=StudentFeedbackResponse, status_code=status.HTTP_201_CREATED, tags=["Feedback"])
def submit_feedback(data: StudentFeedbackCreate, db: Session = Depends(get_db)):
    """Submit verified student feedback. Strictly requires an authenticated attendance check-in ID."""
    # 1. Verify attendance exists
    attendance = db.query(DailyMealAttendance).filter_by(attendance_id=data.attendance_id).first()
    if not attendance:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized: You must swipe / check-in for this meal before submitting feedback."
        )

    # 2. Check if feedback already submitted for this attendance (enforcing 1 review per meal)
    existing_fb = db.query(StudentFeedback).filter_by(attendance_id=data.attendance_id).first()
    if existing_fb:
        raise HTTPException(
            status_code=400,
            detail="Feedback has already been submitted for this meal check-in."
        )

    # 3. Create feedback
    fb = StudentFeedback(
        attendance_id=data.attendance_id,
        category_id=data.category_id,
        rating=data.rating,
        comments=data.comments,
        created_at=datetime.now()
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb


@app.post("/api/waste", response_model=DailyWasteLogResponse, tags=["Waste Management"])
def record_or_update_waste_log(data: DailyWasteLogCreate, db: Session = Depends(get_db)):
    """Mess Manager endpoint to log or update daily food preparation and unconsumed/scrap waste."""
    # Validate menu
    menu = db.query(MealMenu).filter_by(menu_id=data.menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Meal menu not found.")

    # Business rule validation: prepared >= kitchen + scrap
    if (data.unconsumed_kitchen_waste_kg + data.plate_scrap_waste_kg) > data.prepared_weight_kg:
        raise HTTPException(
            status_code=400,
            detail="Invalid waste entry: Total waste (kitchen leftovers + plate scrapings) cannot exceed prepared food weight."
        )

    log = db.query(DailyWasteLog).filter_by(menu_id=data.menu_id).first()
    if log:
        # Update existing
        log.prepared_weight_kg = data.prepared_weight_kg
        log.unconsumed_kitchen_waste_kg = data.unconsumed_kitchen_waste_kg
        log.plate_scrap_waste_kg = data.plate_scrap_waste_kg
        log.recorded_at = datetime.now()
    else:
        # Create new
        log = DailyWasteLog(
            menu_id=data.menu_id,
            prepared_weight_kg=data.prepared_weight_kg,
            unconsumed_kitchen_waste_kg=data.unconsumed_kitchen_waste_kg,
            plate_scrap_waste_kg=data.plate_scrap_waste_kg,
            recorded_at=datetime.now()
        )
        db.add(log)

    db.commit()
    db.refresh(log)
    return DailyWasteLogResponse(
        log_id=log.log_id,
        menu_id=log.menu_id,
        prepared_weight_kg=log.prepared_weight_kg,
        unconsumed_kitchen_waste_kg=log.unconsumed_kitchen_waste_kg,
        plate_scrap_waste_kg=log.plate_scrap_waste_kg,
        total_waste_kg=log.total_waste_kg,
        waste_percentage=log.waste_percentage,
        recorded_at=log.recorded_at
    )


# =========================================================================
# Analytics & Reporting Endpoints
# =========================================================================

@app.get("/api/analytics/metrics", response_model=DashboardMetrics, tags=["Analytics"])
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Fetch high-level KPI cards for the manager dashboard."""
    total_swipes = db.query(func.count(DailyMealAttendance.attendance_id)).scalar() or 0
    avg_rating_val = db.query(func.avg(StudentFeedback.rating)).scalar() or 0.0

    prep_sum = db.query(func.sum(DailyWasteLog.prepared_weight_kg)).scalar() or 0.0
    kitchen_sum = db.query(func.sum(DailyWasteLog.unconsumed_kitchen_waste_kg)).scalar() or 0.0
    scrap_sum = db.query(func.sum(DailyWasteLog.plate_scrap_waste_kg)).scalar() or 0.0
    total_waste = kitchen_sum + scrap_sum

    waste_pct = round((total_waste / prep_sum * 100), 2) if prep_sum > 0 else 0.0

    # Top reported issue (excluding 'Great Taste')
    top_issue = (
        db.query(FeedbackCategory.category_name, func.count(StudentFeedback.feedback_id).label("issue_count"))
        .join(StudentFeedback, FeedbackCategory.category_id == StudentFeedback.category_id)
        .filter(FeedbackCategory.category_name != "Great Taste")
        .group_by(FeedbackCategory.category_name)
        .order_by(desc("issue_count"))
        .first()
    )
    top_complaint_name = top_issue[0] if top_issue else "None Reported"

    return DashboardMetrics(
        total_swipes=total_swipes,
        avg_rating=round(float(avg_rating_val), 2),
        total_prepared_kg=round(float(prep_sum), 1),
        total_waste_kg=round(float(total_waste), 1),
        avg_waste_pct=waste_pct,
        top_complaint=top_complaint_name
    )


@app.get("/api/analytics/waste-vs-rating", response_model=List[WasteCorrelationPoint], tags=["Analytics"])
def get_waste_vs_rating_correlation(db: Session = Depends(get_db)):
    """Returns chronologically ordered points linking average student rating and waste % per meal."""
    menus = (
        db.query(MealMenu)
        .join(DailyWasteLog, MealMenu.menu_id == DailyWasteLog.menu_id)
        .order_by(asc(MealMenu.meal_date), asc(MealMenu.menu_id))
        .all()
    )

    points = []
    for m in menus:
        # Calculate avg rating for this menu
        avg_r = (
            db.query(func.avg(StudentFeedback.rating))
            .join(DailyMealAttendance, StudentFeedback.attendance_id == DailyMealAttendance.attendance_id)
            .filter(DailyMealAttendance.menu_id == m.menu_id)
            .scalar()
        )
        waste = m.waste_log
        points.append(WasteCorrelationPoint(
            menu_id=m.menu_id,
            date=m.meal_date.strftime("%d %b"),
            session=m.meal_session,
            menu_items=m.menu_items[:30] + "..." if len(m.menu_items) > 30 else m.menu_items,
            avg_rating=round(float(avg_r), 2) if avg_r is not None else None,
            waste_percentage=waste.waste_percentage if waste else None,
            total_waste_kg=waste.total_waste_kg if waste else None,
            prepared_kg=waste.prepared_weight_kg if waste else None
        ))
    return points


@app.get("/api/analytics/top-issues", response_model=List[CategoryBreakdownItem], tags=["Analytics"])
def get_top_issues_breakdown(db: Session = Depends(get_db)):
    """Returns frequency distribution of student feedback categories for pie/bar chart."""
    results = (
        db.query(FeedbackCategory.category_name, func.count(StudentFeedback.feedback_id).label("cat_count"))
        .join(StudentFeedback, FeedbackCategory.category_id == StudentFeedback.category_id)
        .group_by(FeedbackCategory.category_name)
        .order_by(desc("cat_count"))
        .all()
    )
    return [CategoryBreakdownItem(category_name=row[0], count=row[1]) for row in results]


@app.get("/api/analytics/lowest-rated-meals", response_model=List[LowestRatedMealItem], tags=["Analytics"])
def get_lowest_rated_meals(limit: int = 5, db: Session = Depends(get_db)):
    """Ranks lowest-rated meals and generates actionable kitchen recommendations."""
    query_results = (
        db.query(
            MealMenu,
            func.avg(StudentFeedback.rating).label("avg_rating"),
            func.count(StudentFeedback.feedback_id).label("review_count")
        )
        .join(DailyMealAttendance, MealMenu.menu_id == DailyMealAttendance.menu_id)
        .join(StudentFeedback, DailyMealAttendance.attendance_id == StudentFeedback.attendance_id)
        .group_by(MealMenu.menu_id)
        .having(func.count(StudentFeedback.feedback_id) >= 2)
        .order_by(asc("avg_rating"))
        .limit(limit)
        .all()
    )

    ranked_items = []
    for menu, avg_r, rev_count in query_results:
        waste_pct = menu.waste_log.waste_percentage if menu.waste_log else 0.0

        # Actionable recommendations based on dishes and rating
        dishes_lower = menu.menu_items.lower()
        if "lauki" in dishes_lower or "bland" in dishes_lower:
            action = "Revamp seasoning & spices; replace bland gourd with popular seasonal curry"
        elif "soya" in dishes_lower or "undercooked" in dishes_lower:
            action = "Increase boiling & marination time for soya chunks to eliminate chewy texture"
        elif "salt" in dishes_lower:
            action = "Standardize salt measurement ratios; check kitchen seasoning consistency"
        elif "pakoda" in dishes_lower or "oily" in dishes_lower:
            action = "Calibrate oil temperature and drain snacks thoroughly on food-grade paper"
        elif avg_r < 2.5 and waste_pct > 30.0:
            action = "High waste alert: reduce preparation portion size by 25% and overhaul recipe"
        else:
            action = "Collect student focus group suggestions before next rotation"

        ranked_items.append(LowestRatedMealItem(
            menu_id=menu.menu_id,
            meal_date=menu.meal_date.strftime("%Y-%m-%d"),
            meal_session=menu.meal_session,
            menu_items=menu.menu_items,
            avg_rating=round(float(avg_r), 2),
            review_count=rev_count,
            waste_percentage=waste_pct,
            action_recommendation=action
        ))

    return ranked_items
