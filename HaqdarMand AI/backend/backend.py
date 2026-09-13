from backend.eligibility import (
    find_eligible_programs
)

from backend.rag import (
    retrieve_program_context
)

from backend.llm import (
    ask_about_program
)


# ==================================================
# STEP 1
# FIND ELIGIBLE PROGRAMS
# ==================================================

def find_programs(
    age,
    province,
    education,
    student_status,
    monthly_income
):

    try:

        eligible_programs = find_eligible_programs(

            age=age,

            province=province,

            education=education,

            student_status=student_status,

            monthly_income=monthly_income
        )

    except Exception as error:

        print(f"[ELIGIBILITY ERROR] {error}")

        return {

            "success": False,

            "programs": [],

            "program_count": 0
        }

    return {

        "success": True,

        "programs": eligible_programs,

        "program_count": len(
            eligible_programs
        )
    }


# ==================================================
# STEP 2
# ASK ABOUT SELECTED PROGRAM
# ==================================================

def ask_program_question(
    program,
    question
):

    # ----------------------------------------------
    # RAG
    # ----------------------------------------------

    try:

        retrieved_context = retrieve_program_context(

            program_id=program["program_id"],

            question=question,

            k=1
        )

    except Exception as error:

        # Covers: Chroma DB unreachable/corrupted, embedding
        # API failure/timeout, network errors, etc.

        print(f"[RAG ERROR] retrieval failed: {error}")

        return {

            "success": False,

            "answer": (
                "I'm having trouble accessing the program "
                "information right now. Please try again "
                "in a moment."
            )
        }

    # ----------------------------------------------
    # NO CONTEXT FOUND
    # ----------------------------------------------

    if not retrieved_context:

        return {

            "success": False,

            "answer": (
                "I could not retrieve information "
                "about this program."
            )
        }

    # ----------------------------------------------
    # GEMINI
    # ----------------------------------------------

    try:

        answer = ask_about_program(

            program=program,

            question=question,

            retrieved_context=retrieved_context
        )

    except Exception as error:

        print(f"[LLM ERROR] answering failed: {error}")

        return {

            "success": False,

            "answer": (
                "I'm having trouble generating an answer "
                "right now. Please try again in a moment."
            )
        }

    return {

        "success": True,

        "program": program,

        "answer": answer
    }