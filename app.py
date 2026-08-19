# ============================================================
# ============================================================
# START PAGE
# ============================================================
# ============================================================

if st.session_state.page == "start":

    show_header()

    # ========================================================
    # WELCOME
    # ========================================================

    st.subheader(
        "Test your knowledge of Infectious Diseases, "
        "and win a cuddly toy!"
    )

    # ========================================================
    # INSTRUCTIONS
    # ========================================================

    st.markdown(
        """
### 📝 How to play

- You will answer **15 questions** about infectious diseases.
- Each question has **three possible answers**.
- You have **15 seconds to answer each question**.
- Questions are selected randomly.
- The answer choices are also shuffled.
- If you run out of time, the question is counted as unanswered.
- Your final score is the number of correct answers.
- If players have the same score, the **fastest total time wins**.
- Each email address can be used to play **once only**.
        """
    )

    # ========================================================
    # CURRENT TOP 3
    # ========================================================

    st.divider()

    st.subheader(
        "🏆 Current Top 3"
    )

    display_leaderboard(
        top_n=3
    )

    # ========================================================
    # PLAYER DETAILS
    # ========================================================

    st.divider()

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
        "Would you like to receive the SPREAD newsletter?",
        [
            "Please select",
            "Yes",
            "No"
        ]
    )

    st.write("")

    # ========================================================
    # START BUTTON
    # ========================================================

    start_clicked = st.button(
        "START QUIZ",
        type="primary",
        use_container_width=True
    )

    # ========================================================
    # START QUIZ
    # ========================================================

    if start_clicked:

        # ----------------------------------------------------
        # VALIDATE NICKNAME
        # ----------------------------------------------------

        if not nickname.strip():

            st.error(
                "Please enter a nickname."
            )

            st.stop()

        # ----------------------------------------------------
        # VALIDATE EMAIL
        # ----------------------------------------------------

        if not email.strip():

            st.error(
                "Please enter your email address."
            )

            st.stop()

        if "@" not in email or "." not in email:

            st.error(
                "Please enter a valid email address."
            )

            st.stop()

        # ----------------------------------------------------
        # VALIDATE NEWSLETTER
        # ----------------------------------------------------

        if newsletter == "Please select":

            st.error(
                "Please select whether you would like "
                "to receive the SPREAD newsletter."
            )

            st.stop()

        # ----------------------------------------------------
        # CHECK EMAIL
        # ----------------------------------------------------

        try:

            if email_already_used(email):

                st.error(
                    "This email address has already been used "
                    "to play the quiz. Each player can only play once."
                )

                st.stop()

        except Exception as e:

            st.error(
                f"Unable to check the Google Sheet: {e}"
            )

            st.stop()

        # ----------------------------------------------------
        # LOAD QUESTIONS
        # ----------------------------------------------------

        questions = load_questions()

        questions = questions.dropna(
            how="all"
        )

        if len(questions) < QUIZ_LENGTH:

            st.error(
                f"The question bank contains only "
                f"{len(questions)} questions. "
                f"You need at least {QUIZ_LENGTH} questions."
            )

            st.stop()

        # ----------------------------------------------------
        # SELECT QUESTIONS
        # ----------------------------------------------------

        selected_questions = questions.sample(
            n=QUIZ_LENGTH,
            replace=False
        ).reset_index(drop=True)

        st.session_state.quiz_questions = (
            selected_questions
        )

        # ----------------------------------------------------
        # PLAYER INFORMATION
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
        # ----------------------------------------------------

        st.session_state.page = "quiz"

        # ----------------------------------------------------
        # RE-RUN
        # ----------------------------------------------------

        st.rerun()


# ============================================================
# ============================================================
# QUIZ PAGE
# ============================================================
# ============================================================
