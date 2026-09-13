import pandas as pd
import re


# ==================================================
# LOAD PROGRAM DATA
# ==================================================

EXCEL_PATH = "programs.xlsx"

REQUIRED_COLUMNS = [
    "program_id",
    "program_name",
    "program_name_ur",
    "category",
    "scope",
    "province",
    "implementing_agency",
    "min_age",
    "max_age",
    "education_level",
    "student_status_required",
    "max_monthly_income_pkr",
    "special_criteria",
    "benefits_coverage",
    "required_documents",
    "application_steps",
    "official_url",
    "helpline"
]

try:

    df = pd.read_excel(EXCEL_PATH)

except FileNotFoundError:

    raise FileNotFoundError(
        f"Could not find '{EXCEL_PATH}'. Make sure the "
        "programs spreadsheet is in the project root "
        "before starting the app."
    )

except Exception as error:

    raise RuntimeError(
        f"Failed to read '{EXCEL_PATH}': {error}"
    )

missing_columns = [
    column
    for column in REQUIRED_COLUMNS
    if column not in df.columns
]

if missing_columns:

    raise RuntimeError(
        f"'{EXCEL_PATH}' is missing required column(s): "
        f"{', '.join(missing_columns)}"
    )


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def clean_text(value):
    if pd.isna(value):
        return ""

    return str(value).strip().lower()


def normalize_province(province):

    province = clean_text(province)

    aliases = {
        "kpk": "khyber pakhtunkhwa",
        "kp": "khyber pakhtunkhwa",
        "nwfp": "khyber pakhtunkhwa",
        "ajk": "azad jammu & kashmir",
        "gb": "gilgit-baltistan",
        "ict": "islamabad",
    }

    return aliases.get(province, province)


# ==================================================
# PROVINCE CHECK
# ==================================================

def province_matches(user_province, program_row):

    user_province = normalize_province(user_province)

    scope = clean_text(program_row["scope"])
    program_province = clean_text(program_row["province"])

    # Pakistan-wide program
    if "pakistan-wide" in scope:
        return True

    if "all pakistan" in program_province:
        return True

    if "all" == program_province:
        return True

    # Direct match
    if user_province in program_province:
        return True

    return False


# ==================================================
# AGE CHECK
# ==================================================

def age_matches(age, program_row):

    min_age = program_row["min_age"]
    max_age = program_row["max_age"]

    if pd.notna(min_age):

        try:

            if age < float(min_age):
                return False

        except:
            pass

    if pd.notna(max_age):

        try:

            if age > float(max_age):
                return False

        except:
            pass

    return True


# ==================================================
# EDUCATION CHECK
# ==================================================

def education_matches(user_education, program_education):

    user_education = clean_text(user_education)

    program_education = clean_text(program_education)

    # No restriction
    if not program_education:
        return True

    if "any" in program_education:
        return True

    if "all" in program_education:
        return True

    # Direct match
    if user_education in program_education:
        return True

    education_aliases = {

        "school": [
            "school",
            "primary",
            "secondary"
        ],

        "matric": [
            "matric",
            "secondary"
        ],

        "intermediate": [
            "intermediate",
            "higher secondary",
            "hssc"
        ],

        "undergraduate": [
            "undergraduate",
            "bachelor",
            "bs",
            "bsc",
            "ba",
            "bba",
            "bcom",
            "mbbs",
            "bds"
        ],

        "postgraduate": [
            "postgraduate",
            "master",
            "ms",
            "mphil",
            "phd",
            "mba"
        ]
    }

    if user_education in education_aliases:

        for keyword in education_aliases[user_education]:

            if keyword in program_education:
                return True

    return False


# ==================================================
# STUDENT STATUS CHECK
# ==================================================

def student_status_matches(
    user_student_status,
    required_status
):

    user_student_status = clean_text(
        user_student_status
    )

    required_status = clean_text(
        required_status
    )

    # Program doesn't specifically require students
    if required_status != "yes":
        return True

    return user_student_status == "yes"


# ==================================================
# INCOME CHECK
# ==================================================

def income_matches(user_income, program_income):

    program_income = clean_text(program_income)

    # No income restriction
    if not program_income:
        return True

    if "not income-tested" in program_income:
        return True

    # Extract number
    numbers = re.findall(
        r"\d+",
        program_income
    )

    if not numbers:
        return True

    try:

        maximum_income = float(numbers[0])

        return user_income <= maximum_income

    except:

        return True


# ==================================================
# MAIN ELIGIBILITY FUNCTION
# ==================================================

def find_eligible_programs(
    age,
    province,
    education,
    student_status,
    monthly_income
):

    eligible_programs = []

    for row_index, program in df.iterrows():

        try:

            # Province
            if not province_matches(
                province,
                program
            ):
                continue

            # Age
            if not age_matches(
                age,
                program
            ):
                continue

            # Education
            if not education_matches(
                education,
                program["education_level"]
            ):
                continue

            # Student status
            if not student_status_matches(
                student_status,
                program["student_status_required"]
            ):
                continue

            # Income
            if not income_matches(
                monthly_income,
                program["max_monthly_income_pkr"]
            ):
                continue

            # --------------------------------------
            # PROGRAM PASSED ALL STRUCTURED CHECKS
            # --------------------------------------

            program_id = clean_text(program.get("program_id"))

            if not program_id:
                # A row with no program_id can't be
                # matched back to its RAG documents,
                # so skip it rather than surface a
                # broken "eligible" result.
                print(
                    f"[SKIPPED ROW {row_index}] "
                    "missing program_id"
                )
                continue

            eligible_programs.append({

                "program_id": str(
                    program["program_id"]
                ),

                "program_name": str(
                    program["program_name"]
                ),

                "program_name_ur": str(
                    program["program_name_ur"]
                ),

                "category": str(
                    program["category"]
                ),

                "agency": str(
                    program["implementing_agency"]
                ),

                "benefits": str(
                    program["benefits_coverage"]
                ),

                "documents": str(
                    program["required_documents"]
                ),

                "application_steps": str(
                    program["application_steps"]
                ),

                "official_url": str(
                    program["official_url"]
                ),

                "helpline": str(
                    program["helpline"]
                ),

                "special_criteria": str(
                    program["special_criteria"]
                )
            })

        except Exception as error:

            # A single malformed row (bad type, unexpected
            # blank, etc.) should not take down the whole
            # search - skip it and keep going.

            print(
                f"[SKIPPED ROW {row_index}] "
                f"unexpected error: {error}"
            )

            continue

    return eligible_programs