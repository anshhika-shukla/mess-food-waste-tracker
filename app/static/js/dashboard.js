/**
 * Mess Manager & Waste Analytics Dashboard Controller
 */
document.addEventListener("DOMContentLoaded", () => {
    let correlationChart = null;
    let issuesChart = null;

    // Elements
    const refreshBtn = document.getElementById("refresh-dashboard-btn");
    const wasteForm = document.getElementById("waste-log-form");
    const menuSelect = document.getElementById("waste-menu-select");
    const prepInput = document.getElementById("prep-weight");
    const kitchenInput = document.getElementById("kitchen-waste");
    const scrapInput = document.getElementById("scrap-waste");
    const liveTotalWasteEl = document.getElementById("live-total-waste");
    const liveWastePctEl = document.getElementById("live-waste-pct");
    const warningEl = document.getElementById("waste-constraint-warning");
    const submitWasteBtn = document.getElementById("submit-waste-btn");
    const lowestMealsTbody = document.getElementById("lowest-meals-tbody");

    // KPI Elements
    const kpiSwipes = document.getElementById("kpi-swipes");
    const kpiRating = document.getElementById("kpi-rating");
    const kpiWaste = document.getElementById("kpi-waste");
    const kpiWastePct = document.getElementById("kpi-waste-pct");
    const kpiComplaint = document.getElementById("kpi-complaint");

    // 1. Fetch & Update KPI Metrics
    async function loadKPIMetrics() {
        try {
            const res = await fetch("/api/analytics/metrics");
            if (!res.ok) throw new Error("Failed to load KPI metrics");
            const data = await res.json();

            kpiSwipes.textContent = data.total_swipes.toLocaleString();
            kpiRating.textContent = data.avg_rating.toFixed(1);
            kpiWaste.textContent = `${data.total_waste_kg} kg`;
            kpiWastePct.textContent = `(${data.avg_waste_pct}%)`;
            kpiComplaint.textContent = data.top_complaint;
        } catch (err) {
            console.error("KPI load error:", err);
        }
    }

    // 2. Render Correlation Chart (Waste % vs Average Rating)
    async function loadCorrelationChart() {
        try {
            const res = await fetch("/api/analytics/waste-vs-rating");
            if (!res.ok) throw new Error("Failed to load correlation data");
            const data = await res.json();

            const labels = data.map(d => `${d.date} (${d.session[0]})`);
            const wasteData = data.map(d => d.waste_percentage);
            const ratingData = data.map(d => d.avg_rating);

            const ctx = document.getElementById("correlationChart").getContext("2d");

            if (correlationChart) {
                correlationChart.destroy();
            }

            correlationChart = new Chart(ctx, {
                type: "bar",
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: "Food Waste %",
                            data: wasteData,
                            backgroundColor: "rgba(244, 63, 94, 0.7)", // rose-500
                            borderColor: "rgba(244, 63, 94, 1)",
                            borderWidth: 1,
                            borderRadius: 6,
                            yAxisID: "yWaste",
                            order: 2
                        },
                        {
                            label: "Average Student Rating (★)",
                            data: ratingData,
                            type: "line",
                            borderColor: "rgba(245, 158, 11, 1)", // amber-500
                            backgroundColor: "rgba(245, 158, 11, 0.15)",
                            pointBackgroundColor: "rgba(245, 158, 11, 1)",
                            pointRadius: 4,
                            pointHoverRadius: 6,
                            borderWidth: 2.5,
                            tension: 0.35,
                            yAxisID: "yRating",
                            order: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: "index",
                        intersect: false
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: "rgba(15, 23, 42, 0.9)",
                            titleFont: { size: 12, weight: "bold" },
                            bodyFont: { size: 12 },
                            padding: 10,
                            cornerRadius: 8,
                            callbacks: {
                                afterTitle: function(items) {
                                    const index = items[0].dataIndex;
                                    return `Menu: ${data[index].menu_items}`;
                                },
                                label: function(context) {
                                    if (context.dataset.yAxisID === "yWaste") {
                                        return `Waste: ${context.parsed.y}%`;
                                    } else {
                                        return `Rating: ${context.parsed.y} ★`;
                                    }
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: { font: { size: 10 } }
                        },
                        yWaste: {
                            type: "linear",
                            position: "left",
                            min: 0,
                            max: 60,
                            title: {
                                display: true,
                                text: "Waste %",
                                font: { size: 11, weight: "bold" },
                                color: "#e11d48"
                            },
                            ticks: {
                                callback: val => `${val}%`
                            },
                            grid: {
                                color: "rgba(226, 232, 240, 0.6)"
                            }
                        },
                        yRating: {
                            type: "linear",
                            position: "right",
                            min: 1,
                            max: 5,
                            title: {
                                display: true,
                                text: "Rating (★)",
                                font: { size: 11, weight: "bold" },
                                color: "#d97706"
                            },
                            ticks: {
                                stepSize: 1
                            },
                            grid: { display: false }
                        }
                    }
                }
            });
        } catch (err) {
            console.error("Correlation chart error:", err);
        }
    }

    // 3. Render Issues Breakdown Doughnut Chart
    async function loadIssuesChart() {
        try {
            const res = await fetch("/api/analytics/top-issues");
            if (!res.ok) throw new Error("Failed to load issues breakdown");
            const data = await res.json();

            const labels = data.map(d => d.category_name);
            const counts = data.map(d => d.count);

            const palette = [
                "#10b981", // Great Taste (emerald)
                "#f43f5e", // Too Salty (rose)
                "#f97316", // Undercooked (orange)
                "#06b6d4", // Cold Food (cyan)
                "#ef4444", // Too Spicy (red)
                "#eab308", // Oily (yellow)
                "#64748b", // Bland (slate)
                "#8b5cf6"  // Small Portion (purple)
            ];

            const ctx = document.getElementById("issuesChart").getContext("2d");

            if (issuesChart) {
                issuesChart.destroy();
            }

            issuesChart = new Chart(ctx, {
                type: "doughnut",
                data: {
                    labels: labels,
                    datasets: [{
                        data: counts,
                        backgroundColor: palette.slice(0, labels.length),
                        borderWidth: 2,
                        borderColor: "#ffffff"
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: "68%",
                    plugins: {
                        legend: {
                            position: "right",
                            labels: {
                                boxWidth: 12,
                                padding: 10,
                                font: { size: 11 }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const val = context.parsed;
                                    const pct = ((val / total) * 100).toFixed(1);
                                    return ` ${context.label}: ${val} logs (${pct}%)`;
                                }
                            }
                        }
                    }
                }
            });
        } catch (err) {
            console.error("Issues chart error:", err);
        }
    }

    // 4. Render Lowest-Rated Meals Table
    async function loadLowestRatedMeals() {
        try {
            const res = await fetch("/api/analytics/lowest-rated-meals?limit=5");
            if (!res.ok) throw new Error("Failed to load lowest rated meals");
            const meals = await res.json();

            if (meals.length === 0) {
                lowestMealsTbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="px-6 py-6 text-center text-slate-400 text-xs">
                            No meal feedback data collected yet.
                        </td>
                    </tr>
                `;
                return;
            }

            lowestMealsTbody.innerHTML = "";

            meals.forEach((m) => {
                const tr = document.createElement("tr");
                tr.className = "hover:bg-slate-50 transition-colors";

                let ratingBadgeColor = m.avg_rating < 2.5 
                    ? "bg-rose-100 text-rose-800 border-rose-200" 
                    : "bg-amber-100 text-amber-800 border-amber-200";

                tr.innerHTML = `
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="font-semibold text-slate-900">${m.meal_date}</div>
                        <div class="text-xs text-slate-400">${m.meal_session}</div>
                    </td>
                    <td class="px-6 py-4 max-w-xs">
                        <p class="font-medium text-slate-800 truncate" title="${m.menu_items}">${m.menu_items}</p>
                    </td>
                    <td class="px-6 py-4 text-center">
                        <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold border ${ratingBadgeColor}">
                            ★ ${m.avg_rating.toFixed(1)}
                        </span>
                    </td>
                    <td class="px-6 py-4 text-center text-xs font-semibold text-slate-600">
                        ${m.review_count} reviews
                    </td>
                    <td class="px-6 py-4 text-center">
                        <span class="text-xs font-bold text-rose-600">${m.waste_percentage.toFixed(1)}%</span>
                    </td>
                    <td class="px-6 py-4">
                        <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold bg-amber-50 text-amber-900 border border-amber-200">
                            💡 ${m.action_recommendation}
                        </span>
                    </td>
                `;
                lowestMealsTbody.appendChild(tr);
            });
        } catch (err) {
            console.error("Lowest meals error:", err);
            lowestMealsTbody.innerHTML = `
                <tr>
                    <td colspan="6" class="px-6 py-4 text-center text-rose-500 text-xs font-medium">
                        Failed to load ranked table: ${err.message}
                    </td>
                </tr>
            `;
        }
    }

    // 5. Live Math & Check-Constraint Validation for Waste Form
    function updateLiveWasteCalculation() {
        const prep = parseFloat(prepInput.value) || 0;
        const kitchen = parseFloat(kitchenInput.value) || 0;
        const scrap = parseFloat(scrapInput.value) || 0;

        const totalWaste = kitchen + scrap;
        liveTotalWasteEl.textContent = `${totalWaste.toFixed(1)} kg`;

        let wastePct = 0;
        if (prep > 0) {
            wastePct = (totalWaste / prep) * 100;
        }
        liveWastePctEl.textContent = `${wastePct.toFixed(1)}%`;

        // Constraint check: prepared >= kitchen + scrap
        if (prep > 0 && totalWaste > prep) {
            warningEl.classList.remove("hidden");
            submitWasteBtn.disabled = true;
            submitWasteBtn.classList.add("opacity-50", "cursor-not-allowed");
        } else {
            warningEl.classList.add("hidden");
            submitWasteBtn.disabled = false;
            submitWasteBtn.classList.remove("opacity-50", "cursor-not-allowed");
        }
    }

    [prepInput, kitchenInput, scrapInput].forEach(inp => {
        inp.addEventListener("input", updateLiveWasteCalculation);
    });

    // 6. Waste Form Submit Handler
    wasteForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const menuId = parseInt(menuSelect.value, 10);
        const prep = parseFloat(prepInput.value);
        const kitchen = parseFloat(kitchenInput.value);
        const scrap = parseFloat(scrapInput.value);

        if (!menuId) {
            showToast("Please choose a meal menu.", "error");
            return;
        }

        submitWasteBtn.disabled = true;
        submitWasteBtn.textContent = "Saving...";

        try {
            const res = await fetch("/api/waste", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    menu_id: menuId,
                    prepared_weight_kg: prep,
                    unconsumed_kitchen_waste_kg: kitchen,
                    plate_scrap_waste_kg: scrap
                })
            });

            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.detail || "Failed to record waste log.");
            }

            showToast("Waste log saved successfully!", "success");
            wasteForm.reset();
            updateLiveWasteCalculation();

            // Refresh dashboards
            loadKPIMetrics();
            loadCorrelationChart();
            loadIssuesChart();
            loadLowestRatedMeals();

        } catch (err) {
            showToast(err.message, "error");
        } finally {
            submitWasteBtn.disabled = false;
            submitWasteBtn.innerHTML = `
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                <span>Save Waste Log</span>
            `;
        }
    });

    // Refresh button
    refreshBtn.addEventListener("click", () => {
        loadKPIMetrics();
        loadCorrelationChart();
        loadIssuesChart();
        loadLowestRatedMeals();
        showToast("Dashboard metrics refreshed.", "success");
    });

    // Initial load
    loadKPIMetrics();
    loadCorrelationChart();
    loadIssuesChart();
    loadLowestRatedMeals();
});
