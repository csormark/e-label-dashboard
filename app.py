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
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image


from datetime import datetime

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
    current_x,
    current_y,
    boundaries,
    x_range,
    y_range,
    x_label,
    y_label,
    x_weight,
    y_weight,
    label_positions,
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

    y_c = (boundaries["C"] - x_weight * x) / y_weight
    y_b = (boundaries["B"] - x_weight * x) / y_weight
    y_a = (boundaries["A"] - x_weight * x) / y_weight

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
        current_x,
        current_y,
        marker="X",
        s=200,
        color="red",
        edgecolor="black",
        zorder=10,
        label="Current Product"
    )

    # ---------------------------------------------
    # Grade labels
    # ---------------------------------------------

    for grade, (x_pos, y_pos) in label_positions.items():

        grade_colors = {
            "A": "#00aa00",
            "B": "#7fc942",
            "C": "#e0b000",
            "D": "#ff5500",
        }

        ax.text(
            x_pos,
            y_pos,
            grade,
            fontsize=26,
            fontweight="bold",
            color=grade_colors[grade]
        )

    ax.set_title(
        title,
        fontsize=20,
        fontweight="bold"
    )

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    ax.set_xlim(x_range)
    ax.set_ylim(y_range)

    ax.grid(True, alpha=0.3)

    ax.legend()

    return fig

def sound_map(
    sound_carpet,
    sound_hardfloor,
):

    fig, ax = plt.subplots(figsize=(10, 8))

    x = np.linspace(55, 85, 200)

    y_a = (68 - 0.75 * x) / 0.25
    y_b = (74 - 0.75 * x) / 0.25
    y_c = (77 - 0.75 * x) / 0.25

    ax.fill_between(
        x,
        55,
        y_a,
        color="#97d397",    # A
        alpha=0.8,
    )

    ax.fill_between(
        x,
        y_a,
        y_b,
        color="#bfdcbf",    # B
        alpha=0.8,
    )

    ax.fill_between(
        x,
        y_b,
        y_c,
        color="#eef0c5",    # C
        alpha=0.8,
    )

    ax.fill_between(
        x,
        y_c,
        85,
        color="#e9e5c4",    # D
        alpha=0.8,
    )

    ax.plot(x, y_a, color="#00aa33", linewidth=3)
    ax.plot(x, y_b, color="#3ae000", linewidth=3)
    ax.plot(x, y_c, color="#f0b400", linewidth=3)

    ax.scatter(
        sound_hardfloor,
        sound_carpet,
        color="red",
        marker="X",
        s=250,
        edgecolor="black",
        zorder=10,
        label="Current Product",
    )

    # Grade labels

    ax.text(
        62.5,
        70,
        "A",
        fontsize=28,
        fontweight="bold",
        color="#00aa33",
    )

    ax.text(
        72,
        70,
        "B",
        fontsize=28,
        fontweight="bold",
        color="#7fc942",
    )

    ax.text(
        77,
        70,
        "C",
        fontsize=28,
        fontweight="bold",
        color="#d4aa00",
    )

    ax.text(
        82,
        70,
        "D",
        fontsize=28,
        fontweight="bold",
        color="#ff5500",
    )

    ax.set_title(
        "Sound Grade",
        fontsize=20,
        fontweight="bold",
    )

    ax.set_xlabel(
        "Hard Floor Sound [dBA]"
    )

    ax.set_ylabel(
        "Carpet Sound [dBA]"
    )

    ax.set_xlim(55, 85)
    ax.set_ylim(55, 85)

    ax.grid(True, alpha=0.3)

    ax.legend()

    return fig

# =====================================================
# PDF REPORT
# =====================================================



def report_grade_color(grade):

    colors_map = {
        "A": colors.HexColor("#00A651"),
        "B": colors.HexColor("#8BC34A"),
        "C": colors.HexColor("#FFD54F"),
        "D": colors.HexColor("#FF7043"),
        "E": colors.HexColor("#FFB74D"),
        "F": colors.HexColor("#FF7043"),
        "G": colors.HexColor("#D32F2F"),
    }

    return colors_map.get(
        grade,
        colors.lightgrey
    )


def create_pdf_report(

    platform_name,
    model_name,
    model_code,
    report_by,
    info_field,
    comments,

    power_type,

    nozzle_width,
    maintenance_power,
    dcpm_power,

    battery_efficiency,
    charger_efficiency,

    mfu_carpet,
    nozzle_carpet,
    clogging_carpet,
    dpu_carpet,
    debris_carpet,
    sound_carpet,

    mfu_hardfloor,
    nozzle_hardfloor,
    clogging_hardfloor,
    dpu_hardfloor,
    debris_hardfloor,
    sound_hardfloor,

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

    # =================================================
    # TITLE
    # =================================================

    elements.append(
        Paragraph(
            "Vacuum Cleaner E-Label Assessment Report",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            datetime.now().strftime(
                "Generated: %Y-%m-%d %H:%M"
            ),
            styles["BodyText"]
        )
    )

    elements.append(Spacer(1, 12))

    # =================================================
    # CONCEPT INFORMATION
    # =================================================

    elements.append(
        Paragraph(
            "Concept Information",
            styles["Heading2"]
        )
    )

    concept_data = [

        ["Field", "Value"],

        ["Platform", platform_name],
        ["Model", model_name],
        ["Model Code", model_code],
        ["Report By", report_by],
        ["Additional Info", info_field],
    ]

    if comments.strip():

        concept_data.append(
            ["Comments", comments]
        )

    concept_table = Table(
        concept_data,
        colWidths=[120, 320],
        hAlign="LEFT"
    )

    concept_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ])
    )

    elements.append(concept_table)

    elements.append(
        Spacer(1, 12)
    )

    # =================================================
    # INPUT PARAMETERS
    # =================================================

    elements.append(
        Paragraph(
            "Input Parameters",
            styles["Heading2"]
        )
    )

    general_data = [

        ["GENERAL", ""],

        ["Product Type", power_type],
        ["Nozzle Width", f"{nozzle_width} mm"],
        ["Maintenance Power", f"{maintenance_power:.1f} W"],
        ["Battery Efficiency", f"{battery_efficiency:.0%}"],
        ["Charger Efficiency", f"{charger_efficiency:.0%}"],
    ]

    general_table = Table(
        general_data,
        colWidths=[130, 80]
    )

    general_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),

            ("BACKGROUND", (0, 0), (1, 0), colors.lightgrey),
            ("SPAN", (0, 0), (1, 0)),

            ("FONTNAME", (0, 0), (1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (1, 0), "CENTER"),
        ])
    )
    power_data = [

        ["POWER", ""],

        ["MFU Carpet", f"{mfu_carpet:.0f} W"],
        ["Nozzle Carpet", f"{nozzle_carpet:.0f} W"],

        ["MFU Hard Floor", f"{mfu_hardfloor:.0f} W"],
        ["Nozzle Hard Floor", f"{nozzle_hardfloor:.0f} W"],

        ["DCPM Power", f"{dcpm_power:.0f} W"],
    ]

    power_table = Table(
        power_data,
        colWidths=[130, 80]
    )

    power_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),

            ("BACKGROUND", (0, 0), (1, 0), colors.lightgrey),
            ("SPAN", (0, 0), (1, 0)),

            ("FONTNAME", (0, 0), (1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (1, 0), "CENTER"),
        ])
    )

    performance_data = [

    ["PERFORMANCE", ""],

    ["Carpet Clogging", f"{clogging_carpet*100:.0f}%"],
    ["Hard Floor Clogging", f"{clogging_hardfloor*100:.0f}%"],

    ["DPU Carpet", f"{dpu_carpet*100:.0f}%"],
    ["Debris Carpet", f"{debris_carpet*100:.0f}%"],

    ["DPU Hard Floor", f"{dpu_hardfloor*100:.0f}%"],
    ["Debris Hard Floor", f"{debris_hardfloor*100:.0f}%"],
    ]

    performance_table = Table(
        performance_data,
        colWidths=[130, 80]
    )

    performance_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),

            ("BACKGROUND", (0, 0), (1, 0), colors.lightgrey),
            ("SPAN", (0, 0), (1, 0)),

            ("FONTNAME", (0, 0), (1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (1, 0), "CENTER"),
        ])
    )

    sound_data = [

        ["SOUND", ""],

        ["Carpet", f"{sound_carpet:.0f} dBA"],
        ["Hard Floor", f"{sound_hardfloor:.0f} dBA"],
    ]

    sound_table = Table(
        sound_data,
        colWidths=[130, 80]
    )

    sound_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),

            ("BACKGROUND", (0, 0), (1, 0), colors.lightgrey),
            ("SPAN", (0, 0), (1, 0)),

            ("FONTNAME", (0, 0), (1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (1, 0), "CENTER"),
        ])
    )

    input_layout = Table(
        [
            [general_table, performance_table],
            [power_table, sound_table]
        ],
        colWidths=[250, 250]
    )

    input_layout.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )

    elements.append(input_layout)

    elements.append(PageBreak())

    elements.append(
        Paragraph(
            "Energy results",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 8))
    
    results_data = [
        ["Result", "Value"],
        ["Energy Class", grade],
        ["EEI", f"{eei:.1f}"],
        ["AE", f"{ae:.1f} kWh/a"],
        ["CP Factor", f"{cp_factor:.6f}"],
    ]

    results_table = Table(
        results_data,
        colWidths=[280, 120],
        hAlign="LEFT"
    )

    results_table.setStyle(
        TableStyle([

            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),

            ("GRID", (0, 0), (-1, -1), 1, colors.black),

            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

            # Energy class color

            (
                "BACKGROUND",
                (1, 1),
                (1, 1),
                report_grade_color(grade)
            ),

            (
                "TEXTCOLOR",
                (1, 1),
                (1, 1),
                colors.white
            ),

            (
                "FONTNAME",
                (1, 1),
                (1, 1),
                "Helvetica-Bold"
            ),

        ])
)

    elements.append(results_table)

    elements.append(Spacer(1, 8))

    # =================================================
    # PERFORMANCE GRADES
    # =================================================

    elements.append(
        Paragraph(
            "Performance Grades",
            styles["Heading2"]
        )
    )

    grades_data = [
        ["Category", "Grade", "Value"],
        ["Carpet", carpet_class, f"{cp_carpet:.1f}"],
        ["Hard Floor", hardfloor_class, f"{cp_hardfloor:.1f}"],
        ["Sound", sound_class, f"{sound_gp:.1f} dBA"],
    ]

    grades_table = Table(
        grades_data,
        colWidths=[280, 80, 120],
        hAlign="LEFT"
    )

    grades_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        ("BACKGROUND", (1, 1), (1, 1),
         report_grade_color(carpet_class)),

        ("BACKGROUND", (1, 2), (1, 2),
         report_grade_color(hardfloor_class)),

        ("BACKGROUND", (1, 3), (1, 3),
         report_grade_color(sound_class)),

        ("TEXTCOLOR", (1, 1), (1, 3), colors.white),

        ("ALIGN", (1, 1), (1, 3), "CENTER"),

        ("FONTNAME", (1, 1), (1, 3),
         "Helvetica-Bold"),
    ])

    grades_table.setStyle(grades_style)

    elements.append(grades_table)

    elements.append(PageBreak())

    # =================================================
    # PERFORMANCE MAPS
    # =================================================

    elements.append(
        Paragraph(
            "Performance Maps",
            styles["Heading2"]
        )
    )

    elements.append(
        Paragraph(
            "Carpet Performance Map",
            styles["Heading3"]
        )
    )

    elements.append(
        Image(
            "carpet_map.png",
            width=300,
            height=220
        )
    )

    elements.append(
        Spacer(1, 10)
    )

    elements.append(
        Paragraph(
            "Hard Floor Performance Map",
            styles["Heading3"]
        )
    )

    elements.append(
        Image(
            "hardfloor_map.png",
            width=300,
            height=220
        )
    )

    elements.append(PageBreak())

    elements.append(
        Paragraph(
            "Sound Map",
            styles["Heading3"]
        )
    )

    elements.append(
        Image(
            "sound_map.png",
            width=300,
            height=220
        )
    )
   
    doc.build(elements)

    pdf = buffer.getvalue()

    buffer.close()

    return pdf

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
# POWER OVERRIDE
# =====================================================

override_power = st.checkbox("Total power input")

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
                step=0.1,
                disabled=override_power
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
            step=1,
            disabled=override_power,
            help="Shared DCPM power consumption used for both Carpet and Hard Floor calculations."
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
            step=0.01,
            disabled=override_power
        )

    with b2:

        charger_efficiency = st.number_input(
            "Charger Efficiency",
            value=0.90,
            step=0.01,
            disabled=override_power
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
        400,
        disabled=override_power
    )

    if power_type == "Cordless":

        nozzle_carpet = st.slider(
            "Nozzle power Carpet [W]",
            0,
            100,
            50,
            disabled=override_power
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
            0,
            disabled=override_power,
            help="""Input power added on carpet due to clogging performance drop"""
        ) / 100
    )

        # Calculated Carpet Power

    calculated_carpet_power = calculate_power(
        mfu_carpet,
        nozzle_carpet,
        dcpm_power,
        clogging_carpet,
        charger_efficiency,
        battery_efficiency,
    )

    if override_power:

        power_carpet = st.number_input(
            "Total Carpet Power [W]",
            value=round(calculated_carpet_power, 1),
            step=1.0,
        )

    else:

        power_carpet = calculated_carpet_power

        st.metric(
            "Total Carpet Power [W]",
            f"{power_carpet:.1f}"
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
        400,
        disabled=override_power
    )

    if power_type == "Cordless":

        nozzle_hardfloor = st.slider(
            "Nozzle power Hard Floor [W]",
            0,
            100,
            10,
            disabled=override_power
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
            0,
            disabled=override_power,
            help="""Input power added on hardfloor due to clogging performance drop"""
        ) / 100
    )
        # Calculated Hard Floor Power

    calculated_hardfloor_power = calculate_power(
        mfu_hardfloor,
        nozzle_hardfloor,
        dcpm_power,
        clogging_hardfloor,
        charger_efficiency,
        battery_efficiency,
    )

    if override_power:

        power_hardfloor = st.number_input(
            "Total Hard Floor Power [W]",
            value=round(calculated_hardfloor_power, 1),
            step=1.0,
        )

    else:

        power_hardfloor = calculated_hardfloor_power

        st.metric(
            "Total Hard Floor Power [W]",
            f"{power_hardfloor:.1f}"
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

        current_x=dpu_carpet * 100,
        current_y=debris_carpet * 100,

        boundaries={
            "A": 81,
            "B": 77,
            "C": 72,
        },

        x_range=(70, 86),
        y_range=(45, 100),

        x_label="Dust Pick-Up [%]",
        y_label="Debris Pick-Up [%]",

        x_weight=0.9,
        y_weight=0.1,

        label_positions={
            "D": (71.0, 68),
            "C": (75.5, 68),
            "B": (79.8, 68),
            "A": (84.2, 68),
        },
    )

    st.pyplot(carpet_fig)

with c2:

    hardfloor_fig = performance_map(
        title="Hard Floor Performance Grade",

        current_x=dpu_hardfloor * 100,
        current_y=debris_hardfloor * 100,

        boundaries={
            "A": 106,
            "B": 101,
            "C": 95,
        },

        x_range=(95, 115),
        y_range=(45, 100),

        x_label="Dust Pick-Up [%]",
        y_label="Debris Pick-Up [%]",

        x_weight=0.9,
        y_weight=0.1,

        label_positions={
            "D": (96.0, 68),
            "C": (101.0, 68),
            "B": (107.5, 68),
            "A": (112.5, 68),
        },
    )

    st.pyplot(hardfloor_fig)

st.subheader("Sound Map")

sound_fig = sound_map(
    sound_carpet,
    sound_hardfloor,
)

st.pyplot(sound_fig)

# =====================================================
# REPORT INFORMATION
# =====================================================

st.subheader("Export")

with st.expander("Report Information", expanded=True):

    c1, c2 = st.columns(2)

    with c1:
        platform_name = st.text_input(
            "Platform",
            value=""
        )

        model_name = st.text_input(
            "Model",
            value=""
        )

        model_code = st.text_input(
            "Model Code",
            value=""
        )

    with c2:
        report_by = st.text_input(
            "Report by",
            value=""
        )

        info_field = st.text_input(
            "Additional info",
            value=""
        )

        comments = st.text_area(
            "Comments",
            value="",
            height=80
        )


# =====================================================
# GENERATE REPORT
# =====================================================

carpet_fig.savefig(
    "carpet_map.png",
    bbox_inches="tight"
)

hardfloor_fig.savefig(
    "hardfloor_map.png",
    bbox_inches="tight"
)

sound_fig.savefig(
    "sound_map.png",
    bbox_inches="tight"
)

pdf_report = create_pdf_report(

    platform_name=platform_name,
    model_name=model_name,
    model_code=model_code,
    report_by=report_by,
    info_field=info_field,
    comments=comments,

    power_type=power_type,

    nozzle_width=nozzle_width,
    maintenance_power=maintenance_power,
    dcpm_power=dcpm_power,

    battery_efficiency=battery_efficiency,
    charger_efficiency=charger_efficiency,

    mfu_carpet=mfu_carpet,
    nozzle_carpet=nozzle_carpet,
    clogging_carpet=clogging_carpet,
    dpu_carpet=dpu_carpet,
    debris_carpet=debris_carpet,
    sound_carpet=sound_carpet,

    mfu_hardfloor=mfu_hardfloor,
    nozzle_hardfloor=nozzle_hardfloor,
    clogging_hardfloor=clogging_hardfloor,
    dpu_hardfloor=dpu_hardfloor,
    debris_hardfloor=debris_hardfloor,
    sound_hardfloor=sound_hardfloor,

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


st.download_button(
    label="📄 Download PDF Report",
    data=pdf_report,
    file_name="e_label_report.pdf",
    mime="application/pdf"
)

st.info(
    """
    Version 0.9.7 | Last updated: 2026-10-13

    Author: CS
    """
)