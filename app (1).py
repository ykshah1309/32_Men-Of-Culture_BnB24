import streamlit as st
import re
import spacy
import requests 
from bs4 import BeautifulSoup
from pyecharts import options as opts
from pyecharts.charts import Bar
from streamlit_echarts import st_pyecharts
import random
import base64
import time
from hugchat import hugchat
from hugchat.login import Login
from dotenv import dotenv_values
import subprocess
import pickle
import json 

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
    elif page == "ChatBot":
        render_chat_page()

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Set background image
set_background('/content/back.png')
st.markdown("""
    <style>
        [data-testid=stSidebar] {
            background-color: #00000000;
        }
    </style>
    """, unsafe_allow_html=True)

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

def scrape_coursera_courses(job_roles):
    courses = []
    ds_course = [['Machine Learning Crash Course by Google [Free]', 'https://developers.google.com/machine-learning/crash-course'],
                 ['Machine Learning A-Z by Udemy','https://www.udemy.com/course/machinelearning/'],
                 ['Machine Learning by Andrew NG','https://www.coursera.org/learn/machine-learning'],
                 ['Data Scientist Master Program of Simplilearn (IBM)','https://www.simplilearn.com/big-data-and-analytics/senior-data-scientist-masters-program-training'],
                 ['Data Science Foundations: Fundamentals by LinkedIn','https://www.linkedin.com/learning/data-science-foundations-fundamentals-5'],
                 ['Data Scientist with Python','https://www.datacamp.com/tracks/data-scientist-with-python'],
                 ['Programming for Data Science with Python','https://www.udacity.com/course/programming-for-data-science-nanodegree--nd104'],
                 ['Programming for Data Science with R','https://www.udacity.com/course/programming-for-data-science-nanodegree-with-R--nd118'],
                 ['Introduction to Data Science','https://www.udacity.com/course/introduction-to-data-science--cd0017'],
                 ['Intro to Machine Learning with TensorFlow','https://www.udacity.com/course/intro-to-machine-learning-with-tensorflow-nanodegree--nd230']]

    web_course = [['Django Crash course [Free]','https://youtu.be/e1IyzVyrLSU'],
                  ['Python and Django Full Stack Web Developer Bootcamp','https://www.udemy.com/course/python-and-django-full-stack-web-developer-bootcamp'],
                  ['React Crash Course [Free]','https://youtu.be/Dorf8i6lCuk'],
                  ['ReactJS Project Development Training','https://www.dotnettricks.com/training/masters-program/reactjs-certification-training'],
                  ['Full Stack Web Developer - MEAN Stack','https://www.simplilearn.com/full-stack-web-developer-mean-stack-certification-training'],
                  ['Node.js and Express.js [Free]','https://youtu.be/Oe421EPjeBE'],
                  ['Flask: Develop Web Applications in Python','https://www.educative.io/courses/flask-develop-web-applications-in-python'],
                  ['Full Stack Web Developer by Udacity','https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd0044'],
                  ['Front End Web Developer by Udacity','https://www.udacity.com/course/front-end-web-developer-nanodegree--nd0011'],
                  ['Become a React Developer by Udacity','https://www.udacity.com/course/react-nanodegree--nd019']]

    android_course = [['Android Development for Beginners [Free]','https://youtu.be/fis26HvvDII'],
                      ['Android App Development Specialization','https://www.coursera.org/specializations/android-app-development'],
                      ['Associate Android Developer Certification','https://grow.google/androiddev/#?modal_active=none'],
                      ['Become an Android Kotlin Developer by Udacity','https://www.udacity.com/course/android-kotlin-developer-nanodegree--nd940'],
                      ['Android Basics by Google','https://www.udacity.com/course/android-basics-nanodegree-by-google--nd803'],
                      ['The Complete Android Developer Course','https://www.udemy.com/course/complete-android-n-developer-course/'],
                      ['Building an Android App with Architecture Components','https://www.linkedin.com/learning/building-an-android-app-with-architecture-components'],
                      ['Android App Development Masterclass using Kotlin','https://www.udemy.com/course/android-oreo-kotlin-app-masterclass/'],
                      ['Flutter & Dart - The Complete Flutter App Development Course','https://www.udemy.com/course/flutter-dart-the-complete-flutter-app-development-course/'],
                      ['Flutter App Development Course [Free]','https://youtu.be/rZLR5olMR64']]

    # Coursera URL for job role search
    url = "https://www.coursera.org/search?query={}&index=prod_all_products_term_optimization".format("+".join(job_roles))

    # Send GET request
    response = requests.get(url)
    if response.status_code == 200:
        # Parse HTML content
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract course information
        course_cards = soup.find_all("li", class_="ais-InfiniteHits-item")
        for card in course_cards:
            title1 = card.find("h2", class_="color-primary-text headline-1-text flex-1").text.strip()
            description = card.find("div", class_="partner-banner--content").text.strip()
            link1 = "https://www.coursera.org" + card.find("a")["href"]
            #courses.append({"title": title, "description": description, "link": link})
        
        if job_roles == "Systems Analyst" or "Database Administrator" or "Systems Analyst" or "Cybersecurity Analyst" or "Data Scientist":
            transformed_array = [{'title': item[0], 'link': item[1]} for item in ds_course]
            courses = ds_course
        elif job_roles == "Software Engineer":
            transformed_array = [{'title': item[0], 'link': item[1]} for item in web_course]
            courses = web_course
    
    return courses

import openai
from openai import OpenAI
# Set your OpenAI API key
OPENAI_API_KEY = "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"
def render_chat_page():
    st.title("CarrerGuide at your assistence!")

    # Set OpenAI API key from Streamlit secrets
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Set a default model
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Display assistant response in chat message container
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})

def render_dashboard(user_info):
    st.title("Dashboard")
    
    # Display user information in sidebar
    st.sidebar.title(f"{user_info['name']}")
    st.sidebar.subheader(f"{user_info['college_name']}")
    st.sidebar.subheader(f"{user_info['course_name']}")

    if user_info.get("company_name") and user_info.get("position"):
        st.sidebar.subheader(f"{user_info['company_name']}")
        st.sidebar.subheader(f"{user_info['position']}")

    # Add navigation buttons at the bottom of the sidebar
    st.sidebar.markdown("---")
    st.sidebar.write("")
    if st.sidebar.button("Evaluate User Details"):
        st.session_state["show_resume_analysis"] = True
    
    st.sidebar.write("")
    if st.sidebar.button("Chat-Assist"):
        st.session_state["page"] = "ChatBot"

    st.sidebar.write("") 
    if st.sidebar.button("Back to User Information"):
        st.session_state["page"] = "User Information"
        st.session_state["show_resume_analysis"] = False
        st.session_state["show_course_recommendation"] = False

    # Main section
    b = (
        Bar()
        .add_xaxis(["Software Engineer", "Data Scientist", "Network Engineer", "Database Administrator", "Systems Analyst", "Cybersecurity Analyst", "Data Scientist", "Cloud Architect"])
        .add_yaxis("2022-2023 Median Salary in ($)", [120000, 125000, 95000, 90000, 85000, 100000, 130000])
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="Job Role Trend", subtitle="2022-2023 Trend"
            ),
            toolbox_opts=opts.ToolboxOpts(),
        )
    )
    st_pyecharts(b)

    with st.expander("Resume Analysis and Course Recommendations", expanded=True):
        uploaded_resume = user_info.get("uploaded_resume")
        if uploaded_resume is not None:
            try:
                resume_text = uploaded_resume.read().decode("utf-8")
                skills, job_roles = analyze_resume(resume_text)

                # Display resume analysis
                st.subheader("Resume Analysis")
                if st.button("Evaluate Resume"):
                    try:
                        st.write(format_job_roles(job_roles))
                    except UnicodeDecodeError:
                        st.error("Error: Unable to decode the resume text. Please ensure the file format is correct.")

                # Scrape Coursera courses based on job roles
                    if job_roles:
                        courses = scrape_coursera_courses(job_roles)
                        # Display course recommendations
                        st.subheader("Recommended Courses")
                        if courses:
                            for course in courses:
                                st.write(courses)
                                st.markdown("---")
                        else:
                            st.write("No courses found for the given job roles.")

            except UnicodeDecodeError:
                st.error("Error: Unable to decode the resume text. Please ensure the file format is correct.")
        else:
            st.write("Upload your resume to analyze skills and suggest job roles.")
    
if __name__ == "__main__":
    main()
