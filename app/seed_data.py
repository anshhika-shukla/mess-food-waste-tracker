import random
from datetime import date, datetime, timedelta
from app.database import engine, SessionLocal, create_tables
from app.models import (
    Student,
    MealMenu,
    DailyMealAttendance,
    FeedbackCategory,
    StudentFeedback,
    DailyWasteLog
)


def seed_database():
    """Seeds the database with realistic historical mess dining data."""
    print("Initializing database tables...")
    create_tables()

    db = SessionLocal()
    try:
        # Check if already seeded
        existing_students = db.query(Student).count()
        if existing_students >= 15:
            print("Database already contains seeded data. Skipping seed.")
            return

        print("Seeding students...")
        students_data = [
            ("STU101", "Aarav Sharma", "Block A", "101"),
            ("STU102", "Diya Patel", "Sarojini Hall", "204"),
            ("STU103", "Rohan Verma", "Block B", "312"),
            ("STU104", "Ananya Iyer", "Sarojini Hall", "118"),
            ("STU105", "Kabir Mehta", "Block A", "205"),
            ("STU106", "Sneha Kulkarni", "Gargi Hall", "102"),
            ("STU107", "Aditya Nair", "Ramanujan Hostel", "401"),
            ("STU108", "Pooja Reddy", "Gargi Hall", "309"),
            ("STU109", "Vikram Singh", "Block B", "115"),
            ("STU110", "Ishita Gupta", "Sarojini Hall", "215"),
            ("STU111", "Rishi Mukherjee", "Ramanujan Hostel", "202"),
            ("STU112", "Tanvi Joshi", "Gargi Hall", "404"),
            ("STU113", "Siddharth Rao", "Block A", "308"),
            ("STU114", "Meera Nambiar", "Sarojini Hall", "301"),
            ("STU115", "Karan Malhotra", "Block B", "220"),
        ]

        for sid, name, block, room in students_data:
            existing = db.query(Student).filter_by(student_id=sid).first()
            if not existing:
                db.add(Student(student_id=sid, full_name=name, hostel_block=block, room_no=room, is_active=True))
        db.commit()

        print("Seeding feedback categories...")
        categories = [
            "Great Taste",
            "Too Salty",
            "Undercooked",
            "Cold Food",
            "Too Spicy",
            "Oily / Greasy",
            "Bland / Tasteless",
            "Small Portion"
        ]
        cat_map = {}
        for cat_name in categories:
            cat_obj = db.query(FeedbackCategory).filter_by(category_name=cat_name).first()
            if not cat_obj:
                cat_obj = FeedbackCategory(category_name=cat_name)
                db.add(cat_obj)
                db.flush()
            cat_map[cat_name] = cat_obj.category_id
        db.commit()

        print("Seeding 7-day meal schedules, attendance, feedback, and waste logs...")
        today = date.today()

        # Define 7 days of realistic menu templates with intentional quality/waste profiles
        # quality_profile: 'high' (rating ~4.5, waste ~6%), 'average' (rating ~3.2, waste ~18%), 'poor' (rating ~2.0, waste ~38%)
        weekly_menu_templates = [
            {
                "day_offset": -6,
                "sessions": [
                    ("Breakfast", "Aloo Paratha, Fresh Curd, Mixed Pickle, Mint Tea", "high"),
                    ("Lunch", "Kadhi Pakoda, Jeera Rice, Aloo Beans Sabzi, Phulka, Papad", "average"),
                    ("Snacks", "Vegetable Cutlets, Green Mint Chutney, Tea", "average"),
                    ("Dinner", "Paneer Lababdar, Butter Naan, Veg Pulao, Gulab Jamun", "high")
                ]
            },
            {
                "day_offset": -5,
                "sessions": [
                    ("Breakfast", "Poha, Sev, Boiled Sprouted Moong, Filter Coffee", "average"),
                    ("Lunch", "Watery Lauki Kofta, Plain Rice, Chapati, Tomato Soup", "poor"),
                    ("Snacks", "Biscuits, Masala Tea", "average"),
                    ("Dinner", "Dal Makhani, Jeera Rice, Tandoori Roti, Boondi Raita", "high")
                ]
            },
            {
                "day_offset": -4,
                "sessions": [
                    ("Breakfast", "Masala Dosa, Sambar, Coconut Chutney, Coffee", "high"),
                    ("Lunch", "Rajma Masala, Steamed Basmati Rice, Phulka, Onion Salad", "high"),
                    ("Snacks", "Bread Pakoda with Ketchup, Cutting Chai", "poor"),  # excessively oily
                    ("Dinner", "Undercooked Soya Chaap Curry, Rice, Roti, Salad", "poor")
                ]
            },
            {
                "day_offset": -3,
                "sessions": [
                    ("Breakfast", "Idli Vada Combo, Hot Sambar, Tomato Chutney", "high"),
                    ("Lunch", "High Salt Dal Tadka, Aloo Gobhi, Rice, Phulka", "poor"),  # too salty
                    ("Snacks", "Puffed Rice Bhel, Ginger Tea", "average"),
                    ("Dinner", "Mutter Paneer, Dal Fry, Jeera Rice, Chapati, Kheer", "high")
                ]
            },
            {
                "day_offset": -2,
                "sessions": [
                    ("Breakfast", "Upma with Coconut Chutney, Banana, Tea", "average"),
                    ("Lunch", "Chole Bhature, Masala Rice, Pickled Onions, Chaas", "high"),
                    ("Snacks", "Samosa, Mint Chutney, Masala Tea", "average"),
                    ("Dinner", "Bland Mixed Vegetable Korma, Steamed Rice, Phulka", "poor")
                ]
            },
            {
                "day_offset": -1,
                "sessions": [
                    ("Breakfast", "Puri Bhaji, Halwa, Masala Chai", "high"),
                    ("Lunch", "Sambar Rice, Poriyal, Curd Rice, Appalam", "average"),
                    ("Snacks", "Corn Chaat, Green Tea", "high"),
                    ("Dinner", "Veg Dum Biryani, Mirchi Ka Salan, Raita, Rasgulla", "high")
                ]
            },
            {
                "day_offset": 0,  # Today
                "sessions": [
                    ("Breakfast", "Methi Thepla, Sweet Lime Pickle, Masala Omelette / Sprout Salad, Tea", "high"),
                    ("Lunch", "Dal Palak, Paneer Bhurji, Steamed Rice, Tawa Roti, Salad", "high"),
                    ("Snacks", "Onion Pakoda with Mint Chutney, Filter Coffee", "average"),
                    ("Dinner", "Special Shahi Paneer, Garlic Naan, Veg Pulao, Ice Cream", "high")
                ]
            }
        ]

        all_students = db.query(Student).all()

        for day_plan in weekly_menu_templates:
            meal_date = today + timedelta(days=day_plan["day_offset"])

            for session_name, dishes, quality in day_plan["sessions"]:
                # 1. Create or fetch Menu
                menu = db.query(MealMenu).filter_by(meal_date=meal_date, meal_session=session_name).first()
                if not menu:
                    menu = MealMenu(meal_date=meal_date, meal_session=session_name, menu_items=dishes)
                    db.add(menu)
                    db.flush()

                # Session baseline hours for realistic swipe timestamp
                hour_map = {"Breakfast": 8, "Lunch": 13, "Snacks": 17, "Dinner": 20}
                base_hour = hour_map.get(session_name, 12)

                # Determine student turnout: between 10 and 15 students swipe
                num_attendees = random.randint(11, 15)
                attendee_students = random.sample(all_students, num_attendees)

                feedbacks_for_this_menu = []

                for student in attendee_students:
                    # 2. DailyMealAttendance
                    attendance = db.query(DailyMealAttendance).filter_by(
                        student_id=student.student_id, menu_id=menu.menu_id
                    ).first()

                    if not attendance:
                        swipe_minute = random.randint(5, 55)
                        swiped_time = datetime(
                            meal_date.year, meal_date.month, meal_date.day,
                            base_hour, swipe_minute, random.randint(0, 59)
                        )
                        attendance = DailyMealAttendance(
                            student_id=student.student_id,
                            menu_id=menu.menu_id,
                            swiped_at=swiped_time
                        )
                        db.add(attendance)
                        db.flush()

                    # 3. Student Feedback (about 70% of attendees leave feedback)
                    # For today's upcoming/current meals (e.g., Dinner/Snacks if earlier in day), leave some unsubmitted
                    is_today = (day_plan["day_offset"] == 0)
                    submit_feedback = random.random() < 0.75

                    if submit_feedback:
                        existing_fb = db.query(StudentFeedback).filter_by(attendance_id=attendance.attendance_id).first()
                        if not existing_fb:
                            if quality == "high":
                                rating = random.choices([4, 5], weights=[0.3, 0.7])[0]
                                cat_name = "Great Taste"
                                comments_pool = [
                                    "Food was delicious and fresh!",
                                    "Loved the spices and soft bread.",
                                    "One of the best meals this semester.",
                                    "Great taste and quick service at the counter.",
                                    "Gulab jamun and paneer were top notch!"
                                ]
                            elif quality == "poor":
                                rating = random.choices([1, 2], weights=[0.6, 0.4])[0]
                                if "Lauki" in dishes or "Bland" in dishes:
                                    cat_name = "Bland / Tasteless"
                                    comments_pool = ["Zero taste or spices, feels completely watery.", "Very bland."]
                                elif "Soyabean" in dishes or "Undercooked" in dishes:
                                    cat_name = "Undercooked"
                                    comments_pool = ["Soyabean was tough and undercooked.", "Vegetables were half-raw."]
                                elif "Salt" in dishes:
                                    cat_name = "Too Salty"
                                    comments_pool = ["Inedible due to excessive salt!", "Way too much salt in the dal."]
                                elif "Bread Pakoda" in dishes:
                                    cat_name = "Oily / Greasy"
                                    comments_pool = ["Completely soaked in leftover burnt oil.", "Felt nauseous from the oil."]
                                else:
                                    cat_name = "Cold Food"
                                    comments_pool = ["Food was lukewarm and stale.", "Cold food served."]
                            else:  # average
                                rating = random.choices([2, 3, 4], weights=[0.2, 0.5, 0.3])[0]
                                if rating == 4:
                                    cat_name = "Great Taste"
                                    comments_pool = ["Decent meal overall.", "Good taste today."]
                                elif rating == 3:
                                    cat_name = random.choice(["Portion Size", "Bland / Tasteless"])
                                    comments_pool = ["Average taste, could use more vegetables.", "Portion was slightly small."]
                                else:
                                    cat_name = random.choice(["Cold Food", "Too Spicy"])
                                    comments_pool = ["A bit too spicy for lunch.", "Was cold by the time I ate."]

                            fb = StudentFeedback(
                                attendance_id=attendance.attendance_id,
                                category_id=cat_map.get(cat_name),
                                rating=rating,
                                comments=random.choice(comments_pool),
                                created_at=attendance.swiped_at + timedelta(minutes=random.randint(15, 35))
                            )
                            db.add(fb)
                            feedbacks_for_this_menu.append(rating)

                # 4. Daily Waste Log
                # Correlate waste with quality profile:
                # - High quality (avg ~4.5): Prep 85kg -> Kitchen waste ~3kg, Plate scrap ~3kg -> Total ~6kg (7%)
                # - Average quality (avg ~3.2): Prep 80kg -> Kitchen waste ~6kg, Plate scrap ~9kg -> Total ~15kg (18.7%)
                # - Poor quality (avg ~2.0): Prep 78kg -> Kitchen waste ~10kg, Plate scrap ~22kg -> Total ~32kg (41%)
                existing_waste = db.query(DailyWasteLog).filter_by(menu_id=menu.menu_id).first()
                if not existing_waste:
                    if quality == "high":
                        prep = round(random.uniform(80.0, 90.0), 1)
                        kitchen = round(random.uniform(2.0, 4.5), 1)
                        plate = round(random.uniform(2.5, 5.0), 1)
                    elif quality == "poor":
                        prep = round(random.uniform(75.0, 82.0), 1)
                        kitchen = round(random.uniform(8.0, 12.0), 1)
                        plate = round(random.uniform(18.0, 24.0), 1)
                    else:  # average
                        prep = round(random.uniform(78.0, 85.0), 1)
                        kitchen = round(random.uniform(4.5, 7.5), 1)
                        plate = round(random.uniform(7.0, 11.5), 1)

                    # Ensure check constraint prepared >= kitchen + plate strictly holds
                    if (kitchen + plate) >= prep:
                        prep = kitchen + plate + 5.0

                    waste_log = DailyWasteLog(
                        menu_id=menu.menu_id,
                        prepared_weight_kg=prep,
                        unconsumed_kitchen_waste_kg=kitchen,
                        plate_scrap_waste_kg=plate,
                        recorded_at=datetime(
                            meal_date.year, meal_date.month, meal_date.day,
                            base_hour + 2, random.randint(10, 45)
                        )
                    )
                    db.add(waste_log)

        db.commit()
        print("Database seeded successfully with 15 students, 28 menus, attendance, feedback & waste logs!")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
