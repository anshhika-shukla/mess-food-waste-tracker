# Smart Mess Food Feedback & Waste Analytics Tracker

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?style=flat&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-CDN-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.x-FF6384?style=flat&logo=chartdotjs&logoColor=white)](https://www.chartjs.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Render Deployment](https://img.shields.io/badge/Render-Live_Demo-46E3B7?style=flat&logo=render&logoColor=white)](https://mess-food-waste-tracker.onrender.com)

> 🚀 **Live Demo:** [https://mess-food-waste-tracker.onrender.com](https://mess-food-waste-tracker.onrender.com)  
> 📖 **API Docs:** [https://mess-food-waste-tracker.onrender.com/docs](https://mess-food-waste-tracker.onrender.com/docs)

A production-ready college mini-project bridging student dining satisfaction with kitchen operational efficiency. The system pairs **NFC/RFID meal card swipe verification** with **authenticated student feedback** and **daily kitchen & plate waste logging** to give mess managers actionable, data-backed insights to reduce food wastage.

---

## 🌟 Key Features

### 1. Student Dining Portal
- **Daily Menu Schedule**: Displays real-time breakfast, lunch, snacks, and dinner dishes.
- **Meal Check-in / Swipe Simulation**: Simulates a physical card swipe before entering the dining hall; prevents double-swiping for the same meal session.
- **Verified Feedback Form**: Strictly unlocked **only after checking in** for that meal session; enforces a rating from 1 to 5 stars, standardized category tags (e.g. *Too Salty*, *Undercooked*, *Great Taste*), and specific comments.
- **One-Review Constraint**: Guarantees exactly one feedback entry per student attendance swipe.

### 2. Mess Manager & Analytics Dashboard
- **Executive KPI Cards**: Real-time summary of total dining swipes, overall average rating, cumulative food prepared vs. wasted (kg and %), and most frequent complaint.
- **Daily Food Waste Logger**: Easy interface for kitchen supervisors to record prepared food weight, kitchen leftovers, and plate scrapings. Features **real-time math validation** ensuring:
  $$\text{Prepared Weight} \ge \text{Kitchen Leftovers} + \text{Plate Scrapings}$$
- **Waste % vs. Average Rating Correlation Chart**: Dual-axis visualization (Chart.js) demonstrating that poor student ratings directly correlate with spikes in plate discard waste (up to 40% waste on low-rated meals).
- **Reported Issues Breakdown**: Interactive doughnut chart breaking down feedback categories to identify systemic kitchen issues (e.g. over-salting, uncalibrated frying temperatures).
- **Lowest-Rated Meals Ranking**: Data-driven backlog highlighting bottom-performing recipes paired with automated kitchen recommendations (e.g. adjust seasoning, increase boiling time, reduce batch size).

### 3. Realistic 7-Day Seed Dataset
- Pre-loaded with **15 students** across different hostels and room numbers.
- **28 scheduled meals** (Breakfast, Lunch, Snacks, Dinner across 7 days).
- **100+ attendance swipe entries** and authentic feedback reviews.
- **Correlated waste logs** illustrating high waste on poorly rated meals and low waste (<7%) on popular meals.

---

## 🏗️ System Architecture

```mermaid
graph TD
    subgraph Client Tier [Responsive Frontend]
        SP[Student Portal: Swipe & Verified Review]
        MD[Manager Dashboard: Waste Entry & Analytics]
        TW[Tailwind CSS CDN + Vanilla JS + Chart.js]
    end

    subgraph API Tier [FastAPI Application]
        REST[REST API Endpoints: /api/*]
        JINJA[Jinja2 HTML Template Rendering]
        PYD[Pydantic v2 Input Validation]
    end

    subgraph Persistence Tier [SQLAlchemy 2.0 ORM]
        FK[SQLite PRAGMA Foreign Keys = ON]
        MODELS[6 Relational Entities & Constraints]
    end

    subgraph Database Tier [Relational Database]
        DB[(mess_tracker.db / PostgreSQL)]
    end

    SP -->|JSON / Form Submissions| REST
    MD -->|Fetch Analytics & Post Waste| REST
    REST --> PYD
    PYD --> MODELS
    MODELS --> FK
    FK --> DB
    REST --> JINJA
    JINJA --> TW
```

---

## 🗄️ Relational Database Schema

The database design adheres to 3NF with cascading referential integrity and check constraints across 6 core tables:

```mermaid
erDiagram
    STUDENTS ||--o{ DAILY_MEAL_ATTENDANCE : "swipes (CASCADE)"
    MEAL_MENUS ||--o{ DAILY_MEAL_ATTENDANCE : "scheduled_in (CASCADE)"
    MEAL_MENUS ||--o| DAILY_WASTE_LOGS : "logs_waste (CASCADE)"
    DAILY_MEAL_ATTENDANCE ||--o| STUDENT_FEEDBACK : "submits (CASCADE, UNIQUE)"
    FEEDBACK_CATEGORIES ||--o{ STUDENT_FEEDBACK : "categorizes (SET NULL)"

    STUDENTS {
        string student_id PK "e.g. STU101"
        string full_name
        string hostel_block
        string room_no
        boolean is_active
    }

    MEAL_MENUS {
        int menu_id PK "Auto Increment"
        date meal_date "Indexed"
        string meal_session "Breakfast | Lunch | Snacks | Dinner"
        text menu_items "Dishes scheduled"
    }

    DAILY_MEAL_ATTENDANCE {
        int attendance_id PK "Auto Increment"
        string student_id FK "References students.student_id"
        int menu_id FK "References meal_menus.menu_id"
        datetime swiped_at "Default: now()"
    }

    FEEDBACK_CATEGORIES {
        int category_id PK "Auto Increment"
        string category_name "Unique"
    }

    STUDENT_FEEDBACK {
        int feedback_id PK "Auto Increment"
        int attendance_id FK "References daily_meal_attendance (UNIQUE)"
        int category_id FK "References feedback_categories"
        int rating "Check: 1 to 5"
        text comments
        datetime created_at
    }

    DAILY_WASTE_LOGS {
        int log_id PK "Auto Increment"
        int menu_id FK "References meal_menus (UNIQUE)"
        float prepared_weight_kg "Check: >= 0"
        float unconsumed_kitchen_waste_kg "Check: >= 0"
        float plate_scrap_waste_kg "Check: >= 0"
        datetime recorded_at
    }
```

### Constraints & Integrity Rules
1. **Swipe Uniqueness**: `UNIQUE(student_id, menu_id)` on `daily_meal_attendance` prevents duplicate check-ins for the same meal session.
2. **Review Integrity**: `UNIQUE(attendance_id)` on `student_feedback` guarantees that each physical attendance swipe can yield at most one review.
3. **Rating Range**: `CHECK(rating >= 1 AND rating <= 5)` prevents invalid scores.
4. **Waste Conservation Check**:
   $$\text{prepared\_weight\_kg} \ge (\text{unconsumed\_kitchen\_waste\_kg} + \text{plate\_scrap\_waste\_kg})$$
5. **Cascading Deletes**: When a student or menu entry is removed, associated attendance records, feedback, and waste logs cascade automatically.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10 or higher installed.
- Git installed.

### Option A: One-Click Launch (Windows)
Double-click `run.bat` in the root folder. It will:
1. Install Python dependencies from `requirements.txt`.
2. Automatically create database tables and seed realistic demo data.
3. Start the FastAPI server on `http://127.0.0.1:8000`.

---

### Option B: Manual Setup (Terminal / PowerShell / Bash)

1. **Clone or Navigate to the Repository**:
   ```bash
   cd c:\Users\Anshika\Desktop\rdbms-project
   ```

2. **Create and Activate a Virtual Environment** (Optional but Recommended):
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Seed the Database**:
   ```bash
   python seed_data.py
   ```

5. **Start the FastAPI Application**:
   ```bash
   python main.py
   # Or using uvicorn directly:
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```




## 📡 API Reference Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/students` | List all active registered students |
| `GET` | `/api/today-menu` | Fetch today's meal schedule with student swipe verification status |
| `POST` | `/api/attendance/swipe` | Record meal check-in swipe (rejects duplicates) |
| `GET` | `/api/feedback/categories` | Retrieve standardized feedback category tags |
| `POST` | `/api/feedback` | Submit verified student feedback (requires `attendance_id`) |
| `POST` | `/api/waste` | Create or update daily kitchen & plate waste log |
| `GET` | `/api/analytics/metrics` | Fetch executive KPI card statistics |
| `GET` | `/api/analytics/waste-vs-rating`| Data series for waste % vs. average rating correlation |
| `GET` | `/api/analytics/top-issues` | Category breakdown for complaint distribution chart |
| `GET` | `/api/analytics/lowest-rated-meals` | Ranked lowest-rated meals with corrective advice |

---

## 🛠️ Pushing to GitHub

To push this repository to GitHub as `mess-food-waste-tracker`:

### Option A: Using the Automated Script
Run the automated script in your terminal:
```cmd
setup_and_push.bat
```
or in PowerShell:
```powershell
.\setup_and_push.ps1
```

### Option B: Using Git & GitHub CLI Commands
```bash
# 1. Initialize local Git repository on main branch
git init -b main

# 2. Stage all files
git add .

# 3. Commit files
git commit -m "feat: initial release of Smart Mess Food Feedback and Waste Tracker"

# 4. Set remote and push:
git remote add origin https://github.com/anshhika-shukla/mess-food-waste-tracker.git
git branch -M main
git push -u origin main
```



## 📄 License
This project is licensed under the MIT License.
