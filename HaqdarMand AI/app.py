import streamlit as st

from backend.backend import (
    find_programs,
    ask_program_question
)

from urdu_rtl import (
    inject_urdu_css,
    display_text
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="HaqDarmand AI",
    page_icon="🤝",
    layout="wide"
)

inject_urdu_css()


# ============================================================
# SESSION STATE
# ============================================================

if "programs" not in st.session_state:
    st.session_state.programs = []

if "selected_program" not in st.session_state:
    st.session_state.selected_program = None

if "answer" not in st.session_state:
    st.session_state.answer = None


# ============================================================
# HEADER
# ============================================================

st.title("🤝 HaqDarmand AI")

st.subheader(
    "Find scholarships, financial assistance, "
    "and health-support programs in Pakistan."
)

st.write(
    "Enter your basic information to discover programs "
    "you may potentially qualify for."
)

st.divider()


# ============================================================
# USER PROFILE
# ============================================================

st.header("👤 Your Information")


col1, col2 = st.columns(2)


with col1:

    age = st.number_input(
        "Age",
        min_value=1,
        max_value=100,
        value=20
    )

    province = st.selectbox(
        "Province / Region",
        [
            "Punjab",
            "Sindh",
            "Balochistan",
            "Khyber Pakhtunkhwa",
            "Islamabad",
            "Gilgit-Baltistan",
            "Azad Jammu & Kashmir"
        ]
    )

    education = st.selectbox(
        "Education Level",
        [
            "school",
            "matric",
            "intermediate",
            "undergraduate",
            "postgraduate"
        ]
    )


with col2:

    student_status = st.selectbox(
        "Are you currently a student?",
        [
            "Yes",
            "No"
        ]
    )

    monthly_income = st.number_input(
        "Monthly Household Income (PKR)",
        min_value=0,
        value=30000,
        step=5000
    )


# ============================================================
# FIND PROGRAMS
# ============================================================

if st.button(
    "🔎 Find Programs",
    type="primary",
    use_container_width=True
):

    with st.spinner("Finding potentially relevant programs..."):

        result = find_programs(
            age=age,
            province=province,
            education=education,
            student_status=student_status,
            monthly_income=monthly_income
        )

    if result["success"]:

        st.session_state.programs = result["programs"]

        # Reset previously selected program
        st.session_state.selected_program = None
        st.session_state.answer = None

    else:

        st.error("Something went wrong while finding programs.")


# ============================================================
# DISPLAY PROGRAMS
# ============================================================

if st.session_state.programs:

    st.divider()

    st.header("🎯 Programs You May Be Eligible For")

    st.info(
        "These programs match the basic criteria in our current "
        "database. This does not guarantee final eligibility."
    )

    st.write(
        f"Found **{len(st.session_state.programs)}** "
        "potentially relevant program(s)."
    )


    # --------------------------------------------------------
    # PROGRAM SELECTION
    # --------------------------------------------------------

    program_names = [
        program["program_name"]
        for program in st.session_state.programs
    ]


    selected_name = st.selectbox(
        "Select a program to learn more:",
        program_names
    )


    # Find selected program dictionary
    selected_program = next(
        program
        for program in st.session_state.programs
        if program["program_name"] == selected_name
    )


    st.session_state.selected_program = selected_program


    # ========================================================
    # SELECTED PROGRAM DETAILS
    # ========================================================

    st.divider()

    st.header("📋 Selected Program")

    st.subheader(
        selected_program["program_name"]
    )


    col1, col2 = st.columns(2)


    with col1:

        st.write(
            f"**Category:** "
            f"{selected_program['category']}"
        )

        st.write(
            f"**Agency:** "
            f"{selected_program['agency']}"
        )

        st.write(
            f"**Benefits:** "
            f"{selected_program['benefits']}"
        )


    with col2:

        st.write(
            f"**Helpline:** "
            f"{selected_program['helpline']}"
        )

        st.write(
            f"**Program ID:** "
            f"{selected_program['program_id']}"
        )


    # ========================================================
    # OFFICIAL SOURCE
    # ========================================================

    st.markdown(
        f"🔗 **Official Source:** "
        f"[Visit Official Website]"
        f"({selected_program['official_url']})"
    )


    # ========================================================
    # ASK AI
    # ========================================================

    st.divider()

    st.header("🤖 Ask AI About This Program")

    st.write(
        "Ask a question about the selected program. "
        "The AI will retrieve information specifically "
        "about this program."
    )


    question = st.text_input(
        "Your question",
        placeholder="e.g. What documents do I need?"
    )


    if st.button(
        "💬 Ask AI",
        type="primary"
    ):

        if not question.strip():

            st.warning(
                "Please enter a question first."
            )

        else:

            with st.spinner(
                "Searching program information..."
            ):

                answer_result = ask_program_question(
                    program=selected_program,
                    question=question
                )


            if answer_result["success"]:

                st.session_state.answer = (
                    answer_result["answer"]
                )

            else:

                st.error(
                    answer_result["answer"]
                )


    # ========================================================
    # DISPLAY AI ANSWER
    # ========================================================

    if st.session_state.answer:

        st.divider()

        st.subheader("🤖 HaqDarmand AI")

        display_text(
            st.session_state.answer
        )


        st.caption(
            "⚠️ This information is for guidance only. "
            "Please verify details through the official "
            "program source before applying."
        )


# ============================================================
# NO PROGRAMS
# ============================================================

elif st.session_state.programs == []:

    # Don't show this immediately on first page load
    # if the user hasn't searched yet.
    pass