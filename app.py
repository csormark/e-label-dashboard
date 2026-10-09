import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet

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
            "to_worse": cp - 72,
        }

    else:
        return {
            "to_better": 72 - cp,
            "to_worse": 0,
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
            "to_worse": cp - 95,
        }

    else:
        return {
            "to_better": 95 - cp,
            "to_worse": 0,
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
            "to_worse": 74 - sound_db,
        }

    elif sound_db <= 74:

        return {
            "to_better": sound_db - 68,
            "to_worse": 77 - sound_db,
        }

    elif sound_db <= 77:

        return {
            "to_better": sound_db - 74,
            "to_worse": 78 - sound_db,
        }

    else:

        return {
            "to_better": sound_db - 77,
            "to_worse": 0,
        }

def energy_color(grade):

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

def performance_color(grade):

    colors = {
        "A": "#00A651",
        "B": "#8BC34A",
        "C": "#FFD54F",
        "D": "#FF7043",
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
            background:{performance_color(grade)};
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

def performance_map(
    title,
    current_dpu,
    current_debris,
    boundaries,
    x_range,
    y_range,
):
    fig, ax = plt.subplots(figsize=(8, 6))

    x = np.linspace(x_range[0], x_range[1], 200)

    region_colors = [
        "#e9e5c4",  # D
        "#eef0c5",  # C
        "#bfdcbf",  # B
        "#97d397",  # A
    ]

    y_top = y_range[1]
    y_bottom = y_range[0]

    y_c = (boundaries["C"] - 0.9 * x) / 0.1
    y_b = (boundaries["B"] - 0.9 * x) / 0.1
    y_a = (boundaries["A"] - 0.9 * x) / 0.1

    ax.fill_between(
        x, y_bottom, y_c,
        color=region_colors[0],
        alpha=0.8
    )

    ax.fill_between(
        x, y_c, y_b,
        color=region_colors[1],
        alpha=0.8
    )

    ax.fill_between(
        x, y_b, y_a,
        color=region_colors[2],
        alpha=0.8
    )

    ax.fill_between(
        x, y_a, y_top,
        color=region_colors[3],
        alpha=0.8
    )

    ax.plot(x, y_c, color="#f0b400", linewidth=2)
    ax.plot(x, y_b, color="#3ae000", linewidth=2)
    ax.plot(x, y_a, color="#00aa33", linewidth=2)

    ax.scatter(
        current_dpu,
        current_debris,
        marker="X",
        s=200,
        color="red",
        edgecolor="black",
        zorder=10,
        label="Current Product"
    )

    # -------------------------------------------------
    # Grade labels
    # -------------------------------------------------

    if boundaries["A"] == 106:

        # Hard Floor

        ax.text(
            96.0, 68, "D",
            fontsize=26,
            fontweight="bold",
            color="#ff5500"
        )

        ax.text(
            100.0, 68, "C",
            fontsize=26,
            fontweight="bold",
            color="#e0b000"
        )

        ax.text(
            104.0, 68, "B",
            fontsize=26,
            fontweight="bold",
            color="#7fc942"
        )

        ax.text(
            108.5, 68, "A",
            fontsize=26,
            fontweight="bold",
            color="#00aa00"
        )

    else:

        # Carpet

        ax.text(
            71.0, 68, "D",
            fontsize=26,
            fontweight="bold",
            color="#ff5500"
        )

        ax.text(
            75.5, 68, "C",
            fontsize=26,
            fontweight="bold",
            color="#e0b000"
        )

        ax.text(
            79.8, 68, "B",
            fontsize=26,
            fontweight="bold",
            color="#7fc942"
        )

        ax.text(
            84.2, 68, "A",
            fontsize=26,
            fontweight="bold",
            color="#00aa00"
        )

    # -------------------------------------------------
    # Plot formatting
    # -------------------------------------------------

    ax.set_title(
        title,
        fontsize=20,
        fontweight="bold"
    )

    ax.set_xlabel("Dust Pick-Up [%]")
    ax.set_ylabel("Debris Pick-Up [%]")

    ax.set_xlim(x_range)
    ax.set_ylim(y_range)

    ax.grid(True, alpha=0.3)

    ax.legend()

    return fig

# =====================================================
# PDF REPORT
# =====================================================


def create_pdf_report(
    power_type,
    eei,
    ae,
    cp_factor,
    grade,
    carpet_class,
    hardfloor_class,
    sound_class,
    cp_carpet,
    cp_hardfloor,
    sound_gp,
):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4
    )

    styles = getSampleStyleSheet()

    elements = []

    title = Paragraph(
        "Vacuum Cleaner E-Label Assessment Report",
        styles["Title"]
    )

    elements.append(title)

    elements.append(Spacer(1, 12))

    summary_data = [
        ["Metric", "Value"],
        ["Product Type", power_type],
        ["Energy Class", grade],
        ["EEI", f"{eei:.1f}"],
        ["AE", f"{ae:.1f} kWh/a"],
        ["CP Factor", f"{cp_factor:.6f}"],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[200, 200]
    )

    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )

    elements.append(summary_table)

    elements.append(Spacer(1, 15))

    grades_data = [
        ["Category", "Grade", "Value"],
        ["Carpet", carpet_class, f"{cp_carpet:.1f}"],
        ["Hard Floor", hardfloor_class, f"{cp_hardfloor:.1f}"],
        ["Sound", sound_class, f"{sound_gp:.1f} dBA"],
    ]

    grades_table = Table(
        grades_data,
        colWidths=[150, 100, 150]
    )

    grades_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )

    elements.append(
        Paragraph(
            "Performance Summary",
            styles["Heading2"]
        )
    )

    elements.append(grades_table)

    elements.append(Spacer(1, 15))

    elements.append(
        Paragraph(
            f"""
            Current Energy Class: <b>{grade}</b><br/>
            EEI: <b>{eei:.1f}</b><br/>
            Annual Energy Consumption: <b>{ae:.1f} kWh/a</b><br/>
            CP Factor: <b>{cp_factor:.6f}</b>
            """,
            styles["BodyText"]
        )
    )

    doc.build(elements)

    pdf = buffer.getvalue()

    buffer.close()

    return pdf

    # -------------------------------------------------
    # Grade labels
    # -------------------------------------------------

    if boundaries["A"] == 106:
        # Hard Floor

        ax.text(
            96.0,
            68,
            "D",
            fontsize=26,
            fontweight="bold",
            color="#ff5500"
        )

        ax.text(
            100.0,
            68,
            "C",
            fontsize=26,
            fontweight="bold",
            color="#e0b000"
        )

        ax.text(
            104.0,
            68,
            "B",
            fontsize=26,
            fontweight="bold",
            color="#7fc942"
        )

        ax.text(
            108.5,
            68,
            "A",
            fontsize=26,
            fontweight="bold",
            color="#00aa00"
        )

    else:
        # Carpet

        ax.text(
            71.0,
            68,
            "D",
            fontsize=26,
            fontweight="bold",
            color="#ff5500"
        )

        ax.text(
            75.5,
            68,
            "C",
            fontsize=26,
            fontweight="bold",
            color="#e0b000"
        )

        ax.text(
            79.8,
            68,
            "B",
            fontsize=26,
            fontweight="bold",
            color="#7fc942"
        )

        ax.text(
            84.2,
            68,
            "A",
            fontsize=26,
            fontweight="bold",
            color="#00aa00"
        )

    # -------------------------------------------------
    # Plot formatting
    # -------------------------------------------------

    ax.set_title(
        title,
        fontsize=20,
        fontweight="bold"
    )

    ax.set_xlabel("Dust Pick-Up [%]")
    ax.set_ylabel("Debris Pick-Up [%]")

    ax.set_xlim(x_range)
    ax.set_ylim(y_range)

    ax.grid(True, alpha=0.3)

    ax.legend()

    return fig

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

  c1, c2, c3 = st.columns(3)

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

with c3:

        dcpm_power = st.number_input(
            "DCPM Power [W]",
            value=10,
            step=1
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
        "MFU power Carpet [W]",
        0,
        750,
        400
    )

    if power_type == "Cordless":

        nozzle_carpet = st.slider(
            "Nozzle power Carpet [W]",
            0,
            100,
            50
        )

    else:

        nozzle_carpet = 0

        st.slider(
            "Nozzle power Carpet [W]",
            0,
            100,
            0,
            disabled=True
        )


    clogging_carpet = (
        st.slider(
            "Clogging Carpet [%]",
            0,
            50,
            10,
            help="""Input power added on carpet due to clogging performance drop"""
        ) / 100
    )
    
    dpu_carpet = (
        st.slider(
            "Dust Pick-Up on Carpet [%]",
            70,
            100,
            75,
            help="""3 DS dust removal from Wilton carpet"""
        ) / 100
    )

    debris_carpet = (
        st.slider(
            "Debris Pick-Up Carpet [%]",
            45,
            100,
            80,
            help="""3 DS FS/BS average debris pick up on carpet"""
        ) / 100
    )

with p2:

    st.subheader("Hard Floor")

    mfu_hardfloor = st.slider(
        "MFU power Hard Floor [W]",
        0,
        750,
        400
    )

    if power_type == "Cordless":

        nozzle_hardfloor = st.slider(
            "Nozzle power Hard Floor [W]",
            0,
            100,
            10
        )

    else:

        nozzle_hardfloor = 0

        st.slider(
            "Nozzle power Hard Floor [W]",
            0,
            100,
            0,
            disabled=True
        )


    clogging_hardfloor = (
        st.slider(
            "Clogging Hard Floor [%]",
            0,
            50,
            10,
            help="""Input power added on hardfloor due to clogging performance drop"""
        ) / 100
    )

    dpu_hardfloor = (
        st.slider(
            "Dust Pick-Up Hard Floor [%]",
            95,
            115,
            105,
            help="""3 DS dust removal from crevice"""
        ) / 100
    )

    debris_hardfloor = (
        st.slider(
            "Debris Pick-Up Hard Floor [%]",
            45,
            100,
            80,
            help="""3 DS FS/BS average debris pick up on hardfloor"""
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
    dcpm_power,
    clogging_carpet,
    charger_efficiency,
    battery_efficiency,
)

power_hardfloor = calculate_power(
    mfu_hardfloor,
    nozzle_hardfloor,
    dcpm_power,
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
# AE COMPLIANCE CHECK
# =====================================================

if ae > 36:

    st.error(
        f"❌ Annual Energy Consumption exceeds SAE limit. "
        f"AE = {ae:.1f} kWh/year (Limit = 36.0)"
    )

elif ae > 33:

    st.warning(
        f"⚠️ Annual Energy Consumption is approaching the SAE limit. "
        f"AE = {ae:.1f} kWh/year (Limit = 36.0)"
    )


# =====================================================
# PERFORMANCE VALUES
# =====================================================

st.subheader("Performance Values")

p1, p2, p3 = st.columns(3)

with p1:
    st.metric(
        "CP Carpet",
        f"{cp_carpet:.1f} %"
    )


with p2:
    st.metric(
        "CP Hard Floor",
        f"{cp_hardfloor:.1f} %",
    )

with p3:
    st.metric(
        "Sound Power",
        f"{sound_gp:.1f} dBA",
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
# PERFORMANCE MAPS
# =====================================================

st.header("Performance Maps")

c1, c2 = st.columns(2)

with c1:

    carpet_fig = performance_map(
        title="Carpet Performance Grade",
        current_dpu=dpu_carpet * 100,
        current_debris=debris_carpet * 100,
        boundaries={
            "A": 81,
            "B": 77,
            "C": 72,
        },
        x_range=(70, 86),
        y_range=(45, 100),
    )

    st.pyplot(carpet_fig)

with c2:

    hardfloor_fig = performance_map(
        title="Hard Floor Performance Grade",
        current_dpu=dpu_hardfloor * 100,
        current_debris=debris_hardfloor * 100,
        boundaries={
            "A": 106,
            "B": 101,
            "C": 95,
        },
        x_range=(95, 115),
        y_range=(45, 100),
    )

    st.pyplot(hardfloor_fig)


## GENERATE REPORT

pdf_report = create_pdf_report(
    power_type=power_type,
    eei=eei,
    ae=ae,
    cp_factor=cp_factor,
    grade=grade,
    carpet_class=carpet_class,
    hardfloor_class=hardfloor_class,
    sound_class=sound_class,
    cp_carpet=cp_carpet,
    cp_hardfloor=cp_hardfloor,
    sound_gp=sound_gp,
)

st.subheader("Export")

st.download_button(
    label="📄 Download PDF Report",
    data=pdf_report,
    file_name="e_label_report.pdf",
    mime="application/pdf"
)

# =====================================================
# CALCULATION CONSTANTS
# =====================================================

with st.expander("Calculation Constants"):

    st.markdown("""
### Energy and Performance Constants

- **General Purpose weighting**
  - Hard Floor: **75%**
  - Carpet: **25%**

- **Cleaning Performance weighting**
  - Dust Pick-Up (DPU): **90%**
  - Debris Pick-Up: **10%**

- **Standard Annual Energy (SAE)**
  - **36 kWh/year**

- **Minimum Cleaning Performance Reference (CPmin)**
  - **0.84375**
  - Corresponds to:
    - Debris Carpet: **45%**
    - Debris Hard Floor: **45%**
    - DPU Carpet: **70%**
    - DPU Hard Floor: **95%**

### Key Equations

**CP Carpet**

CPc = (0.9 × DPUc + 0.1 × DEBc) × 100

**CP Hard Floor**

CPhf = (0.9 × DPUhf + 0.1 × DEBhf) × 100

**CP General Purpose**

CPgp = (0.25 × CPc + 0.75 × CPhf) / 100

**CP Factor**

CPfactor = 0.84375 / (0.66 × 0.84375 + 0.33 × CPgp)

**EEI**

EEI = (AE / 36) × CPfactor × 100
""")

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
    Version 0.9.3 | Last updated: 2026-10-09

    Author: Christoffer Sörmark
    """
)