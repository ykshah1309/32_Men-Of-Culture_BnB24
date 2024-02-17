import streamlit as st
import re
import spacy

# Set page config to wide layout
st.set_page_config(layout="wide")

def main():
    page = st.session_state.get("page", "Landing")
    user_info = st.session_state.get("user_info", {})  # Retrieve user information from session state
    
    if page == "Landing":
        render_landing_page()
    elif page == "User Information":
        render_user_info_page()
    elif page == "Dashboard":
        render_dashboard(user_info)  # Pass user_info to render_dashboard function

def render_landing_page():
    st.title("Welcome to Career Navigator")
    st.markdown("<p style='font-size: 24px;'>This is where you can start your career journey!</p>", unsafe_allow_html=True)
    if st.button("Continue to User Information"):
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

    # Ask for resume upload
    uploaded_resume = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"], key="resume")

    # Check if all mandatory fields are filled
    mandatory_fields_filled = False
    if name.strip() and email.strip() and college_name.strip() and course_name and uploaded_resume:
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
                "years_worked": years_worked if current_employment == "Yes" else None,
                "uploaded_resume": uploaded_resume
            }
            st.session_state["user_info"] = user_info
            st.session_state["page"] = "Dashboard"
    else:
        st.warning("Please fill in all mandatory fields to proceed to the Dashboard.")

import spacy

# Function to extract skills from the resume text
def extract_skills_from_resume(resume_text):
    # Load English tokenizer, tagger, parser, NER, and word vectors
    nlp = spacy.load("en_core_web_sm")

    # Process the resume text using spaCy
    doc = nlp(resume_text)

    # Initialize an empty set to store extracted skills
    skills = set()

    # Extract skills using NER (Named Entity Recognition) or pattern matching
    for ent in doc.ents:
        if ent.label_ == "SKILL":
            skills.add(ent.text.lower())

    return skills

# Function to suggest job roles based on the extracted skills
def suggest_job_roles(skills):
    # Mapping of job roles to associated skills
    job_role_skills = {
        "Software Engineer": ["programming", "software development", "algorithm design", "data structures"],
        "Network Engineer": ["networking", "routing", "switching", "firewalls"],
        "Database Administrator": ["database management", "sql", "database tuning", "data modeling"],
        "Systems Analyst": ["system analysis", "requirements gathering", "business process modeling"],
        "Cybersecurity Analyst": ["cybersecurity", "penetration testing", "vulnerability assessment"],
        "Data Scientist": ["data analysis", "machine learning", "data visualization", "statistical modeling"],
        "Cloud Architect": ["cloud computing", "aws", "azure", "google cloud platform"],
        "Web Developer": ["web development", "html", "css", "javascript", "front-end", "back-end"],
        "Telecommunication Engineer": ["telecommunication systems", "wireless communication", "telephony protocols"],
        "Signal Processing Engineer": ["signal processing", "digital signal processing", "image processing"],
        "Electronics Engineer": ["analog electronics", "digital electronics", "circuit design", "pcb design"]
    }

    # Initialize a dictionary to store the count of matching skills for each job role
    job_role_counts = {role: 0 for role in job_role_skills}

    # Count the matching skills for each job role
    for skill in skills:
        for role, role_skills in job_role_skills.items():
            if skill in role_skills:
                job_role_counts[role] += 1
    
    # Rank the job roles based on the count of matching skills
    ranked_job_roles = sorted(job_role_counts, key=job_role_counts.get, reverse=True)
    
    # Return only the top 7 ranked job roles
    return ranked_job_roles[:7]

import streamlit as st

import streamlit as st

# Function to analyze the resume
def analyze_resume(resume_text):
    # Extract skills from the resume text
    skills = extract_skills_from_resume(resume_text)

    # Suggest job roles based on the extracted skills
    job_roles = suggest_job_roles(skills)

    return skills, job_roles

# Function to format skills as a string
def format_skills(skills):
    skills_str = ", ".join(skills)
    return f"Skills: {skills_str}"

# Function to format job roles as a string
def format_job_roles(job_roles):
    job_roles_str = ", ".join(job_roles)
    return f"Job Roles: {job_roles_str}"

# Main function to render the dashboard
def render_dashboard(user_info):
    st.title("Dashboard")
    
    # Display user information in sidebar
    st.sidebar.title("User Information")
    st.sidebar.write(f"{user_info['name']}")
    st.sidebar.write(f"{user_info['college_name']}, {user_info['course_name']}, {user_info['study_year']}")

    if user_info.get("company_name") and user_info.get("position"):
        st.sidebar.write(f"{user_info['company_name']}, {user_info['position']}")

    # Add navigation buttons at the bottom of the sidebar
    st.sidebar.markdown("---")
    if st.sidebar.button("Show Resume Analysis"):
        st.session_state["show_resume_analysis"] = True
    
    if st.sidebar.button("Back to User Information"):
        st.session_state["page"] = "User Information"

    if st.session_state.get("show_resume_analysis"):
        uploaded_resume = user_info.get("uploaded_resume")
        if uploaded_resume is not None:
            try:
                resume_text = uploaded_resume.read().decode("utf-8")
                skills, job_roles = analyze_resume(resume_text)

                # Display resume analysis in an expandable panel
                with st.expander("Resume Analysis", expanded=True):
                    if st.button("Evaluate"):
                        try:
                            resume_text = uploaded_resume.read().decode("utf-8")
                            skills, job_roles = analyze_resume(resume_text)
                            st.subheader("Suggested Job Roles")
                            st.write(format_job_roles(job_roles))
                        except UnicodeDecodeError:
                            st.error("Error: Unable to decode the resume text. Please ensure the file format is correct.")

            except UnicodeDecodeError:
                st.error("Error: Unable to decode the resume text. Please ensure the file format is correct.")
        else:
            st.write("Upload your resume to analyze skills and suggest job roles.")

if __name__ == "__main__":
    main()
