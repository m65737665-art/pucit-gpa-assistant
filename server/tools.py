# tool1
def marks_to_grade_points(marks:int)->float | str:
    """use this tool to convert marks to grade points """
    if marks < 0 or marks > 100:
        return "Error: marks must be between 0 and 100"

    if marks>=85:
        return 4.0
    elif marks>=80:
        return 3.7
    elif marks>=75:
        return 3.3
    elif marks>=70:
        return 3.0
    elif marks>=65:
        return 2.7
    elif marks>=61:
        return 2.3
    elif marks>=58:
        return 2.0
    elif marks>=55:
        return 1.7
    elif marks>=50:
        return 1.0
    else:
        return 0.0

    
# tool2
def calculate_semester_gpa(grade_points:list[float],credit_hours:list[float])->float | str:
    """use this tool to calculate semester gpa """

    if len(grade_points)!=len(credit_hours):
        return "Error: grade_points and credit_hours lists must have the same length"
    if(not grade_points or not credit_hours):
        return "Error: grade_points and credit_hours lists must not be empty"
    gpa=0
    for gp , ch in zip(grade_points, credit_hours ):
        if gp < 0 or gp > 4:
            return "Error: grade points must be between 0 and 4"
        if ch <= 0:
            return "Error: credit hours must be positive"
        gpa+=gp*ch

    return (gpa)/sum(credit_hours)

# tool3

def calculate_new_cgpa(current_cgpa:float ,completed_credit_hours:float, semester_gpa:float , semester_credit_hours: float)->float:
    """use this tool to calculate new cgpa after a semester """
    if current_cgpa < 0 or current_cgpa > 4:
        return "Error: current cgpa must be between 0 and 4"
    if completed_credit_hours <= 0:
        return "Error: completed credit hours must be positive"
    if semester_gpa < 0 or semester_gpa > 4:
        return "Error: semester gpa must be between 0 and 4"
    if semester_credit_hours <= 0:
        return "Error: semester credit hours must be positive"

    new_cgpa=(current_cgpa*completed_credit_hours + semester_gpa*semester_credit_hours)/(completed_credit_hours+semester_credit_hours)
    return new_cgpa

# tool4 

def required_gpa_for_target(target_cgpa:float ,current_cgpa:float ,completed_credit_hours:float, remaining_credit_hours:float)->float | str:
    """use this tool to calculate required gpa for target cgpa """
    if target_cgpa < 0 or target_cgpa > 4:
        return "Error: target cgpa must be between 0 and 4"
    if current_cgpa < 0 or current_cgpa > 4:
        return "Error: current cgpa must be between 0 and 4"
    if completed_credit_hours <= 0:
        return "Error: completed credit hours must be positive"
    if remaining_credit_hours <= 0:
        return "Error: remaining credit hours must be positive"

    required_gpa=(target_cgpa*(completed_credit_hours+remaining_credit_hours)-current_cgpa*completed_credit_hours)/remaining_credit_hours
    return required_gpa

# tool5

COURSES = {
    1: [
        ("MS-251", "Probability & Statistics", 3.0),
        ("GE-160", "Applications of ICT", 3.0),
        ("GE-169", "Applied Physics", 3.0),
        ("GE-167", "Discrete Structures", 3.0),
        ("HQ-001", "Quran Translation - I", 0.5),
        ("GE-190", "Functional English", 3.0),
    ],

    2: [
        ("CC-112", "Programming Fundamentals", 3.0),
        ("CC-112-L", "Programming Fundamentals Lab", 1.0),
        ("CC-110", "Digital Logic Design", 2.0),
        ("CC-110-L", "Digital Logic Design Lab", 1.0),
        ("MS-252", "Linear Algebra", 3.0),
        ("GE-191", "Expository Writing", 3.0),
        ("GE-163", "Islamic Studies", 2.0),
        ("HQ-002", "Quran Translation - II", 0.5),
    ],

    3: [
        ("CC-211", "Object Oriented Programming", 3.0),
        ("CC-211-L", "Object Oriented Programming Lab", 1.0),
        ("CC-215", "Database Systems", 3.0),
        ("CC-215-L", "Database Systems Lab", 1.0),
        ("CC-210", "Computer Organization & Assembly Language", 3.0),
        ("GE-162", "Calculus & Analytical Geometry", 3.0),
        ("GE-192", "Introduction to Management", 2.0),
        ("HQ-003", "Quran Translation - III", 0.5),
    ],

    4: [
        ("CC-213", "Data Structures", 3.0),
        ("CC-213-L", "Data Structures Lab", 1.0),
        ("CC-312", "Information Security", 3.0),
        ("CC-214", "Computer Networks", 3.0),
        ("CC-212", "Software Engineering", 3.0),
        ("DC-220", "Advanced Database Management Systems", 3.0),
        ("HQ-004", "Quran Translation - IV", 0.5),
    ],

    5: [
        ("CC-313", "Analysis of Algorithms", 3.0),
        ("CC-310", "Artificial Intelligence", 3.0),
        ("DC-320", "Theory of Automata and Formal Languages", 3.0),
        ("DC-321", "Human Computer Interaction", 3.0),
        ("DC-322", "Computer Architecture", 3.0),
        ("EC-330", "Web Technologies / Elective", 3.0),
        ("HQ-005", "Quran Translation - V", 0.5),
    ],

    6: [
        ("CC-311", "Operating Systems", 3.0),
        ("EC-333", "Mobile Application Development / Elective", 3.0),
        ("EC-324", "Software Construction & Development / Elective", 3.0),
        ("EC-335", "Machine Learning / Elective", 3.0),
        ("EC-334", "Game Design and Development / Elective", 3.0),
        ("MS-253", "Multivariable Calculus", 3.0),
        ("HQ-006", "Quran Translation - VI", 0.5),
    ],

    7: [
        ("CC-411", "Final Year Project - I", 2.0),
        ("DC-328", "Parallel & Distributed Computing", 3.0),
        ("EC-345", "Computer Vision / Elective", 3.0),
        ("EC-425", "Software Quality Engineering / Elective", 3.0),
        ("MS-254", "Technical and Business Writing", 3.0),
        ("GE-263", "Entrepreneurship", 2.0),
        ("GE-262", "Professional Practices", 2.0),
        ("HQ-007", "Quran Translation - VII", 0.5),
    ],

    8: [
        ("CC-412", "Final Year Project - II", 4.0),
        ("DC-421", "Compiler Construction", 3.0),
        ("UE-272", "Introduction to Marketing", 3.0),
        ("GE-168", "Ideology and Constitution of Pakistan", 2.0),
        ("GE-363", "Civics and Community Engagement", 2.0),
        ("HQ-008", "Quran Translation - VIII", 0.5),
    ],
}
def get_semester_courses(semester:int)-> str:
    """use this tool to get semester courses """
    if semester < 1 or semester > 8:
        return "Error: semester must be between 1 and 8"
    


    courses = COURSES[semester]
    result = f"Semester {semester} courses:\n"
    for code, name, credits in courses:
        result += f"- {code}: {name} ({credits} credits)\n"
    return result


# tool6
def get_remaining_credit_hours(semester:int)->float | str:
    """use this tool to get remaining credit hours from current semester """
    if semester < 1 or semester > 8:
        return "Error: semester must be between 1 and 8"
    remaining=0
    for i in range(semester,9):
        for course in COURSES[i]:
            remaining+=course[2]

    return remaining


# tool7

def save_report(filename: str, content: str) -> str:
    """Use this tool when the student asks to save a completed GPA/CGPA report."""

    if not filename.strip():
        return "Error: filename cannot be empty"

    try:
        with open(filename, "w") as file:
            file.write(content)

        return f"Report saved successfully as {filename}"

    except Exception as e:
        return f"Error: could not save report: {e}"

    
#tool8

def get_credit_hours(semesters: list[int]) -> float | str:
    """Calculate the total credit hours for a list of specified semesters."""

    if not semesters:
        return "Error: semesters list cannot be empty"

    total = 0.0

    for semester in semesters:
        if semester < 1 or semester > 8:
            return f"Error: invalid semester {semester}. Semester must be between 1 and 8."

        for course in COURSES[semester]:
            total += course[2]

    return total