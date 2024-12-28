import streamlit as st

if 'user_feedback' not in st.session_state:
    st.session_state.user_feedback = {}

def display_account():
    st.subheader("My Account")

    username = st.text_input("Enter your name:")
    profile = st.text_area("Write your profile:")
    if st.button("Save Profile"):
        st.session_state.user_feedback[username].append(profile)
        st.success("Profile saved successfully!")

    st.write("### Display User Feedback")
    for user, feedbacks in st.session_state.user_feedback.items():
        st.write(f"**{user}:**")
        for fb in feedbacks:
            st.write(f"- {fb}")
