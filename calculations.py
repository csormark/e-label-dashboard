# calculations.py

def calculate_power(
    mfu_power,
    nozzle_power,
    dcpm_power,
    clogging_factor,
    charger_efficiency,
    battery_efficiency,
):
    """
    Excel:

    (MFU*(1+clogging)+nozzle+dcpm)
    /(charger_efficiency*battery_efficiency)
    """

    return (
        (
            mfu_power * (1 + clogging_factor)
            + nozzle_power
            + dcpm_power
        )
        / charger_efficiency
        / battery_efficiency
    )


# ============================================================
# ENERGY
# ============================================================

def calculate_eon(
    power_carpet,
    power_hardfloor,
    nozzle_width_mm,
):
    """
    Excel D13 contribution:

    ((Pc*0.25 + Phf*0.75)
      *17.4
      /(0.5*B/1000))
      /3600
    """

    weighted_power = (
        power_carpet * 0.25
        + power_hardfloor * 0.75
    )

    return (
        weighted_power
        * 17.4
        / (0.5 * nozzle_width_mm / 1000)
        / 3600
    )


def calculate_eaux():
    """
    Workbook value
    """

    return 0.0


def calculate_emaint(
    maintenance_power,
):
    """
    Excel:
    0.3 W → 2.4
    """

    return maintenance_power * 8


def calculate_ae(
    eon,
    eaux,
    emaint,
):
    """
    Excel D13

    Eaux + Emaint + Eon
    """

    return (
        eon
        + eaux
        + emaint
    )


# ============================================================
# CLEANING PERFORMANCE
# ============================================================

def calculate_cp_carpet(
    dpu_carpet,
    debris_carpet,
):
    """
    Excel D22

    =(0.9*D18+0.1*D19)*100
    """

    return (
        0.9 * dpu_carpet
        + 0.1 * debris_carpet
    ) * 100


def calculate_cp_hardfloor(
    dpu_hardfloor,
    debris_hardfloor,
):
    """
    Excel D23

    =(0.9*D20+0.1*D21)*100
    """

    return (
        0.9 * dpu_hardfloor
        + 0.1 * debris_hardfloor
    ) * 100



def calculate_cpgp(
    cp_carpet,
    cp_hardfloor,
):
    """
    Excel D24

    =(0.25*CPc+0.75*CPhf)/100
    """

    return (
        (
            0.25 * cp_carpet
            + 0.75 * cp_hardfloor
        )
        / 100
    )


def calculate_cp_factor(
    cpgp,
):
    """
    Excel D25

    =0.84375/(0.66*0.84375+0.33*CPgp)
    """

    return (
        0.84375
        / (
            0.66 * 0.84375
            + 0.33 * cpgp
        )
    )


# ============================================================
# EEI
# ============================================================

def calculate_eei(
    annual_energy,
    cp_factor,
):
    """
    Excel D15

    =(D13/36)*D25*100
    """

    return (
        annual_energy
        / 36
        * cp_factor
        * 100
    )


# ============================================================
# SOUND
# ============================================================

def calculate_sound_gp(
    sound_carpet,
    sound_hardfloor,
):
    """
    Excel D33

    =0.25*D31+0.75*D32
    """

    return (
        0.25 * sound_carpet
        + 0.75 * sound_hardfloor
    )


# ============================================================
# GRADES
# ============================================================

def energy_grade(
    eei,
):
    """
    Excel limits:
    30 A
    42 B
    54 C
    66 D
    78 E
    90 F
    """

    if eei < 30:
        return "A"
    elif eei < 42:
        return "B"
    elif eei < 54:
        return "C"
    elif eei < 66:
        return "D"
    elif eei < 78:
        return "E"
    elif eei < 90:
        return "F"
    else:
        return "G"
if __name__ == "__main__":

    power_carpet = 617
    power_hardfloor = 370
    nozzle_width = 250

    eon = calculate_eon(
        power_carpet,
        power_hardfloor,
        nozzle_width
    )

    emaint = calculate_emaint(0.3)

    ae = calculate_ae(
        eon,
        0,
        emaint
    )

    cp_c = calculate_cp_carpet(0.80)
    cp_hf = calculate_cp_hardfloor(1.05)

    cpgp = calculate_cpgp(
        cp_c,
        cp_hf
    )

    cp_factor = calculate_cp_factor(
        cpgp
    )

    eei = calculate_eei(
        ae,
        cp_factor
    )

    print("Eon =", round(eon, 1))
    print("Emaint =", round(emaint, 1))
    print("AE =", round(ae, 1))
    print("EEI =", round(eei, 1))