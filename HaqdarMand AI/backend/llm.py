import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:

    raise RuntimeError(
        "GOOGLE_API_KEY is not set. Add it to your .env "
        "file before starting the app."
    )

llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite"),
    google_api_key=GOOGLE_API_KEY,
    temperature=0.2
)


def ask_about_program(program, question, retrieved_context):

    # Combine retrieved RAG documents
    context_text = "\n\n".join(
        document.page_content
        for document in retrieved_context
    )

    prompt = f"""
You are HaqDarmand AI.

You help people in Pakistan understand
scholarships, financial assistance, and
health-support programs.

The user has already been identified as
potentially matching this program's basic
structured eligibility criteria.

You are now answering a QUESTION ABOUT
THIS SPECIFIC PROGRAM.

IMPORTANT RULES:

1. Answer ONLY using the RETRIEVED PROGRAM
   INFORMATION provided below.

2. Every factual statement in your answer must
   be directly supported by the retrieved
   program information.

3. Do NOT use your general knowledge about the
   program, even if you recognize the program name.

4. Do NOT invent information.

5. Do NOT invent eligibility requirements.

6. Do NOT invent benefits.

7. Do NOT invent documents.

8. Do NOT invent application procedures.

9. If the retrieved information does not contain
   the answer to the user's question, say:

   "I don't have this information in the current
   program data."

10. Do not make a definitive eligibility claim.
    Use "potentially eligible" or "may be eligible".

11. Keep the answer simple and easy to understand.

12. If the user asks in Urdu, respond in Urdu.
    If the user asks in English, respond in English.

13. When appropriate, remind the user to verify
    the information through the official source.

14. Do not answer about a different program.

--------------------------------------------------
SELECTED PROGRAM
--------------------------------------------------

Program Name:
{program["program_name"]}

Category:
{program["category"]}

Agency:
{program["agency"]}

Official URL:
{program["official_url"]}

--------------------------------------------------
USER QUESTION
--------------------------------------------------

{question}

--------------------------------------------------
RETRIEVED PROGRAM INFORMATION
--------------------------------------------------

{context_text}

--------------------------------------------------
ANSWER
--------------------------------------------------

Give a direct answer to the user's question.

Use ONLY information contained in the retrieved
program information above.

Do not provide unnecessary information.
"""

    # Ask Gemini
    try:

        response = llm.invoke(prompt)

    except Exception as error:

        print(f"[LLM ERROR] Gemini call failed: {error}")

        raise RuntimeError(
            "Gemini call failed"
        ) from error

    # -----------------------------------------
    # EXTRACT CLEAN TEXT FROM GEMINI RESPONSE
    # -----------------------------------------

    content = response.content

    # Case 1: Gemini directly returns a string
    if isinstance(content, str):
        return content

    # Case 2: Gemini returns a list of dictionaries
    #
    # Example:
    # [
    #     {
    #         "type": "text",
    #         "text": "The program provides..."
    #     }
    # ]
    if isinstance(content, list):

        text_parts = []

        for item in content:

            if isinstance(item, dict):

                if item.get("type") == "text":

                    text = item.get("text", "")

                    if text:
                        text_parts.append(text)

        if text_parts:
            return "\n".join(text_parts)

    # Fallback
    return str(content)