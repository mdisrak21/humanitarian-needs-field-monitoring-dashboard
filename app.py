import streamlit as st
import pandas as pd
import plotly.express as px

from database import (
    initialize_database,
    seed_data,
    get_assessments,
    add_assessment,
    delete_assessment
)


st.set_page_config(
    page_title="Humanitarian Needs & Field Monitoring Dashboard",
    page_icon="🌍",
    layout="wide"
)

initialize_database()
seed_data()

data = pd.DataFrame(get_assessments())

if not data.empty:
    data["assessment_date"] = pd.to_datetime(
        data["assessment_date"]
    )


# =========================================================
# HELPERS
# =========================================================

def calculate_sector_totals(df):

    return {
        "Food": int(df["food_need"].sum()),
        "Water": int(df["water_need"].sum()),
        "Health": int(df["health_need"].sum()),
        "Shelter": int(df["shelter_need"].sum()),
        "Education": int(df["education_need"].sum())
    }


def calculate_priority_score(row):

    sector_need = (
        row["food_need"]
        + row["water_need"]
        + row["health_need"]
        + row["shelter_need"]
        + row["education_need"]
    )

    population_score = min(
        row["affected_population"] / 20000 * 40,
        40
    )

    need_score = min(
        sector_need / 50000 * 40,
        40
    )

    vulnerability_score = min(
        (
            row["children"]
            + row["women"]
            + row["persons_with_disabilities"]
        )
        /
        max(row["affected_population"], 1)
        * 20,
        20
    )

    return round(
        population_score
        + need_score
        + vulnerability_score,
        1
    )


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🌍 Humanitarian Monitoring")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Field Assessment",
        "Priority Analysis",
        "Assistance Monitoring",
        "Reports"
    ]
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.title(
        "🌍 Humanitarian Needs & Field Monitoring Dashboard"
    )

    st.caption(
        "Decision-support dashboard for humanitarian "
        "needs assessment and field monitoring."
    )

    if data.empty:
        st.warning("No data available.")
        st.stop()

    st.sidebar.subheader("Dashboard Filters")

    districts = ["All"] + sorted(
        data["district"].unique().tolist()
    )

    selected_district = st.sidebar.selectbox(
        "District",
        districts
    )

    priorities = ["All"] + sorted(
        data["priority"].unique().tolist()
    )

    selected_priority = st.sidebar.selectbox(
        "Priority",
        priorities
    )

    filtered = data.copy()

    if selected_district != "All":

        filtered = filtered[
            filtered["district"]
            == selected_district
        ]

    if selected_priority != "All":

        filtered = filtered[
            filtered["priority"]
            == selected_priority
        ]

    total_population = int(
        filtered["affected_population"].sum()
    )

    total_children = int(
        filtered["children"].sum()
    )

    total_women = int(
        filtered["women"].sum()
    )

    total_pwid = int(
        filtered[
            "persons_with_disabilities"
        ].sum()
    )

    total_assistance = int(
        filtered["assistance_delivered"].sum()
    )

    high_priority = int(
        (
            filtered["priority"]
            == "High"
        ).sum()
    )

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric(
        "Affected Population",
        f"{total_population:,}"
    )

    col2.metric(
        "Children",
        f"{total_children:,}"
    )

    col3.metric(
        "Women",
        f"{total_women:,}"
    )

    col4.metric(
        "Persons with Disabilities",
        f"{total_pwid:,}"
    )

    col5.metric(
        "Assistance Delivered",
        f"{total_assistance:,}"
    )

    col6.metric(
        "High Priority",
        high_priority
    )

    st.divider()

    # -----------------------------------------------------
    # SECTOR NEEDS
    # -----------------------------------------------------

    st.subheader("🎯 Sector Needs")

    sector_totals = calculate_sector_totals(
        filtered
    )

    sector_df = pd.DataFrame({
        "Sector": list(
            sector_totals.keys()
        ),
        "People in Need": list(
            sector_totals.values()
        )
    })

    left, right = st.columns(2)

    with left:

        fig = px.bar(
            sector_df,
            x="Sector",
            y="People in Need",
            title="People in Need by Sector",
            text="People in Need"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:

        fig = px.pie(
            sector_df,
            names="Sector",
            values="People in Need",
            title="Sector Need Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.divider()

    # -----------------------------------------------------
    # DISTRICT ANALYSIS
    # -----------------------------------------------------

    st.subheader("📍 District Analysis")

    district_summary = (
        filtered.groupby("district")
        .agg(
            Affected_Population=(
                "affected_population",
                "sum"
            ),
            Assistance_Delivered=(
                "assistance_delivered",
                "sum"
            ),
            Assessments=(
                "id",
                "count"
            )
        )
        .reset_index()
    )

    district_summary["Coverage_%"] = (
        district_summary[
            "Assistance_Delivered"
        ]
        /
        district_summary[
            "Affected_Population"
        ]
        * 100
    ).round(1)

    st.dataframe(
        district_summary,
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------------------------
    # TREND
    # -----------------------------------------------------

    st.subheader("📈 Monitoring Trend")

    trend = (
        filtered.groupby(
            "assessment_date"
        )
        .agg(
            Affected_Population=(
                "affected_population",
                "sum"
            ),
            Assistance_Delivered=(
                "assistance_delivered",
                "sum"
            )
        )
        .reset_index()
    )

    fig = px.line(
        trend,
        x="assessment_date",
        y=[
            "Affected_Population",
            "Assistance_Delivered"
        ],
        markers=True,
        title="Needs vs Assistance"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# FIELD ASSESSMENT
# =========================================================

elif page == "Field Assessment":

    st.title("📝 Field Assessment")

    st.write(
        "Create and manage humanitarian field assessments."
    )

    with st.form(
        "new_assessment",
        clear_on_submit=True
    ):

        st.subheader("📍 Location")

        col1, col2, col3 = st.columns(3)

        with col1:

            assessment_date = st.date_input(
                "Assessment Date"
            )

        with col2:

            district = st.text_input(
                "District"
            )

        with col3:

            upazila = st.text_input(
                "Upazila"
            )

        st.subheader("👥 Population")

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            affected_population = st.number_input(
                "Affected Population",
                min_value=0,
                step=100
            )

        with col2:

            children = st.number_input(
                "Children",
                min_value=0,
                step=50
            )

        with col3:

            women = st.number_input(
                "Women",
                min_value=0,
                step=50
            )

        with col4:

            persons_with_disabilities = st.number_input(
                "Persons with Disabilities",
                min_value=0,
                step=10
            )

        st.subheader("🎯 Sector Needs")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:

            food_need = st.number_input(
                "Food",
                min_value=0,
                step=100
            )

        with col2:

            water_need = st.number_input(
                "Water",
                min_value=0,
                step=100
            )

        with col3:

            health_need = st.number_input(
                "Health",
                min_value=0,
                step=100
            )

        with col4:

            shelter_need = st.number_input(
                "Shelter",
                min_value=0,
                step=100
            )

        with col5:

            education_need = st.number_input(
                "Education",
                min_value=0,
                step=100
            )

        st.subheader("📦 Assistance")

        assistance_delivered = st.number_input(
            "Assistance Delivered",
            min_value=0,
            step=100
        )

        priority = st.selectbox(
            "Priority",
            [
                "High",
                "Medium",
                "Low"
            ]
        )

        submit = st.form_submit_button(
            "➕ Save Assessment"
        )

        if submit:

            if not district.strip():

                st.error(
                    "District is required."
                )

            elif not upazila.strip():

                st.error(
                    "Upazila is required."
                )

            elif affected_population <= 0:

                st.error(
                    "Affected population must be greater than zero."
                )

            else:

                add_assessment(
                    str(assessment_date),
                    district.strip(),
                    upazila.strip(),
                    affected_population,
                    children,
                    women,
                    persons_with_disabilities,
                    food_need,
                    water_need,
                    health_need,
                    shelter_need,
                    education_need,
                    assistance_delivered,
                    priority
                )

                st.success(
                    "Assessment saved successfully."
                )

                st.rerun()

    st.divider()

    st.subheader(
        "🗂️ Existing Assessments"
    )

    st.dataframe(
        data[
            [
                "id",
                "assessment_date",
                "district",
                "upazila",
                "affected_population",
                "priority"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# PRIORITY ANALYSIS
# =========================================================

elif page == "Priority Analysis":

    st.title(
        "🚨 Humanitarian Priority Analysis"
    )

    priority_data = data.copy()

    priority_data[
        "Priority Score"
    ] = priority_data.apply(
        calculate_priority_score,
        axis=1
    )

    priority_data["Calculated Priority"] = (
        priority_data["Priority Score"]
        .apply(
            lambda score:
                "Critical"
                if score >= 70
                else
                "High"
                if score >= 50
                else
                "Medium"
                if score >= 30
                else
                "Low"
        )
    )

    priority_data = priority_data.sort_values(
        "Priority Score",
        ascending=False
    )

    st.subheader(
        "Priority Ranking"
    )

    display_priority = priority_data[
        [
            "district",
            "upazila",
            "affected_population",
            "food_need",
            "water_need",
            "health_need",
            "shelter_need",
            "education_need",
            "Priority Score",
            "Calculated Priority"
        ]
    ]

    st.dataframe(
        display_priority,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    left, right = st.columns(2)

    with left:

        fig = px.bar(
            priority_data.head(10),
            x="upazila",
            y="Priority Score",
            title="Top Priority Locations",
            text="Priority Score"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:

        calculated = (
            priority_data[
                "Calculated Priority"
            ]
            .value_counts()
            .reset_index()
        )

        calculated.columns = [
            "Priority",
            "Locations"
        ]

        fig = px.pie(
            calculated,
            names="Priority",
            values="Locations",
            title="Calculated Priority Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.info(
        "Priority score is a portfolio demonstration metric "
        "based on affected population, sector needs and "
        "vulnerability indicators."
    )


# =========================================================
# ASSISTANCE MONITORING
# =========================================================

elif page == "Assistance Monitoring":

    st.title(
        "📦 Assistance Monitoring"
    )

    total_need = int(
        data[
            [
                "food_need",
                "water_need",
                "health_need",
                "shelter_need",
                "education_need"
            ]
        ].sum().sum()
    )

    total_assistance = int(
        data[
            "assistance_delivered"
        ].sum()
    )

    remaining_gap = max(
        total_need - total_assistance,
        0
    )

    coverage = (
        total_assistance
        /
        total_need
        *
        100
        if total_need > 0
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Needs",
        f"{total_need:,}"
    )

    col2.metric(
        "Delivered",
        f"{total_assistance:,}"
    )

    col3.metric(
        "Remaining Gap",
        f"{remaining_gap:,}"
    )

    col4.metric(
        "Coverage",
        f"{coverage:.1f}%"
    )

    st.divider()

    assistance_df = pd.DataFrame({
        "Category": [
            "Total Needs",
            "Assistance Delivered",
            "Remaining Gap"
        ],
        "Population": [
            total_need,
            total_assistance,
            remaining_gap
        ]
    })

    fig = px.bar(
        assistance_df,
        x="Category",
        y="Population",
        title="Assistance Coverage",
        text="Population"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader(
        "📍 District Assistance Coverage"
    )

    district_assistance = (
        data.groupby("district")
        .agg(
            Affected_Population=(
                "affected_population",
                "sum"
            ),
            Assistance_Delivered=(
                "assistance_delivered",
                "sum"
            )
        )
        .reset_index()
    )

    district_assistance["Coverage_%"] = (
        district_assistance[
            "Assistance_Delivered"
        ]
        /
        district_assistance[
            "Affected_Population"
        ]
        *
        100
    ).round(1)

    st.dataframe(
        district_assistance,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# REPORTS
# =========================================================

elif page == "Reports":

    st.title(
        "📑 Humanitarian Monitoring Reports"
    )

    total_population = int(
        data[
            "affected_population"
        ].sum()
    )

    total_assistance = int(
        data[
            "assistance_delivered"
        ].sum()
    )

    high_priority = int(
        (
            data["priority"]
            == "High"
        ).sum()
    )

    st.subheader(
        "Executive Summary"
    )

    st.write(
        f"Total assessed affected population: "
        f"**{total_population:,}**"
    )

    st.write(
        f"Total assistance recorded: "
        f"**{total_assistance:,}**"
    )

    st.write(
        f"High-priority assessment areas: "
        f"**{high_priority}**"
    )

    st.divider()

    report = (
        data.groupby("district")
        .agg(
            Assessments=(
                "id",
                "count"
            ),
            Affected_Population=(
                "affected_population",
                "sum"
            ),
            Assistance_Delivered=(
                "assistance_delivered",
                "sum"
            ),
            High_Priority=(
                "priority",
                lambda x:
                    (x == "High").sum()
            )
        )
        .reset_index()
    )

    report["Coverage_%"] = (
        report[
            "Assistance_Delivered"
        ]
        /
        report[
            "Affected_Population"
        ]
        *
        100
    ).round(1)

    st.subheader(
        "District Monitoring Report"
    )

    st.dataframe(
        report,
        use_container_width=True,
        hide_index=True
    )

    report_csv = report.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "📥 Download District Report",
        data=report_csv,
        file_name="humanitarian_district_report.csv",
        mime="text/csv"
    )

    st.divider()

    full_csv = data.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "📥 Download Full Assessment Data",
        data=full_csv,
        file_name="humanitarian_assessment_data.csv",
        mime="text/csv"
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "⚠️ Synthetic data only — created for educational "
    "and portfolio purposes. No real beneficiary or "
    "refugee personal information is used."
)