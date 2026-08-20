import streamlit as st
import pandas as pd
import time
import random
import gspread
from google.oauth2.service_account import Credentials


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="MCID Mosquito Quiz",
    page_icon="🦟",
    layout="centered"
)


# ============================================================
# SETTINGS
# ============================================================

QUIZ_LENGTH = 15
TIME_LIMIT = 20

GOOGLE_SHEET_NAME = "Mosquito Week Leaderboard"

QUESTIONS_FILE = "questions.csv"
LOGO_FILE = "MCID visual.jpg"


# ============================================================
# GOOGLE SHEETS CONNECTION
# ============================================================

def connect_to_google_sheet():

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open(
        GOOGLE_SHEET_NAME
    )

    worksheet = spreadsheet.sheet1

    return worksheet


# ============================================================
# LOAD QUESTIONS
# ============================================================

@st.cache_data
def load_questions():

    return pd.read_csv(
        QUESTIONS_FILE
    )


# ============================================================
# READ GOOGLE SHEET
# ============================================================

def read_sheet():

    worksheet = connect_to_google_sheet()

    values = worksheet.get_all_values()

    if not values:
        return [], []

    headers = values[0]

    valid_indexes = [
        i
        for i, header in enumerate(headers)
        if str(header).strip() != ""
    ]

    clean_headers = [
        str(headers[i]).strip()
        for i in valid_indexes
    ]

    data = []

    for row in values[1:]:

        clean_row = []

        for i in valid_indexes:

            if i < len(row):
                clean_row.append(row[i])
            else:
                clean_row.append("")

        data.append(clean_row)

    return clean_headers, data


# ============================================================
# GET LEADERBOARD
# ============================================================

def get_leaderboard():

    headers, data = read_sheet()

    if not headers:

        return pd.DataFrame(
            columns=[
                "Nickname",
                "Email",
                "SPREAD Newsletter",
                "Score",
                "Total Time"
            ]
        )

    leaderboard = pd.DataFrame(
        data,
        columns=headers
    )

    required_columns = [
        "Nickname",
        "Email",
        "SPREAD Newsletter",
        "Score",
        "Total Time"
    ]

    for column in required_columns:

        if column not in leaderboard.columns:
            leaderboard[column] = ""

    leaderboard["Score"] = pd.to_numeric(
        leaderboard["Score"],
        errors="coerce"
    )

    leaderboard["Total Time"] = pd.to_numeric(
        leaderboard["Total Time"],
        errors="coerce"
    )

    return leaderboard


# ============================================================
# CHECK EMAIL
# ============================================================

def email_already_used(email):

    headers, data = read_sheet()

    if not headers:
        return False

    if "Email" not in headers:
        return False

    email_index = headers.index(
        "Email"
    )

    target_email = (
        email.strip().lower()
    )

    for row in data:

        if email_index < len(row):

            existing_email = (
                str(row[email_index])
                .strip()
                .lower()
            )

            if existing_email == target_email:
                return True

    return False


# ============================================================
# SAVE RESULT
# ============================================================

def save_result(
    nickname,
    email,
    newsletter,
    score,
    total_time
):

    worksheet = connect_to_google_sheet()

    headers = worksheet.row_values(
        1
    )

    headers = [
        str(header).strip()
        for header in headers
    ]

    required_columns = [
        "Nickname",
        "Email",
        "SPREAD Newsletter",
        "Score",
        "Total Time"
    ]

    missing = [
        column
        for column in required_columns
        if column not in headers
    ]

    if missing:

        raise Exception(
            "The Mosquito Week Leaderboard is missing "
            "these column headers: "
            + ", ".join(missing)
            + ". The first row should contain: "
            + ", ".join(required_columns)
        )

    all_values = worksheet.get_all_values()

    next_row = len(all_values) + 1

    new_row = [
        ""
        for _ in headers
    ]

    new_row[
        headers.index("Nickname")
    ] = nickname

    new_row[
        headers.index("Email")
    ] = email

    new_row[
        headers.index("SPREAD Newsletter")
    ] = newsletter

    new_row[
        headers.index("Score")
    ] = int(score)

    new_row[
        headers.index("Total Time")
    ] = round(
        total_time,
        2
    )

    worksheet.update(
        range_name=f"A{next_row}",
        values=[new_row]
    )

    verification = worksheet.row_values(
        next_row
    )

    if not verification:

        raise Exception(
            "The score could not be verified in the "
            "Mosquito Week Leaderboard."
        )

    score_index = headers.index(
        "Score"
    )

    if score_index >= len(verification):

        raise Exception(
            "The score column could not be verified."
        )

    saved_score = str(
        verification[score_index]
    ).strip()

    if saved_score != str(int(score)):

        raise Exception(
            "The score was written but could not "
            "be verified."
        )


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "start"

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = None

if "current_question" not in st.session_state:
    st.session_state.current_question = 0

if "quiz_start_time" not in st.session_state:
    st.session_state.quiz_start_time = None

if "question_start_time" not in st.session_state:
    st.session_state.question_start_time = None

if "nickname" not in st.session_state:
    st.session_state.nickname = ""

if "email" not in st.session_state:
    st.session_state.email = ""

if "newsletter" not in st.session_state:
    st.session_state.newsletter = "Please select"

if "answers" not in st.session_state:
    st.session_state.answers = []

if "score" not in st.session_state:
    st.session_state.score = 0

if "final_time" not in st.session_state:
    st.session_state.final_time = 0

if "result_saved" not in st.session_state:
    st.session_state.result_saved = False

if "current_answers" not in st.session_state:
    st.session_state.current_answers = None

if "answers_for_question" not in st.session_state:
    st.session_state.answers_for_question = None

if "show_timeout" not in st.session_state:
    st.session_state.show_timeout = False

if "timeout_started" not in st.session_state:
    st.session_state.timeout_started = None

if "timeout_recorded_for" not in st.session_state:
    st.session_state.timeout_recorded_for = None

if "start_error" not in st.session_state:
    st.session_state.start_error = ""


# ============================================================
# HEADER
# ============================================================

def show_header():

    col1, col2 = st.columns(
        [1, 4],
        vertical_alignment="center"
    )

    with col1:

        try:

            st.image(
                LOGO_FILE,
                width=90
            )

        except Exception:

            pass

    with col2:

        st.title(
            "MCID Mosquito Quiz 🦟"
        )


# ============================================================
# TOP 3 LEADERBOARD
# ============================================================

def display_top3_leaderboard():

    try:

        leaderboard = get_leaderboard()

    except Exception as e:

        st.error(
            "Unable to load the Mosquito Week Leaderboard: "
            f"{e}"
        )

        return

    if leaderboard.empty:

        st.write(
            "No scores yet. Be the first to play!"
        )

        return

    leaderboard["Score"] = pd.to_numeric(
        leaderboard["Score"],
        errors="coerce"
    )

    leaderboard["Total Time"] = pd.to_numeric(
        leaderboard["Total Time"],
        errors="coerce"
    )

    leaderboard = leaderboard.dropna(
        subset=["Score"]
    )

    if leaderboard.empty:

        st.write(
            "No scores yet. Be the first to play!"
        )

        return

    leaderboard = leaderboard.sort_values(
        by=[
            "Score",
            "Total Time"
        ],
        ascending=[
            False,
            True
        ]
    ).reset_index(
        drop=True
    )

    leaderboard.insert(
        0,
        "Rank",
        range(
            1,
            len(leaderboard) + 1
        )
    )

    top3 = leaderboard.head(
        3
    ).copy()

    public_board = top3[
        [
            "Rank",
            "Nickname",
            "Score",
            "Total Time"
        ]
    ].copy()

    public_board = public_board.rename(
        columns={
            "Total Time": "Time (sec)"
        }
    )

    st.dataframe(
        public_board,
        hide_index=True,
        use_container_width=True
    )


# ============================================================
# FULL LEADERBOARD
# ============================================================

def display_leaderboard():

    try:

        leaderboard = get_leaderboard()

    except Exception as e:

        st.error(
            "Unable to load the Mosquito Week Leaderboard: "
            f"{e}"
        )

        return

    if leaderboard.empty:

        st.write(
            "No scores yet. Be the first to play!"
        )

        return

    leaderboard["Score"] = pd.to_numeric(
        leaderboard["Score"],
        errors="coerce"
    )

    leaderboard["Total Time"] = pd.to_numeric(
        leaderboard["Total Time"],
        errors="coerce"
    )

    leaderboard = leaderboard.dropna(
        subset=["Score"]
    )

    if leaderboard.empty:

        st.write(
            "No scores yet. Be the first to play!"
        )

        return

    leaderboard = leaderboard.sort_values(
        by=[
            "Score",
            "Total Time"
        ],
        ascending=[
            False,
            True
        ]
    ).reset_index(
        drop=True
    )

    leaderboard.insert(
        0,
        "Rank",
        range(
            1,
            len(leaderboard) + 1
        )
    )

    public_board = leaderboard[
        [
            "Rank",
            "Nickname",
            "Score",
            "Total Time"
        ]
    ].copy()

    public_board = public_board.rename(
        columns={
            "Total Time": "Time (sec)"
        }
    )

    st.dataframe(
        public_board,
        hide_index=True,
        use_container_width=True
    )


# ============================================================
# CALCULATE SCORE
# ============================================================

def calculate_score():

    return sum(
        1
        for answer in st.session_state.answers
        if answer["is_correct"]
    )


# ============================================================
# FINISH QUIZ
# ============================================================

def finish_quiz():

    st.session_state.final_time = (
        time.time()
        -
        st.session_state.quiz_start_time
    )

    st.session_state.score = (
        calculate_score()
    )

    st.session_state.page = "results"


# ============================================================
# START PAGE
# ============================================================

if st.session_state.page == "start":

    show_header()

    st.subheader(
        "As its World Mosquito Day, we would like to test "
        "your knowledge of mosquitoes and mosquito-borne "
        "Infectious Disease"
    )

    st.markdown(
        """
### 📝 How to play

- You will answer **15 questions** about mosquitoes and mosquito-borne infectious diseases.
- Each question has **three possible answers**.
- You have **20 seconds to answer each question**.
- Questions are selected randomly.
- The answer choices are also shuffled.
- If you run out of time, the question is counted as unanswered.
- Your final score is the number of correct answers.
- If players have the same score, the **fastest total time wins**.
- Each email address can be used to play **once only**.

### 🏆 Good luck!
        """
    )

    st.divider()

    # --------------------------------------------------------
    # PLAYER DETAILS
    # --------------------------------------------------------

    nickname = st.text_input(
        "Nickname",
        value=st.session_state.nickname,
        placeholder="Enter your nickname"
    )

    email = st.text_input(
        "Email address",
        value=st.session_state.email,
        placeholder="Enter your email address"
    )

    newsletter = st.selectbox(
        'Would you like to receive the MCID\'s newsletter "the SPREAD"?',
        [
            "Please select",
            "Yes",
            "No"
        ]
    )

    # --------------------------------------------------------
    # MCID WEBPAGE
    # --------------------------------------------------------

    st.markdown(
        'To find out more about the MCID, please check out our '
        '[webpage](https://mcid.unibe.ch).'
    )

    st.write("")

    # --------------------------------------------------------
    # ERROR MESSAGE
    # --------------------------------------------------------

    if st.session_state.start_error:

        st.error(
            st.session_state.start_error
        )

    # --------------------------------------------------------
    # START BUTTON
    # --------------------------------------------------------

    start_clicked = st.button(
        "START QUIZ",
        type="primary",
        use_container_width=True
    )

    # --------------------------------------------------------
    # TOP 3
    # --------------------------------------------------------

    st.write("")

    st.subheader(
        "🏆 Top 3"
    )

    display_top3_leaderboard()

    # --------------------------------------------------------
    # START QUIZ
    # --------------------------------------------------------

    if start_clicked:

        # Clear any previous error

        st.session_state.start_error = ""

        # ----------------------------------------------------
        # VALIDATE NICKNAME
        # ----------------------------------------------------

        if not nickname.strip():

            st.session_state.start_error = (
                "Please enter a nickname."
            )

            st.rerun()

        # ----------------------------------------------------
        # VALIDATE EMAIL
        # ----------------------------------------------------

        if not email.strip():

            st.session_state.start_error = (
                "Please enter your email address."
            )

            st.rerun()

        if "@" not in email or "." not in email:

            st.session_state.start_error = (
                "Please enter a valid email address."
            )

            st.rerun()

        # ----------------------------------------------------
        # VALIDATE NEWSLETTER
        # ----------------------------------------------------

        if newsletter == "Please select":

            st.session_state.start_error = (
                "Please select whether you would like "
                "to receive the MCID's newsletter."
            )

            st.rerun()

        # ----------------------------------------------------
        # CHECK EMAIL
        # ----------------------------------------------------

        try:

            if email_already_used(email):

                st.session_state.start_error = (
                    "This email address has already been used "
                    "to play the quiz. Each player can only "
                    "play once."
                )

                st.rerun()

        except Exception as e:

            st.session_state.start_error = (
                "Unable to check the Mosquito Week "
                f"Leaderboard: {e}"
            )

            st.rerun()

        # ----------------------------------------------------
        # LOAD QUESTIONS
        # ----------------------------------------------------

        try:

            questions = load_questions()

        except Exception as e:

            st.session_state.start_error = (
                f"Unable to load the questions: {e}"
            )

            st.rerun()

        questions = questions.dropna(
            how="all"
        )

        if len(questions) < QUIZ_LENGTH:

            st.session_state.start_error = (
                f"The question bank contains only "
                f"{len(questions)} questions. "
                f"You need at least {QUIZ_LENGTH} questions."
            )

            st.rerun()

        # ----------------------------------------------------
        # SELECT QUESTIONS
        # ----------------------------------------------------

        selected_questions = questions.sample(
            n=QUIZ_LENGTH,
            replace=False
        ).reset_index(
            drop=True
        )

        st.session_state.quiz_questions = (
            selected_questions
        )

        # ----------------------------------------------------
        # SAVE PLAYER INFORMATION
        # ----------------------------------------------------

        st.session_state.nickname = (
            nickname.strip()
        )

        st.session_state.email = (
            email.strip()
        )

        st.session_state.newsletter = (
            newsletter
        )

        # ----------------------------------------------------
        # RESET QUIZ
        # ----------------------------------------------------

        st.session_state.current_question = 0

        st.session_state.answers = []

        st.session_state.score = 0

        st.session_state.final_time = 0

        st.session_state.result_saved = False

        st.session_state.current_answers = None

        st.session_state.answers_for_question = None

        st.session_state.show_timeout = False

        st.session_state.timeout_started = None

        st.session_state.timeout_recorded_for = None

        # ----------------------------------------------------
        # START TIMERS
        # ----------------------------------------------------

        now = time.time()

        st.session_state.quiz_start_time = now

        st.session_state.question_start_time = now

        # ----------------------------------------------------
        # CHANGE PAGE
        #
        # THIS IS THE IMPORTANT PART.
        #
        # We go directly from start to quiz.
        # There is no page container and no blank page.
        # ----------------------------------------------------

        st.session_state.page = "quiz"

        st.rerun()


# ============================================================
# QUIZ PAGE
# ============================================================

elif st.session_state.page == "quiz":

    show_header()

    # --------------------------------------------------------
    # GET QUESTIONS
    # --------------------------------------------------------

    questions = (
        st.session_state.quiz_questions
    )

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if questions is None:

        st.session_state.page = "start"

        st.rerun()

    question_number = (
        st.session_state.current_question
    )

    # --------------------------------------------------------
    # CHECK WHETHER QUIZ IS COMPLETE
    # --------------------------------------------------------

    if question_number >= QUIZ_LENGTH:

        finish_quiz()

        st.rerun()

    # --------------------------------------------------------
    # TIMEOUT SCREEN
    # --------------------------------------------------------

    if st.session_state.show_timeout:

        st.subheader(
            f"Question {question_number + 1} "
            f"of {QUIZ_LENGTH}"
        )

        st.error(
            "⏰ TIME'S UP!"
        )

        if (
            time.time()
            -
            st.session_state.timeout_started
            >= 1
        ):

            st.session_state.show_timeout = False

            st.session_state.timeout_started = None

            st.session_state.current_question += 1

            st.session_state.current_answers = None

            st.session_state.answers_for_question = None

            st.session_state.timeout_recorded_for = None

            if (
                st.session_state.current_question
                >= QUIZ_LENGTH
            ):

                finish_quiz()

            else:

                st.session_state.question_start_time = (
                    time.time()
                )

            st.rerun()

        else:

            time.sleep(0.1)

            st.rerun()

    # --------------------------------------------------------
    # GET CURRENT QUESTION
    # --------------------------------------------------------

    question = questions.iloc[
        question_number
    ]

    question_text = str(
        question.iloc[0]
    )

    option_a = str(
        question.iloc[1]
    )

    option_b = str(
        question.iloc[2]
    )

    option_c = str(
        question.iloc[3]
    )

    correct_answer = str(
        question.iloc[4]
    )

    # --------------------------------------------------------
    # QUESTION NUMBER
    # --------------------------------------------------------

    st.subheader(
        f"Question {question_number + 1} "
        f"of {QUIZ_LENGTH}"
    )

    # --------------------------------------------------------
    # TIMER
    # --------------------------------------------------------

    elapsed = (
        time.time()
        -
        st.session_state.question_start_time
    )

    remaining = max(
        0,
        TIME_LIMIT - int(elapsed)
    )

    st.markdown(
        f"## ⏱️ {remaining} seconds"
    )

    # --------------------------------------------------------
    # TIMEOUT CHECK
    # --------------------------------------------------------

    if elapsed >= TIME_LIMIT:

        if (
            st.session_state.timeout_recorded_for
            != question_number
        ):

            st.session_state.answers.append({

                "question": question_text,

                "answer": "No answer",

                "correct": correct_answer,

                "is_correct": False

            })

            st.session_state.timeout_recorded_for = (
                question_number
            )

        st.session_state.show_timeout = True

        st.session_state.timeout_started = (
            time.time()
        )

        st.rerun()

    # --------------------------------------------------------
    # QUESTION TEXT
    # --------------------------------------------------------

    st.write("")

    st.markdown(
        f"### {question_text}"
    )

    st.write("")

    # --------------------------------------------------------
    # SHUFFLE ANSWERS ONCE
    # --------------------------------------------------------

    if (
        st.session_state.answers_for_question
        != question_number
    ):

        answers = [
            option_a,
            option_b,
            option_c
        ]

        random.shuffle(
            answers
        )

        st.session_state.current_answers = (
            answers
        )

        st.session_state.answers_for_question = (
            question_number
        )

    answers = (
        st.session_state.current_answers
    )

    # --------------------------------------------------------
    # ANSWER BUTTONS
    # --------------------------------------------------------

    for answer_index, answer in enumerate(
        answers
    ):

        if st.button(
            answer,
            use_container_width=True,
            key=f"question_{question_number}_answer_{answer_index}"
        ):

            is_correct = (
                str(answer)
                .strip()
                .lower()
                ==
                str(correct_answer)
                .strip()
                .lower()
            )

            st.session_state.answers.append({

                "question": question_text,

                "answer": answer,

                "correct": correct_answer,

                "is_correct": is_correct

            })

            # ------------------------------------------------
            # MOVE TO NEXT QUESTION
            # ------------------------------------------------

            st.session_state.current_question += 1

            st.session_state.question_start_time = (
                time.time()
            )

            st.session_state.current_answers = None

            st.session_state.answers_for_question = None

            st.session_state.timeout_recorded_for = None

            # ------------------------------------------------
            # FINISHED?
            # ------------------------------------------------

            if (
                st.session_state.current_question
                >= QUIZ_LENGTH
            ):

                finish_quiz()

            st.rerun()

    # --------------------------------------------------------
    # REFRESH COUNTDOWN
    # --------------------------------------------------------

    time.sleep(1)

    st.rerun()


# ============================================================
# RESULTS PAGE
# ============================================================

elif st.session_state.page == "results":

    show_header()

    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    score = calculate_score()

    st.session_state.score = score

    final_time = (
        st.session_state.final_time
    )

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    st.subheader(
        "🎉 Quiz complete!"
    )

    st.markdown(
        f"## {score} / {QUIZ_LENGTH}"
    )

    st.write(
        f"Your total time was "
        f"**{final_time:.2f} seconds**."
    )

    # --------------------------------------------------------
    # YOUR ANSWERS
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "📝 Your answers"
    )

    results_table = []

    for number, answer_data in enumerate(
        st.session_state.answers,
        start=1
    ):

        results_table.append({

            "#": number,

            "Question": answer_data["question"],

            "Your answer": answer_data["answer"],

            "Correct answer": answer_data["correct"],

            "Result": (
                "✅"
                if answer_data["is_correct"]
                else "❌"
            )

        })

    if results_table:

        results_df = pd.DataFrame(
            results_table
        )

        st.dataframe(
            results_df,
            hide_index=True,
            use_container_width=True
        )

    # --------------------------------------------------------
    # SAVE SCORE
    # --------------------------------------------------------

    if not st.session_state.result_saved:

        try:

            save_result(
                nickname=st.session_state.nickname,
                email=st.session_state.email,
                newsletter=st.session_state.newsletter,
                score=score,
                total_time=final_time
            )

            st.session_state.result_saved = True

            st.success(
                "Your score has been added to the "
                "Mosquito Day leaderboard!"
            )

        except Exception as e:

            st.error(
                f"Problem saving your score: {e}"
            )

    else:

        st.success(
            "Your score has been added to the "
            "Mosquito Day leaderboard!"
        )

    # --------------------------------------------------------
    # FULL LEADERBOARD
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "🏆 Mosquito Day Leaderboard"
    )

    display_leaderboard()

    # --------------------------------------------------------
    # THANK YOU
    # --------------------------------------------------------

    st.write("")

    st.info(
        "Thanks for taking part in the MCID Mosquito Quiz!"
    )
