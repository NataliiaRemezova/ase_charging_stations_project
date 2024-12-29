import streamlit as st

def display_account():
    # Check if the user is logged in (i.e., user_info is in session_state)
    if 'user_info' in st.session_state and st.session_state.user_info:
        # Show user's profile picture and details
        st.subheader(f"Welcome, {st.session_state.user_info['username']}!")
        st.text(f"Email: {st.session_state.user_info['email']}")

        # Profile Picture upload
        profile_picture = st.file_uploader("Upload Profile Picture", type=['jpg', 'png', 'jpeg'])
        if profile_picture is not None:
            st.image(profile_picture, width=100)
            st.session_state.user_info['profile_picture'] = profile_picture  # Save profile picture in session state
        
        # Edit Profile Section
        st.markdown("### Edit Profile")
        username = st.text_input("Username", value=st.session_state.user_info['username'])
        email = st.text_input("Email", value=st.session_state.user_info['email'])
        
        # Optionally, save the edited profile (update session_state)
        if st.button("Save Profile"):
            st.session_state.user_info['username'] = username
            st.session_state.user_info['email'] = email
            st.success("Profile updated successfully!")

        # Password change section
        st.markdown("### Change Password")
        old_password = st.text_input("Old Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.button("Change Password"):
            if old_password and new_password == confirm_password:
                # Add your logic to update the password (e.g., via API or database)
                st.success("Password updated successfully!")
            else:
                st.error("Password mismatch or missing information.")
        
        # Feedback section
        st.markdown("### Feedback")
        feedback = st.text_area("Share your feedback:")
        
        if st.button("Save Feedback"):
            if feedback:
                # Save feedback in session state
                if st.session_state.user_info['username'] not in st.session_state.user_feedback:
                    st.session_state.user_feedback[st.session_state.user_info['username']] = []
                st.session_state.user_feedback[st.session_state.user_info['username']].append(feedback)
                st.success("Feedback saved successfully!")
            else:
                st.error("Please enter your feedback before submitting.")
        
        # Display feedback history for the user
        st.write("### Your Feedback History")
        if st.session_state.user_info['username'] in st.session_state.user_feedback:
            for fb in st.session_state.user_feedback[st.session_state.user_info['username']]:
                st.write(f"- {fb}")
        
        # Logout button
        if st.button("Log Out"):
            st.session_state.user_info = None
            st.success("Logged out successfully!")
            st.rerun()  # Rerun the app to refresh the page

    else:
        st.write("Please log in to view your account.")
        st.stop()  # Stop further rendering if the user is not logged in
