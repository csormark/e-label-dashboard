import streamlit as st

from calculations import (
    calculate_power,
    calculate_eon,
    calculate_eaux,
    calculate_emaint,
    calculate_ae,
    calculate_cp_carpet,
    calculate_cp_hardfloor,
    calculate_cpgp,
    calculate_cp_factor,
    calculate_eei,
    calculate_sound_gp,
    energy_grade,
)

# =====================================================
# HELPERS
# =====================================================

def carpet_grade(cp):

    if cp >= 81:
        return "A"
    elif cp >= 77:
        return "B"
    elif cp >= 72:
        return "C"
    else:
        return "D"

def carpet_margins(cp):

    if cp >= 81:
        return {
            "to_better": 0,
            "to_worse": cp - 77,
        }

    elif cp >= 77:
        return {
            "to_better": 81 - cp,
            "to_worse": cp - 72,
        }

    elif cp >= 72:
        return {
            "to_better": 77 - cp,
            "to_worse": cp,
        }

    else:
        return {
            "to_better": 72 - cp,
            "to_worse": cp,
        }


def hardfloor_grade(cp):

    if cp >= 106:
        return "A"
    elif cp >= 101:
        return "B"
    elif cp >= 95:
        return "C"
    else:
        return "D"

def hardfloor_margins(cp):

    if cp >= 106:
        return {
            "to_better": 0,
            "to_worse": cp - 101,
        }

    elif cp >= 101:
        return {
            "to_better": 106 - cp,
            "to_worse": cp - 95,
        }

    elif cp >= 95:
        return {
            "to_better": 101 - cp,
            "to_worse": cp,
        }

    else:
        return {
            "to_better": 95 - cp,
            "to_worse": cp,
        }


def sound_grade(sound_db):

    if sound_db <= 68:
        return "A"
    elif sound_db <= 74:
        return "B"
    elif sound_db <= 77:
        return "C"
    else:
        return "D"

def sound_margins(sound_db):

    if sound_db <= 68:

        return {
            "to_better": 0,
            "to_worse": 68 - sound_db,
        }

    elif sound_db <= 74:

        return {
            "to_better": sound_db - 68,
            "to_worse": 74 - sound_db,
        }

    elif sound_db <= 77:

        return {
            "to_better": sound_db - 74,
            "to_worse": 77 - sound_db,
        }

    else:

        return {
            "to_better": sound_db - 77,
            "to_worse": 0,
        }


def grade_color(grade):

    colors = {
        "A": "#00A651",
        "B": "#4CAF50",
        "C": "#8BC34A",
        "D": "#FFD54F",
        "E": "#FFB74D",
        "F": "#FF7043",
        "G": "#D32F2F",
    }

    return colors.get(grade, "#808080")

def eei_margins(eei):

    bands = [
        ("A", 0, 30),
        ("B", 30, 42),
        ("C", 42, 54),
        ("D", 54, 66),
        ("E", 66, 78),
        ("F", 78, 90),
        ("G", 90, 999),
    ]

    for grade, lower, upper in bands:

        if lower <= eei < upper:

            return {
                "current": grade,
                "better": None if grade == "A" else lower,
                "worse": upper,
                "to_better": 0 if grade == "A" else eei - lower,
                "to_worse": upper - eei,
            }


def grade_card(title, grade):

    st.markdown(
        f"""
        <div style="
            background:{grade_color(grade)};
            color:white;
            border-radius:12px;
            padding:20px;
            text-align:center;
        ">
            <div style="font-size:18px;">
                {title}
            </div>
            <div style="
                font-size:48px;
                font-weight:bold;
            ">
                {grade}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def energy_grade_gauge(active_grade):

    grades = ["A", "B", "C", "D", "E", "F", "G"]

    colors = {
        "A": "#00A651",
        "B": "#4CAF50",
        "C": "#8BC34A",
        "D": "#FFD54F",
        "E": "#FFB74D",
        "F": "#FF7043",
        "G": "#D32F2F",
    }

    cols = st.columns(7)

    for col, current_grade in zip(cols, grades):

        with col:

            border = (
                "4px solid black"
                if current_grade == active_grade
                else "1px solid white"
            )

            st.markdown(
                f"""
                <div style="
                    background:{colors[current_grade]};
                    color:white;
                    text-align:center;
                    padding:10px;
                    border-radius:6px;
                    font-size:24px;
                    font-weight:bold;
                    border:{border};
                ">
                    {current_grade}
                </div>
                """,
                unsafe_allow_html=True,
            )


# =====================================================
# PRODUCT TYPE
# =====================================================

power_type = st.segmented_control(
    "Product Type",
    options=["Cordless", "Corded"],
    default="Cordless"
)

# =====================================================
# HEADER
# =====================================================

st.title("Vacuum Cleaner E-Label Dashboard")

st.divider()

# =====================================================
# GENERAL SETTINGS
# =====================================================

with st.expander("General Settings", expanded=True):

    c1, c2 = st.columns(2)

    with c1:

        nozzle_width = st.number_input(
            "Nozzle Width [mm]",
            value=250 if power_type == "Cordless" else 280
        )

    with c2:

        if power_type == "Cordless":

            maintenance_power = st.number_input(
                "Maintenance Power [W]",
                value=0.3,
                step=0.1
            )

        else:

            maintenance_power = 0.0

            st.number_input(
                "Maintenance Power [W]",
                value=0.0,
                disabled=True
            )

# =====================================================
# BATTERY
# =====================================================

if power_type == "Cordless":

    b1, b2 = st.columns(2)

    with b1:

        battery_efficiency = st.number_input(
            "Battery Efficiency",
            value=0.90,
            step=0.01
        )

    with b2:

        charger_efficiency = st.number_input(
            "Charger Efficiency",
            value=0.90,
            step=0.01
        )

else:

    battery_efficiency = 1.0
    charger_efficiency = 1.0

# =====================================================
# PERFORMANCE INPUTS
# =====================================================

p1, p2 = st.columns(2)

with p1:

    st.subheader("Carpet")

    mfu_carpet = st.slider(
        "MFU Carpet",
        0,
        1000,
        400
    )

    if power_type == "Cordless":

        nozzle_carpet = st.slider(
            "Nozzle Carpet",
            0,
            300,
            50
        )

    else:

        nozzle_carpet = 0

        st.slider(
            "Nozzle Carpet",
            0,
            300,
            0,
            disabled=True
        )

    dcpm_carpet = st.slider(
        "DCPM Carpet",
        0,
        100,
        10
    )

    clogging_carpet = (
        st.slider(
            "Clogging Carpet (%)",
            0,
            100,
            10
        ) / 100
    )

    dpu_carpet = (
        st.slider(
            "Dust Pick-Up Carpet (%)",
            70,
            100,
            80
        ) / 100
    )

    debris_carpet = (
        st.slider(
            "Debris Pick-Up Carpet (%)",
            45,
            100,
            90
        ) / 100
    )

with p2:

    st.subheader("Hard Floor")

    mfu_hardfloor = st.slider(
        "MFU Hard Floor",
        0,
        1000,
        280
    )

    if power_type == "Cordless":

        nozzle_hardfloor = st.slider(
            "Nozzle Hard Floor",
            0,
            300,
            10
        )

    else:

        nozzle_hardfloor = 0

        st.slider(
            "Nozzle Hard Floor",
            0,
            300,
            0,
            disabled=True
        )

    dcpm_hardfloor = st.slider(
        "DCPM Hard Floor",
        0,
        100,
        10
    )

    clogging_hardfloor = (
        st.slider(
            "Clogging Hard Floor (%)",
            0,
            100,
            0
        ) / 100
    )

    dpu_hardfloor = (
        st.slider(
            "Dust Pick-Up Hard Floor (%)",
            95,
            115,
            105
        ) / 100
    )

    debris_hardfloor = (
        st.slider(
            "Debris Pick-Up Hard Floor (%)",
            45,
            100,
            90
        ) / 100
    )


# =====================================================
# SOUND
# =====================================================

s1, s2 = st.columns(2)

with s1:

    sound_carpet = st.number_input(
        "Sound Carpet [dBA]",
        value=57
    )

with s2:

    sound_hardfloor = st.number_input(
        "Sound Hard Floor [dBA]",
        value=70
    )

# =====================================================
# CALCULATIONS
# =====================================================

power_carpet = calculate_power(
    mfu_carpet,
    nozzle_carpet,
    dcpm_carpet,
    clogging_carpet,
    charger_efficiency,
    battery_efficiency,
)

power_hardfloor = calculate_power(
    mfu_hardfloor,
    nozzle_hardfloor,
    dcpm_hardfloor,
    clogging_hardfloor,
    charger_efficiency,
    battery_efficiency,
)

eon = calculate_eon(
    power_carpet,
    power_hardfloor,
    nozzle_width,
)

eaux = calculate_eaux()

emaint = calculate_emaint(
    maintenance_power
)

ae = calculate_ae(
    eon,
    eaux,
    emaint,
)

cp_carpet = calculate_cp_carpet(
    dpu_carpet,
    debris_carpet
)

cp_hardfloor = calculate_cp_hardfloor(
    dpu_hardfloor,
    debris_hardfloor
)

cpgp = calculate_cpgp(
    cp_carpet,
    cp_hardfloor
)

cp_factor = calculate_cp_factor(
    cpgp
)

eei = calculate_eei(
    ae,
    cp_factor
)

grade = energy_grade(
    eei
)

sound_gp = calculate_sound_gp(
    sound_carpet,
    sound_hardfloor
)

carpet_class = carpet_grade(cp_carpet)
hardfloor_class = hardfloor_grade(cp_hardfloor)
sound_class = sound_grade(sound_gp)
eei_margin = eei_margins(eei)
carpet_margin = carpet_margins(cp_carpet)
hardfloor_margin = hardfloor_margins(cp_hardfloor)
sound_margin = sound_margins(sound_gp)

# =====================================================
# RESULTS
# =====================================================

st.header("Results")

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        "EEI",
        f"{eei:.1f}"
    )

with k2:
    st.metric(
        "AE",
        f"{ae:.1f}"
    )

with k3:
    st.metric(
        "CP Factor",
        f"{cp_factor:.6f}"
    )

with k4:
    st.metric(
        "Energy Class",
        grade
    )

# =====================================================
# PERFORMANCE VALUES
# =====================================================

st.subheader("Performance Values")

p1, p2, p3 = st.columns(3)

with p1:
    st.metric(
        "CP Carpet (Grade A)",
        f"{cp_carpet:.1f}"
    )


with p2:
    st.metric(
        "CP Hard Floor",
        f"{cp_hardfloor:.1f}",
    )

with p3:
    st.metric(
        "Sound Power",
        f"{sound_gp:.1f} dBA",
    )


# =====================================================
# PERFORMANCE GRADES
# =====================================================

st.subheader("Performance Grades")

g1, g2, g3 = st.columns(3)

with g1:

    grade_card(
        "Carpet",
        carpet_class
    )

    st.caption(
        f"Margin to lower grade: {carpet_margin['to_worse']:.1f}"
    )

    if carpet_class != "A":
        st.caption(
            f"Needed for next grade: {carpet_margin['to_better']:.1f}"
        )

with g2:

    grade_card(
        "Hard Floor",
        hardfloor_class
    )

    st.caption(
        f"Margin to lower grade: {hardfloor_margin['to_worse']:.1f}"
    )

    if hardfloor_class != "A":
        st.caption(
            f"Needed for next grade: {hardfloor_margin['to_better']:.1f}"
        )


with g3:

    grade_card(
        "Sound",
        sound_class
    )

    st.caption(
        f"Margin to worse grade: {sound_margin['to_worse']:.1f}"
    )

    if sound_class != "A":

        st.caption(
            f"Reduction needed for next grade: {sound_margin['to_better']:.1f} dBA"
        )

# =====================================================
# ENERGY LABEL RATING
# =====================================================

st.subheader("Energy Label Rating")

energy_grade_gauge(grade)

m1, m2 = st.columns(2)

with m1:

    st.metric(
        "Margin to worse grade",
        f"{eei_margin['to_worse']:.2f}"
    )

with m2:

    if grade != "A":

        st.metric(
            "Improvement needed for better grade",
            f"{eei_margin['to_better']:.2f}"
        )

st.markdown("")

st.metric(
    "Current Energy Class",
    grade
)

st.markdown(
    f"""
**Energy Efficiency Index (EEI):** {eei:.1f}

**Annual Energy Consumption (AE):** {ae:.1f} kWh/a

**Carpet Cleaning Performance:** {cp_carpet:.1f} ({carpet_class})

**Hard Floor Cleaning Performance:** {cp_hardfloor:.1f} ({hardfloor_class})

**Sound Power:** {sound_gp:.1f} dBA ({sound_class})

**CP Factor:** {cp_factor:.6f}
"""
)

# =====================================================
# TECHNICAL DETAILS
# =====================================================

with st.expander("Technical Details"):

    st.json({
        "AE": round(ae, 2),
        "EEI": round(eei, 2),
        "CP Carpet": round(cp_carpet, 2),
        "CP Hard Floor": round(cp_hardfloor, 2),
        "CP GP": round(cpgp, 5),
        "CP Factor": round(cp_factor, 8),
        "Sound GP": round(sound_gp, 2),
    })

st.info(
    """
    Version 0.9.0 | Last updated: 2026-10-08

    Author: Christoffer Sörmark
    """
)