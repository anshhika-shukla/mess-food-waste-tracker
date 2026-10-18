/**
 * Student Dining Portal & Verified Feedback Interaction Controller
 */
document.addEventListener("DOMContentLoaded", () => {
    const studentSelect = document.getElementById("student-select");
    const studentRoomEl = document.getElementById("student-room");
    const mealsContainer = document.getElementById("meals-container");

    // Modal elements
    const feedbackModal = document.getElementById("feedback-modal");
    const closeModalBtn = document.getElementById("close-modal-btn");
    const cancelModalBtn = document.getElementById("cancel-modal-btn");
    const feedbackForm = document.getElementById("feedback-form");
    const modalMealTitle = document.getElementById("modal-meal-title");
    const modalMenuDishes = document.getElementById("modal-menu-dishes");
    const modalAttendanceIdInput = document.getElementById("modal-attendance-id");
    const starButtons = document.querySelectorAll(".star-btn");
    const selectedRatingInput = document.getElementById("selected-rating");
    const ratingLabel = document.getElementById("rating-label");
    const categoryPills = document.querySelectorAll(".cat-pill");
    const selectedCategoryInput = document.getElementById("selected-category-id");
    const commentsInput = document.getElementById("feedback-comments");

    const ratingDescriptions = {
        1: "1 - Poor / Inedible",
        2: "2 - Below Average",
        3: "3 - Average / Acceptable",
        4: "4 - Good / Tasty",
        5: "5 - Excellent / Delicious"
    };

    // Update Room Badge based on selected option
    function updateStudentInfo() {
        const selectedOpt = studentSelect.options[studentSelect.selectedIndex];
        if (selectedOpt) {
            const hostel = selectedOpt.getAttribute("data-hostel") || "";
            const room = selectedOpt.getAttribute("data-room") || "";
            studentRoomEl.textContent = `Hostel: ${hostel} | Room: ${room}`;
        }
        loadTodayMenu();
    }

    // Fetch and render today's menus with status for currently active student
    async function loadTodayMenu() {
        const studentId = studentSelect.value;
        if (!studentId) return;

        mealsContainer.innerHTML = `
            <div class="col-span-full py-12 text-center text-slate-400">
                <svg class="w-8 h-8 animate-spin mx-auto text-emerald-500 mb-2" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                Syncing meal check-in status...
            </div>
        `;

        try {
            const res = await fetch(`/api/today-menu?student_id=${encodeURIComponent(studentId)}`);
            if (!res.ok) throw new Error("Failed to load today's menu");
            const menus = await res.json();

            if (menus.length === 0) {
                mealsContainer.innerHTML = `
                    <div class="col-span-full p-8 text-center bg-white rounded-2xl border border-slate-200">
                        <p class="text-slate-500 font-medium">No meals scheduled for today yet.</p>
                    </div>
                `;
                return;
            }

            mealsContainer.innerHTML = "";

            menus.forEach((menu) => {
                const card = document.createElement("div");
                card.className = "bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col justify-between hover:shadow-md transition-shadow";

                // Header icon & color per session
                let sessionIcon = "🍽️";
                let badgeColor = "bg-emerald-50 text-emerald-700 border-emerald-200";
                if (menu.meal_session === "Breakfast") {
                    sessionIcon = "☕";
                    badgeColor = "bg-amber-50 text-amber-700 border-amber-200";
                } else if (menu.meal_session === "Lunch") {
                    sessionIcon = "🍛";
                    badgeColor = "bg-sky-50 text-sky-700 border-sky-200";
                } else if (menu.meal_session === "Snacks") {
                    sessionIcon = "🫖";
                    badgeColor = "bg-purple-50 text-purple-700 border-purple-200";
                } else if (menu.meal_session === "Dinner") {
                    sessionIcon = "🍲";
                    badgeColor = "bg-indigo-50 text-indigo-700 border-indigo-200";
                }

                // Status Badge logic
                let statusBadgeHtml = "";
                let actionBtnHtml = "";

                if (menu.feedback_submitted) {
                    statusBadgeHtml = `
                        <span class="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
                            <svg class="w-3.5 h-3.5 text-emerald-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>
                            Feedback Submitted (${menu.submitted_rating}★)
                        </span>
                    `;
                    actionBtnHtml = `
                        <button disabled class="w-full py-2.5 px-4 bg-slate-100 text-slate-400 font-semibold text-xs rounded-xl cursor-not-allowed">
                            ✓ Feedback Recorded
                        </button>
                    `;
                } else if (menu.is_swiped) {
                    statusBadgeHtml = `
                        <span class="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full bg-sky-100 text-sky-800 border border-sky-200">
                            <span class="w-2 h-2 rounded-full bg-sky-500 animate-pulse"></span>
                            Swiped & Verified
                        </span>
                    `;
                    actionBtnHtml = `
                        <button type="button" class="open-feedback-btn w-full py-2.5 px-4 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs rounded-xl shadow-md shadow-emerald-600/20 transition-all flex items-center justify-center gap-1.5"
                            data-attendance-id="${menu.attendance_id}"
                            data-session="${menu.meal_session}"
                            data-dishes="${menu.menu_items}">
                            <span>Give Verified Feedback</span>
                            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                        </button>
                    `;
                } else {
                    statusBadgeHtml = `
                        <span class="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
                            Not Swiped
                        </span>
                    `;
                    actionBtnHtml = `
                        <button type="button" class="swipe-btn w-full py-2.5 px-4 bg-slate-900 hover:bg-emerald-600 text-white font-semibold text-xs rounded-xl shadow-sm transition-all flex items-center justify-center gap-1.5"
                            data-menu-id="${menu.menu_id}"
                            data-session="${menu.meal_session}">
                            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"></path></svg>
                            <span>Swipe Meal Card</span>
                        </button>
                    `;
                }

                card.innerHTML = `
                    <div class="p-5">
                        <div class="flex items-center justify-between mb-3">
                            <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold border ${badgeColor}">
                                <span>${sessionIcon}</span> ${menu.meal_session}
                            </span>
                            ${statusBadgeHtml}
                        </div>
                        <div class="min-h-[70px]">
                            <h4 class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">Scheduled Menu</h4>
                            <p class="text-sm font-medium text-slate-800 leading-relaxed">${menu.menu_items}</p>
                        </div>
                    </div>
                    <div class="p-4 bg-slate-50 border-t border-slate-100">
                        ${actionBtnHtml}
                    </div>
                `;

                mealsContainer.appendChild(card);
            });

            attachCardEventListeners();

        } catch (err) {
            console.error(err);
            mealsContainer.innerHTML = `
                <div class="col-span-full p-6 text-center text-rose-600 bg-rose-50 rounded-2xl border border-rose-200">
                    <p class="font-semibold">Unable to load meal schedule.</p>
                    <p class="text-xs mt-1 text-rose-500">${err.message}</p>
                </div>
            `;
        }
    }

    // Attach event listeners for Swipe Card and Open Feedback
    function attachCardEventListeners() {
        // Swipe Meal Card Handler
        document.querySelectorAll(".swipe-btn").forEach((btn) => {
            btn.addEventListener("click", async (e) => {
                const menuId = parseInt(btn.getAttribute("data-menu-id"), 10);
                const session = btn.getAttribute("data-session");
                const studentId = studentSelect.value;

                btn.disabled = true;
                btn.innerHTML = `
                    <svg class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                    </svg>
                    <span>Swiping...</span>
                `;

                try {
                    const res = await fetch("/api/attendance/swipe", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ student_id: studentId, menu_id: menuId })
                    });

                    const data = await res.json();
                    if (!res.ok) {
                        throw new Error(data.detail || "Swipe failed");
                    }

                    showToast(`Card Swiped successfully for ${session}!`, "success");
                    loadTodayMenu();
                } catch (err) {
                    showToast(err.message, "error");
                    btn.disabled = false;
                    btn.innerHTML = `
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"></path></svg>
                        <span>Swipe Meal Card</span>
                    `;
                }
            });
        });

        // Open Feedback Modal Handler
        document.querySelectorAll(".open-feedback-btn").forEach((btn) => {
            btn.addEventListener("click", () => {
                const attId = btn.getAttribute("data-attendance-id");
                const session = btn.getAttribute("data-session");
                const dishes = btn.getAttribute("data-dishes");

                openFeedbackModal(attId, session, dishes);
            });
        });
    }

    // Modal Control
    function openFeedbackModal(attendanceId, session, dishes) {
        modalAttendanceIdInput.value = attendanceId;
        modalMealTitle.textContent = `${session} Feedback`;
        modalMenuDishes.textContent = dishes;
        resetFeedbackForm();
        feedbackModal.classList.remove("hidden");
    }

    function closeFeedbackModal() {
        feedbackModal.classList.add("hidden");
        resetFeedbackForm();
    }

    function resetFeedbackForm() {
        feedbackForm.reset();
        selectedRatingInput.value = "";
        selectedCategoryInput.value = "";
        ratingLabel.textContent = "Click a star (1-5)";
        starButtons.forEach(btn => btn.classList.remove("active"));
        categoryPills.forEach(pill => pill.classList.remove("active"));
    }

    // Star Rating Event Handlers
    starButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
            const ratingVal = parseInt(btn.getAttribute("data-rating"), 10);
            selectedRatingInput.value = ratingVal;
            ratingLabel.textContent = ratingDescriptions[ratingVal] || `${ratingVal} Stars`;

            starButtons.forEach((s) => {
                const sVal = parseInt(s.getAttribute("data-rating"), 10);
                if (sVal <= ratingVal) {
                    s.classList.add("active");
                } else {
                    s.classList.remove("active");
                }
            });
        });
    });

    // Category Pill Selection
    categoryPills.forEach((pill) => {
        pill.addEventListener("click", () => {
            const catId = pill.getAttribute("data-cat-id");
            if (pill.classList.contains("active")) {
                pill.classList.remove("active");
                selectedCategoryInput.value = "";
            } else {
                categoryPills.forEach(p => p.classList.remove("active"));
                pill.classList.add("active");
                selectedCategoryInput.value = catId;
            }
        });
    });

    // Feedback Submission
    feedbackForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const rating = parseInt(selectedRatingInput.value, 10);
        if (!rating || rating < 1 || rating > 5) {
            showToast("Please select a rating between 1 and 5 stars.", "error");
            return;
        }

        const attendanceId = parseInt(modalAttendanceIdInput.value, 10);
        const categoryId = selectedCategoryInput.value ? parseInt(selectedCategoryInput.value, 10) : null;
        const comments = commentsInput.value.trim() || null;

        const submitBtn = document.getElementById("submit-feedback-btn");
        submitBtn.disabled = true;
        submitBtn.textContent = "Submitting...";

        try {
            const res = await fetch("/api/feedback", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    attendance_id: attendanceId,
                    category_id: categoryId,
                    rating: rating,
                    comments: comments
                })
            });

            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.detail || "Feedback submission failed");
            }

            showToast("Verified review recorded. Thank you for your feedback!", "success");
            closeFeedbackModal();
            loadTodayMenu();
        } catch (err) {
            showToast(err.message, "error");
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = "Submit Verified Review";
        }
    });

    closeModalBtn.addEventListener("click", closeFeedbackModal);
    cancelModalBtn.addEventListener("click", closeFeedbackModal);
    studentSelect.addEventListener("change", updateStudentInfo);

    // Initial load
    updateStudentInfo();
});
