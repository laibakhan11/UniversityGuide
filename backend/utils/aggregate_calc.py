def pct(obt, total):
    return (obt / total) * 100 if total else 0



def comsatsAggregate_calculator(ssc_obtained, ssc_total, hssc_obtained, hssc_total, 
                                entry_testmarks, total_entry_test_marks,
                                additionalcategoryselected=None, weightage=None, gap_years=None):
    
    matric = pct(ssc_obtained, ssc_total)
    inter = pct(hssc_obtained, hssc_total)
    test = pct(entry_testmarks, total_entry_test_marks)
    
    agg = (matric*0.10) + (inter*0.40) + (test*0.50)
    return round(agg, 2)



def puAggregate_calculator(ssc_obtained, ssc_total, hssc_obtained, hssc_total, 
                           entry_testmarks, total_entry_test_marks, 
                           additionalcategoryselected=None, weightage=100, gap_years=0):
    
    additionalcategoryselected = additionalcategoryselected or {}

    
    fixed_bonus = {
        "hafiz": 20, "diploma": 20, "combination": 10
    }

    add_obt, add_total = 0, 0

  
    for key, marks in fixed_bonus.items():
        if additionalcategoryselected.get(key):
            add_obt += marks
            add_total += marks

    
    limited_fields = {
        "elective_marks": 20,
        "optional_marks": 10,
        "additional_elective_marks": 10,
        "additional_optional_marks": 5,
        "other_marks": 10
    }

    for field, limit in limited_fields.items():
        value = additionalcategoryselected.get(field, 0)
        if value > 0:
            add_obt += min(value, limit)
            add_total += limit

    
    add_obt += additionalcategoryselected.get("subject_marks", 0)
    add_total += additionalcategoryselected.get("subject_total", 0)

   
    numerator = (ssc_obtained/4) + hssc_obtained + add_obt
    denominator = (ssc_total/4) + hssc_total + add_total
    academic = pct(numerator, denominator)

  
    merit = (academic * weightage/100)

    if weightage < 100:
        test_pct = pct(entry_testmarks, total_entry_test_marks)
        merit += test_pct * ((100-weightage)/100)

    merit -= min(gap_years, 5) * 2

    return round(merit, 2)




def fastAggregate_calculator(ssc_obtained, ssc_total, hssc_obtained, hssc_total,
                             entry_testmarks, total_entry_test_marks, is_engineering=False):

    matric = pct(ssc_obtained, ssc_total)
    inter = pct(hssc_obtained, hssc_total)
    test = pct(entry_testmarks, total_entry_test_marks)

    if is_engineering:
        agg = (matric*0.17) + (inter*0.50) + (test*0.33)
    else:
        agg = (matric*0.10) + (inter*0.40) + (test*0.50)

    return round(agg, 2)



def umtAggregate_calculator(ssc_obtained, ssc_total, hssc_obtained, hssc_total,
                            entry_testmarks, total_entry_test_marks, is_engineering=False):

    matric = pct(ssc_obtained, ssc_total)
    inter = pct(hssc_obtained, hssc_total)
    test = pct(entry_testmarks, total_entry_test_marks)

    if is_engineering and test < 33:
        return "Fail in test — 33% required"

    if is_engineering:
        agg = (matric*0.17) + (inter*0.50) + (test*0.33)
    else:
        agg = (matric*0.20) + (inter*0.50) + (test*0.30)

    return round(agg, 2)

def gikiAggregate_calculator(ssc_obtained, ssc_total, hssc_obtained, hssc_total,
                             entry_testmarks, total_entry_test_marks):
    inter = pct(hssc_obtained, hssc_total)
    test = pct(entry_testmarks, total_entry_test_marks)
    agg = (test * 0.85) + (inter * 0.15)
    return round(agg, 2)

def airAggregate_calculator(ssc_obtained, ssc_total, hssc_obtained, hssc_total,
                            entry_testmarks, total_entry_test_marks, is_engineering=False):
  
    matric = pct(ssc_obtained, ssc_total)
    inter = pct(hssc_obtained, hssc_total)
    test = pct(entry_testmarks, total_entry_test_marks)
    
    if is_engineering:
        agg = (matric * 0.10) + (inter * 0.35) + (test * 0.55)
    else:
        agg = (matric * 0.15) + (inter * 0.40) + (test * 0.45)
    return round(agg, 2)

def calculate_aggregate(university_name, *args, **kwargs):
    uni = university_name.upper().strip()
    
    uni_map = {
        "COMSATS": comsatsAggregate_calculator,
        "PU": puAggregate_calculator,
        "PUNJAB UNIVERSITY": puAggregate_calculator,
        "FAST": fastAggregate_calculator,
        "FAST NU": fastAggregate_calculator,
        "FAST NUCES": fastAggregate_calculator,
        "NUCES": fastAggregate_calculator,
        "UMT": umtAggregate_calculator,
        "GIKI": gikiAggregate_calculator,
        "AIR": airAggregate_calculator,
        "AIR UNIVERSITY": airAggregate_calculator,
    }
    
    if uni not in uni_map:
        return f"Aggregate formula not available for {university_name}"
    
    return uni_map[uni](*args, **kwargs)