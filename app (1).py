import streamlit as st
import re

# Set page config to wide layout
st.set_page_config(layout="wide")

# Define custom CSS styles for dark theme
# Add custom CSS styles
st.markdown(
    """
    <style>
        /* Add custom styles here */
        .title-text {
            color: blue; /* Change font color to blue */
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 20px;
            font-family: Arial, sans-serif;
        }
        .input-text, .stTextInput > div > div > div > input {
            background-color: transparent !important; /* Make input boxes transparent */
            border: 1px solid blue; /* Add blue outline to input boxes */
            color: blue; /* Change font color to blue */
        }
        .stTextInput > div > div > div > input:focus {
            box-shadow: 0 0 0 2px lightgreen; /* Add green shadow when input box is selected */
        }
        .stButton > button {
            background-color: transparent !important; /* Make buttons transparent */
            border: 1px solid blue; /* Add blue outline to buttons */
            color: blue; /* Change font color to blue */
        }
        .stButton > button:hover {
            box-shadow: 0 0 0 2px lightgreen; /* Add green shadow when button is hovered */
        }
    </style>
    """,
    unsafe_allow_html=True
)


def main():
    page = st.session_state.get("page", "Launch")
    user_info = st.session_state.get("user_info", {})  # Retrieve user information from session state
    
    if page == "Launch":
        render_launch_page()
    elif page == "User Information":
        render_user_info_page()
    elif page == "Dashboard":
        render_dashboard(user_info)  # Pass user_info to render_dashboard function

def render_launch_page():
    st.title("Welcome to Career Navigator")
    st.markdown("<p style='font-size: 24px;'>This is where you can start your career journey!</p>", unsafe_allow_html=True)
    if st.button("Continue"):
        st.session_state["page"] = "User Information"

def render_user_info_page():
    st.title("User Information")

    # Input fields for user name and email
    name = st.text_input("Enter your name:")
    email = st.text_input("Enter your email:")
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        st.error("Please enter a valid email address.")
        return

    # Determine if the user is an undergraduate or graduate
    is_undergraduate = st.radio("Are you an undergraduate or graduate?", ("Undergraduate", "Graduate"))

    # Ask for college name and course name
    if is_undergraduate == "Undergraduate":
        college_name = st.text_input("Enter your undergraduate college name:")
        course_name = st.selectbox("Select your undergraduate course:", ["BTech. Computer Engineering", "BTech. EXTC", "BTech. Information Technology"])
        is_studying = st.radio("Are you currently studying?", ("Yes", "No"))
        if is_studying == "Yes":
            study_year = st.number_input("Enter the year of study:", min_value=1, max_value=4, step=1)
        else:
            study_year = "Passed"
    else:
        college_name = st.text_input("Enter your graduate college name:")
        course_name = st.selectbox("Select your graduate course:", ["BTech. Computer Engineering", "BTech. EXTC", "BTech. Information Technology"])
        is_studying = st.radio("Are you currently studying?", ("Yes", "No"))
        if is_studying == "Yes":
            study_year = st.number_input("Enter the year of study:", min_value=1, max_value=4, step=1)
        else:
            study_year = "Passed"

    # Ask about internships if applicable
    internships_done = False
    internship_company = None
    internship_role = None
    internship_duration = None
    if is_studying == "Yes":
        internships_done = st.radio("Have you done any internships?", ("Yes", "No"))
        if internships_done == "Yes":
            internship_company = st.text_input("Enter the company name of your internship:")
            internship_role = st.text_input("Enter your role during the internship:")
            internship_duration = st.number_input("Enter the duration of internship (in months):", min_value=1)

    # Ask about current employment if applicable
    current_employment = None
    if is_studying == "No":
        internships_done = st        .radio("Have you done any internships?", ("Yes", "No"))
        if internships_done == "Yes":
            internship_company = st.text_input("Enter the company name of your internship:")
            internship_role = st.text_input("Enter your role during the internship:")
            internship_duration = st.number_input("Enter the duration of internship (in months):", min_value=1)

        current_employment = st.radio("Are you currently employed?", ("Yes", "No"))
        if current_employment == "Yes":
            company_name = st.text_input("Enter your current company name:")
            position = st.text_input("Enter your current position:")
            years_worked = st.number_input("Enter how many years you've worked:", min_value=0)

    # Check if all mandatory fields are filled
    mandatory_fields_filled = False
    if name.strip() and email.strip() and college_name.strip() and course_name:
        if is_studying == "Yes":
            if internships_done == "Yes":
                if internship_company.strip() and internship_role.strip() and internship_duration:
                    mandatory_fields_filled = True
            else:
                mandatory_fields_filled = True
        elif is_studying == "No":
            if current_employment == "Yes":
                if company_name.strip() and position.strip() and years_worked:
                    mandatory_fields_filled = True
            else:
                mandatory_fields_filled = True

    # Proceed to Dashboard if all mandatory fields are filled
    if mandatory_fields_filled:
        if st.button("Proceed to Dashboard"):
            user_info = {
                "name": name,
                "email": email,
                "college_name": college_name,
                "course_name": course_name,
                "is_undergraduate": is_undergraduate,
                "study_year": study_year,
                "internship_company": internship_company,
                "internship_role": internship_role,
                "internship_duration": internship_duration,
                "current_employment": current_employment,
                "company_name": company_name if current_employment == "Yes" else None,
                "position": position if current_employment == "Yes" else None,
                "years_worked": years_worked if current_employment == "Yes" else None
            }
            st.session_state["user_info"] = user_info
            st.session_state["page"] = "Dashboard"
    else:
        st.warning("Please fill in all mandatory fields to proceed to the Dashboard.")

def render_dashboard(user_info):
    st.title("Dashboard")
    
    # Retrieve user information from session state
    name = user_info.get("name", "")
    is_undergraduate = user_info.get("is_undergraduate", False)
    is_studying = user_info.get("is_studying", False)
    college_name = user_info.get("college_name", "")
    course_name = user_info.get("course_name", "")
    study_year = user_info.get("study_year", "")
    company_name = user_info.get("company_name", "")
    position = user_info.get("position", "")

    # Display user information in sidebar
    st.sidebar.title("User Information")
    st.sidebar.write(f"{name}")

    if is_undergraduate and is_studying:
        st.sidebar.write(f"{college_name}, {course_name}, {study_year}")
    elif not is_undergraduate and is_studying:
        st.sidebar.write(f"{college_name}, {course_name}, {study_year}")
    elif is_undergraduate and not is_studying:
        st.sidebar.write(f"{college_name}, {course_name}")
    elif not is_undergraduate and not is_studying:
        st.sidebar.write(f"{college_name}, {course_name}")

    if company_name and position:
        st.sidebar.write(f"{company_name}, {position}")
    
    # Add button to upload resume in the sidebar
    uploaded_file = st.sidebar.file_uploader("Upload your resume", type=["pdf", "docx"])
    
    # Add navigation tab at the bottom of the sidebar
    st.sidebar.markdown("---")
    if st.sidebar.button("Back to User Information"):
        st.session_state["page"] = "User Information"
    
    # Add dashboard content here
    st.write("Welcome to your personalized dashboard!")

if __name__ == "__main__":
    main()

