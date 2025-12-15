def pct(obt, total):
    return (obt / total) * 100 if total else 0

def comsatsAggregate_calculator(ssc_obtained, ssc_total, hssc_obtained, hssc_total, 
                                entry_testmarks, total_entry_test_marks, **kwargs):
    matric = pct(ssc_obtained, ssc_total)
    inter = pct(hssc_obtained, hssc_total)
    test = pct(entry_testmarks, total_entry_test_marks)
    agg = (matric*0.10) + (inter*0.40) + (test*0.50)
    return round(agg, 2)

def puAggregate_calculator(ssc_obtained, ssc_total, hssc_obtained, hssc_total, 
                           entry_testmarks, total_entry_test_marks, 
                           additionalcategoryselected=None, weightage=100, gap_years=0, **kwargs):
    additionalcategoryselected = additionalcategoryselected or {}
    fixed_bonus = {"hafiz": 20, "diploma": 20, "combination": 10}
    add_obt, add_total = 0, 0

    for key, marks in fixed_bonus.items():
        if additionalcategoryselected.get(key):
            add_obt += marks
            add_total += marks

    elective = min(additionalcategoryselected.get('elective_marks', 0), 20)
    add_obt += elective
    add_total += 20

    numerator = (ssc_obtained/4) + hssc_obtained + add_obt
    denominator = (ssc_total/4) + hssc_total + add_total
    academic = pct(numerator, denominator)
    merit = academic - (min(gap_years, 5) * 2)
    return round(merit, 2)

def fastAggregate_calculator(ssc_obtained, ssc_total, hssc_obtained, hssc_total,
                             entry_testmarks, total_entry_test_marks, is_engineering=False, **kwargs):
    matric = pct(ssc_obtained, ssc_total)
    inter = pct(hssc_obtained, hssc_total)
    test = pct(entry_testmarks, total_entry_test_marks)
    
    if is_engineering:
        agg = (matric*0.17) + (inter*0.50) + (test*0.33)
    else:
        agg = (matric*0.10) + (inter*0.40) + (test*0.50)
    return round(agg, 2)

def umtAggregate_calculator(ssc_obtained, ssc_total, hssc_obtained, hssc_total,
                            entry_testmarks, total_entry_test_marks, is_engineering=False, **kwargs):
    matric = pct(ssc_obtained, ssc_total)
    inter = pct(hssc_obtained, hssc_total)
    test = pct(entry_testmarks, total_entry_test_marks)
    
    if is_engineering and test < 33:
        return {"error": "Test score must be ≥33% for Engineering"}
    
    if is_engineering:
        agg = (matric*0.17) + (inter*0.50) + (test*0.33)
    else:
        agg = (matric*0.20) + (inter*0.50) + (test*0.30)
    return round(agg, 2)

def gikiAggregate_calculator(ssc_obtained, ssc_total, hssc_obtained, hssc_total,
                             entry_testmarks, total_entry_test_marks, **kwargs):
    inter = pct(hssc_obtained, hssc_total)
    test = pct(entry_testmarks, total_entry_test_marks)
    agg = (test * 0.85) + (inter * 0.15)
    return round(agg, 2)

def airAggregate_calculator(ssc_obtained, ssc_total, hssc_obtained, hssc_total,
                            entry_testmarks, total_entry_test_marks, is_engineering=False, **kwargs):
    matric = pct(ssc_obtained, ssc_total)
    inter = pct(hssc_obtained, hssc_total)
    test = pct(entry_testmarks, total_entry_test_marks)
    
    if is_engineering:
        agg = (matric * 0.10) + (inter * 0.35) + (test * 0.55)
    else:
        agg = (matric * 0.15) + (inter * 0.40) + (test * 0.45)
    return round(agg, 2)

def ibaAggregate_calculator(ssc_obtained, ssc_total, hssc_obtained, hssc_total,
                            entry_testmarks, total_entry_test_marks, **kwargs):
    matric = pct(ssc_obtained, ssc_total)
    inter = pct(hssc_obtained, hssc_total)
    test = pct(entry_testmarks, total_entry_test_marks)
    agg = (matric * 0.10) + (inter * 0.40) + (test * 0.50)
    return round(agg, 2)

def nustAggregate_calculator(ssc_obtained, ssc_total, hssc_obtained, hssc_total,
                             entry_testmarks, total_entry_test_marks, **kwargs):
    matric = pct(ssc_obtained, ssc_total)
    inter = pct(hssc_obtained, hssc_total)
    test = pct(entry_testmarks, total_entry_test_marks)
    agg = (matric * 0.10) + (inter * 0.15) + (test * 0.75)
    return round(agg, 2)

def ituAggregate_calculator(ssc_obtained, ssc_total, hssc_obtained, hssc_total,
                            entry_testmarks, total_entry_test_marks, **kwargs):
    matric = pct(ssc_obtained, ssc_total)
    inter = pct(hssc_obtained, hssc_total)
    test = pct(entry_testmarks, total_entry_test_marks)
    agg = (matric * 0.10) + (inter * 0.40) + (test * 0.50)
    return round(agg, 2)

def lseAggregate_calculator(ssc_obtained, ssc_total, hssc_obtained, hssc_total,
                            entry_testmarks, total_entry_test_marks, **kwargs):
    matric = pct(ssc_obtained, ssc_total)
    inter = pct(hssc_obtained, hssc_total)
    test = pct(entry_testmarks, total_entry_test_marks)
    agg = (matric * 0.15) + (inter * 0.45) + (test * 0.40)
    return round(agg, 2)

# University Calculator Mapping
UNIVERSITY_CALCULATORS = {
    "COMSATS": {
        "name": "COMSATS University",
        "calculator": comsatsAggregate_calculator,
        "formula": "10% Matric + 40% Inter + 50% Test",
        "options": []
    },
    "PU": {
        "name": "Punjab University (PU)",
        "calculator": puAggregate_calculator,
        "formula": "Academic Merit + Bonuses - Gap Years",
        "options": ["hafiz", "diploma", "combination", "elective_marks", "gap_years"]
    },
    "FAST": {
        "name": "FAST-NUCES",
        "calculator": fastAggregate_calculator,
        "formula": "Eng: 17%+50%+33% | Non-Eng: 10%+40%+50%",
        "options": ["is_engineering"]
    },
    "UMT": {
        "name": "University of Management & Technology (UMT)",
        "calculator": umtAggregate_calculator,
        "formula": "Eng: 17%+50%+33% | Non-Eng: 20%+50%+30%",
        "options": ["is_engineering"]
    },
    "GIKI": {
        "name": "Ghulam Ishaq Khan Institute (GIKI)",
        "calculator": gikiAggregate_calculator,
        "formula": "85% Test + 15% Inter",
        "options": []
    },
    "AU": {
        "name": "Air University",
        "calculator": airAggregate_calculator,
        "formula": "Eng: 10%+35%+55% | Non-Eng: 15%+40%+45%",
        "options": ["is_engineering"]
    },
    "IBA": {
        "name": "IBA Karachi",
        "calculator": ibaAggregate_calculator,
        "formula": "10% Matric + 40% Inter + 50% Test",
        "options": []
    },
    "NUST": {
        "name": "NUST",
        "calculator": nustAggregate_calculator,
        "formula": "10% Matric + 15% Inter + 75% NET",
        "options": []
    },
    "ITU": {
        "name": "Information Technology University (ITU)",
        "calculator": ituAggregate_calculator,
        "formula": "10% Matric + 40% Inter + 50% Test",
        "options": []
    },
    "LSE": {
        "name": "Lahore School of Economics (LSE)",
        "calculator": lseAggregate_calculator,
        "formula": "15% Matric + 45% Inter + 40% Test",
        "options": []
    },
    "FAST-NU Lahore": {
        "name": "FAST-NUCES Lahore",
        "calculator": fastAggregate_calculator,
        "formula": "Eng: 17%+50%+33% | Non-Eng: 10%+40%+50%",
        "options": ["is_engineering"]
    }
}