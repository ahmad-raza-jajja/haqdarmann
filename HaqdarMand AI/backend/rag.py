import os
import pandas as pd

from dotenv import load_dotenv

from langchain_core.documents import Document

from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings
)

from langchain_chroma import Chroma


# ==================================================
# ENVIRONMENT
# ==================================================

load_dotenv()

GOOGLE_API_KEY = os.getenv(
    "GOOGLE_API_KEY"
)

if not GOOGLE_API_KEY:

    raise RuntimeError(
        "GOOGLE_API_KEY is not set. Add it to your .env "
        "file before starting the app."
    )

EXCEL_PATH = "programs.xlsx"

CHROMA_PATH = "./chroma_db"

COLLECTION_NAME = "haqdarmand_programs"


# ==================================================
# EMBEDDINGS
# ==================================================

def get_embeddings():

    return GoogleGenerativeAIEmbeddings(

        model=os.getenv(
            "EMBEDDING_MODEL",
            "gemini-embedding-2"
        ),

        google_api_key=GOOGLE_API_KEY
    )


# ==================================================
# CREATE DOCUMENTS
# ==================================================

def create_documents():

    try:

        df = pd.read_excel(
            EXCEL_PATH
        )

    except FileNotFoundError:

        raise FileNotFoundError(
            f"Could not find '{EXCEL_PATH}'. Make sure the "
            "programs spreadsheet is in the project root."
        )

    except Exception as error:

        raise RuntimeError(
            f"Failed to read '{EXCEL_PATH}': {error}"
        )

    documents = []

    for row_index, row in df.iterrows():

        try:

            text = f"""
Program ID:
{row['program_id']}

Program Name:
{row['program_name']}

Urdu Name:
{row['program_name_ur']}

Category:
{row['category']}

Scope:
{row['scope']}

Province:
{row['province']}

Implementing Agency:
{row['implementing_agency']}

Target Beneficiary:
{row['target_beneficiary']}

Minimum Age:
{row['min_age']}

Maximum Age:
{row['max_age']}

Education Level:
{row['education_level']}

Student Status Required:
{row['student_status_required']}

Maximum Monthly Income:
{row['max_monthly_income_pkr']}

Special Criteria:
{row['special_criteria']}

Benefits:
{row['benefits_coverage']}

Required Documents:
{row['required_documents']}

Application Steps:
{row['application_steps']}

Official URL:
{row['official_url']}

Helpline:
{row['helpline']}
"""

            document = Document(

                page_content=text,

                metadata={

                    "program_id": str(
                        row["program_id"]
                    ),

                    "program_name": str(
                        row["program_name"]
                    ),

                    "category": str(
                        row["category"]
                    ),

                    "province": str(
                        row["province"]
                    ),

                    "agency": str(
                        row["implementing_agency"]
                    )
                }
            )

            documents.append(document)

        except Exception as error:

            print(
                f"[SKIPPED ROW {row_index}] "
                f"could not build document: {error}"
            )

            continue

    return documents


# ==================================================
# CREATE VECTOR DATABASE
# ==================================================

def create_vector_database():

    print(
        "No ChromaDB found. "
        "Creating vector database..."
    )

    documents = create_documents()

    if not documents:

        raise RuntimeError(
            "No valid program documents could be built "
            f"from '{EXCEL_PATH}' - check the spreadsheet "
            "for missing/malformed rows."
        )

    print(
        f"Creating embeddings for "
        f"{len(documents)} programs..."
    )

    embeddings = get_embeddings()

    try:

        vectorstore = Chroma.from_documents(

            documents=documents,

            embedding=embeddings,

            persist_directory=CHROMA_PATH,

            collection_name=COLLECTION_NAME
        )

    except Exception as error:

        raise RuntimeError(
            "Failed to build the vector database - check "
            f"your GOOGLE_API_KEY and network connection: "
            f"{error}"
        )

    print(
        "ChromaDB created successfully."
    )

    return vectorstore


# ==================================================
# LOAD VECTOR DATABASE
# ==================================================

def load_vector_database():

    embeddings = get_embeddings()

    try:

        vectorstore = Chroma(

            persist_directory=CHROMA_PATH,

            embedding_function=embeddings,

            collection_name=COLLECTION_NAME
        )

    except Exception as error:

        raise RuntimeError(
            f"Failed to load existing ChromaDB at "
            f"'{CHROMA_PATH}': {error}"
        )

    return vectorstore


# ==================================================
# GET VECTOR DATABASE
# ==================================================

def get_vector_database():

    if os.path.exists(CHROMA_PATH):

        return load_vector_database()

    else:

        return create_vector_database()


# ==================================================
# RETRIEVE SELECTED PROGRAM
# ==================================================

def retrieve_program_context(
    program_id,
    question,
    k=1
):

    vectorstore = get_vector_database()

    results = vectorstore.similarity_search(

        question,

        k=k,

        filter={
            "program_id": str(program_id)
        }
    )

    return results