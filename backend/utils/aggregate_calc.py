def comsatsAggregate_calculator(ssc_obtained, ssc_total, hssc_obtained, hssc_total, 
                                entry_testmarks, total_entry_test_marks,
                                additionalcategoryselected=None, weightage=None, gap_years=None):
   
    entry_testpercent = (entry_testmarks / total_entry_test_marks) * 100
    matric_percent = (ssc_obtained / ssc_total) * 100
    inter_percent = (hssc_obtained / hssc_total) * 100
    aggregate = (matric_percent * 0.1) + (inter_percent * 0.4) + (entry_testpercent * 0.5)
    return round(aggregate, 2)


def puAggregate_calculator(ssc_obtained, ssc_total, hssc_obtained, hssc_total, 
                          entry_testmarks, total_entry_test_marks, 
                          additionalcategoryselected=None, weightage=100, gap_years=0):
   
    if additionalcategoryselected is None:
        additionalcategoryselected = {}
    
    
    additional_obtained = 0
    additional_total = 0
    
    
    if additionalcategoryselected.get('hafiz', False):
        additional_obtained += 20
        additional_total += 20
    
    
    elective = additionalcategoryselected.get('elective_marks', 0)
    if elective > 0:
        additional_obtained += min(elective, 20)
        additional_total += 20
    
    
    optional = additionalcategoryselected.get('optional_marks', 0)
    if optional > 0:
        additional_obtained += min(optional, 10)
        additional_total += 10
    
    
    if additionalcategoryselected.get('diploma', False):
        additional_obtained += 20
        additional_total += 20
    
    
    additional_elective = additionalcategoryselected.get('additional_elective_marks', 0)
    if additional_elective > 0:
        additional_obtained += min(additional_elective, 10)
        additional_total += 10
    
    
    additional_optional = additionalcategoryselected.get('additional_optional_marks', 0)
    if additional_optional > 0:
        additional_obtained += min(additional_optional, 5)
        additional_total += 5
    
    
    if additionalcategoryselected.get('combination', False):
        additional_obtained += 10
        additional_total += 10
    

    subject_marks = additionalcategoryselected.get('subject_marks', 0)
    subject_total = additionalcategoryselected.get('subject_total', 0)
    if subject_marks > 0 and subject_total > 0:
        additional_obtained += subject_marks
        additional_total += subject_total
    
    
    other = additionalcategoryselected.get('other_marks', 0)
    if other > 0:
        additional_obtained += min(other, 10)
        additional_total += 10
    
    
    matric_contribution_obtained = ssc_obtained / 4
    matric_contribution_total = ssc_total / 4
    

    numerator = matric_contribution_obtained + hssc_obtained + additional_obtained
    denominator = matric_contribution_total + hssc_total + additional_total
    academic_percentage = (numerator / denominator) * 100
    
    # Apply academic weightage
    merit = academic_percentage * (weightage / 100)
    
    # Add entry test contribution if weightage < 100
    if weightage < 100:
        test_weightage = 100 - weightage  # e.g., if 70% academic, then 30% test
        test_percentage = (entry_testmarks / total_entry_test_marks) * 100
        merit += test_percentage * (test_weightage / 100)
    
    # Deduct for gap years (2 marks per year, max 5 years = 10 marks)
    gap_deduction = min(gap_years, 5) * 2
    final_aggregate = merit - gap_deduction
    
    return round(final_aggregate, 2)


def calculate_aggregate(university_name, ssc_obtained, ssc_total, hssc_obtained, hssc_total,
                       entry_testmarks, total_entry_test_marks,
                       additionalcategoryselected=None, weightage=100, gap_years=0):
  
    university_name = university_name.upper().strip()
    
    if university_name == 'COMSATS':
        return comsatsAggregate_calculator(
            ssc_obtained, ssc_total, hssc_obtained, hssc_total,
            entry_testmarks, total_entry_test_marks
        )
    
    elif university_name in ['PU', 'PUNJAB UNIVERSITY']:
        return puAggregate_calculator(
            ssc_obtained, ssc_total, hssc_obtained, hssc_total,
            entry_testmarks, total_entry_test_marks,
            additionalcategoryselected, weightage, gap_years
        )
    
    else:
        raise ValueError(f"Aggregate calculator for {university_name} is not available.")


