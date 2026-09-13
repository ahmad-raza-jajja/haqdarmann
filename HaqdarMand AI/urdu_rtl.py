import re
import streamlit as st


# ==================================================
# URDU DETECTION
# ==================================================

# Matches the Unicode range used by Arabic/Urdu script
URDU_PATTERN = re.compile(r'[\u0600-\u06FF]')


def is_urdu(text):
    """
    Returns True if the given text contains Urdu/Arabic
    script characters. Used to decide whether to render
    the text right-to-left.
    """

    if not text:
        return False

    return bool(URDU_PATTERN.search(text))


# ==================================================
# RTL STYLING (call once, near the top of app.py)
# ==================================================

def inject_urdu_css():

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');

    .urdu-text {
        direction: rtl;
        text-align: right;
        font-family: "Noto Nastaliq Urdu", serif;
        font-size: 1.05rem;
        line-height: 2;
    }
    </style>
    """, unsafe_allow_html=True)


# ==================================================
# DISPLAY HELPER (use this instead of st.markdown
# wherever you're showing AI answers / program text
# that might come back in Urdu)
# ==================================================

def display_text(text):

    if is_urdu(text):

        st.markdown(
            f'<div class="urdu-text">{text}</div>',
            unsafe_allow_html=True
        )

    else:

        st.markdown(text)


# ==================================================
# EXAMPLE USAGE IN app.py
# ==================================================
#
# from urdu_rtl import inject_urdu_css, display_text
#
# inject_urdu_css()   # call once near the top of the script
#
# ...
#
# if st.session_state.answer:
#     st.subheader("HaqDarmand AI")
#     display_text(st.session_state.answer)   # instead of st.markdown(...)
