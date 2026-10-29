
import streamlit as st
from pathlib import Path
import database

st.set_page_config(
    page_title="TechConnect AI",
    page_icon="💻",
    layout="wide"
)
with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
css_file = Path(__file__).parent / "style.css"

if css_file.exists():
    with open(css_file, "r", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )
else:
    st.warning("style.css file not found!")
# TechConnect - Custom UI Theme
st.markdown("""
<style>
/* Main background */
.stApp {
    background-color: #0B1120;
    color: #F1F5F9;
}

/* Main content spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1100px;
}

/* Main headings */
h1, h2, h3 {
    color: #F8FAFC !important;
}

/* Input fields */
.stTextInput input,
.stSelectbox div[data-baseweb="select"],
.stMultiSelect div[data-baseweb="select"] {
    background-color: #172033;
    border-radius: 10px;
}

/* Buttons */
.stButton button {
    background-color: #06B6D4;
    color: #07111F;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.2rem;
    font-weight: 700;
    transition: 0.2s ease;
}

/* Button hover effect */
.stButton button:hover {
    background-color: #22D3EE;
    color: #07111F;
    border: none;
}

/* Divider */
hr {
    border-color: #263449;
}
</style>
""", unsafe_allow_html=True)


# ---------- SAMPLE STUDENTS ----------
students = [
    {
        "name": "Aarav",
        "year": "1st Year",
        "skills": ["Python", "AI/ML"],
        "interests": ["Artificial Intelligence", "Hackathons"],
        "role": "AI/ML Developer"
    },
    {
        "name": "Priya",
        "year": "1st Year",
        "skills": ["Web Development", "UI/UX Design"],
        "interests": ["Web Development", "Hackathons"],
        "role": "Frontend Developer"
    },
    {
        "name": "Rohan",
        "year": "2nd Year",
        "skills": ["Python", "Data Analysis"],
        "interests": ["Artificial Intelligence", "App Development"],
        "role": "Data Analyst"
    },
    {
        "name": "Ananya",
        "year": "1st Year",
        "skills": ["C/C++", "Python"],
        "interests": ["Robotics", "Hackathons"],
        "role": "Problem Solver"
    },
    {
        "name": "Kabir",
        "year": "2nd Year",
        "skills": ["Web Development", "Python"],
        "interests": ["Web Development", "App Development"],
        "role": "Full-Stack Developer"
    }
]

# ---------- MATCHING ALGORITHM ----------
def calculate_match(user, student):
    user_skills = set(user["skills"])
    other_skills = set(student["skills"])

    user_interests = set(user["interests"])
    other_interests = set(student["interests"])

    # Shared skills and interests
    all_skills = user_skills | other_skills
    all_interests = user_interests | other_interests

    skill_score = (
        len(user_skills & other_skills) / len(all_skills)
        if all_skills else 0
    )

    interest_score = (
        len(user_interests & other_interests) / len(all_interests)
        if all_interests else 0
    )

    # Reward complementary skills too
    complementary_score = (
        len(other_skills - user_skills) / len(other_skills)
        if other_skills else 0
    )

    score = round(
        45 * skill_score
        + 35 * interest_score
        + 20 * complementary_score
    )

    reasons = []

    shared_skills = user_skills & other_skills
    shared_interests = user_interests & other_interests
    new_skills = other_skills - user_skills

    if shared_skills:
        reasons.append(
            "Shared skills: " + ", ".join(sorted(shared_skills))
        )

    if shared_interests:
        reasons.append(
            "Shared interests: " + ", ".join(sorted(shared_interests))
        )

    if new_skills:
        reasons.append(
            "Can contribute additional skills: "
            + ", ".join(sorted(new_skills))
        )

    if not reasons:
        reasons.append("Explore a new collaboration opportunity")

    return score, reasons


# ---------- WEBSITE DESIGN ----------

st.title("🎀 TechConnect AI 💻")
st.caption("✨ Find your people. Build cool stuff. Slay hackathons. 🚀")

st.subheader("Find your people. Build something amazing!")

st.write(
    "An intelligent teammate recommender for hackathons, "
    "AI projects, and coding competitions."
)

st.info(
    "Create your profile to discover students with "
    "compatible skills and interests."
)

st.divider()

st.header("👤 Create Your Student Profile")

with st.form("profile_form"):
    name = st.text_input("Your name")

    year = st.selectbox(
        "Study year",
        ["1st Year", "2nd Year", "3rd Year", "4th Year"]
    )

    skills = st.multiselect(
        "Your skills",
        [
            "Python",
            "AI/ML",
            "Web Development",
            "UI/UX Design",
            "Data Analysis",
            "C/C++",
            "Java",
            "SQL"
        ]
    )

    interests = st.multiselect(
        "Your tech interests",
        [
            "Hackathons",
            "Artificial Intelligence",
            "Web Development",
            "Cybersecurity",
            "Robotics",
            "App Development",
            "Data Science"
        ]
    )

    role = st.selectbox(
        "Your preferred role",
        [
            "AI/ML Developer",
            "Frontend Developer",
            "Backend Developer",
            "Designer",
            "Data Analyst",
            "Problem Solver",
            "Open to any role"
        ]
    )

    submitted = st.form_submit_button("✨ Find My Teammates")

if submitted:
    if not name.strip() or not skills or not interests:
        st.warning(
            "Please enter your name and select at least "
            "one skill and one interest."
        )
    else:
        user = {
            "name": name.strip(),
            "year": year,
            "skills": skills,
            "interests": interests,
            "role": role
        }

        # Do not recommend the user as their own teammate
        candidates = [
            student for student in students
            if student["name"].lower() != name.strip().lower()
        ]

        results = []

        for student in candidates:
            score, reasons = calculate_match(user, student)

            results.append({
                "student": student,
                "score": score,
                "reasons": reasons
            })

        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

       

        st.session_state["user"] = user
        database.save_profile(user)
        st.session_state["results"] = results


# ---------- SHOW RECOMMENDATIONS ----------

if "results" in st.session_state:
    st.divider()
    st.header("💖 Your Potential Teammates")
    st.caption("✨ Find your people. Build cool stuff. Slay hackathons. 🚀")

    st.write(
        "Your matches are ranked by shared skills, shared "
        "interests, and complementary skills. 🫶"
    )

    for rank, result in enumerate(
        st.session_state["results"][:3], start=1
    ):
        student = result["student"]
        score = max(0, min(100, int(result["score"])))

        st.markdown(
            f"""
            <div class="match-card">
                <div class="match-top">
                    <div class="match-name">
                        🎀 #{rank} | {student['name']}
                    </div>
                    <div class="match-badge">
                        💘 {score}% VIBE MATCH
                    </div>
                </div>

                <div class="match-bar-bg">
                    <div class="match-bar-fill"
                         style="width: {score}%;">
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container():
            st.write(f"🎓 **Study year:** {student['year']}")
            st.write(f"🧑‍💻 **Preferred role:** {student['role']}")
            st.write("🛠️ **Skills:** " + " · ".join(student["skills"]))
            st.write("💫 **Interests:** " + " · ".join(student["interests"]))

            st.write("🫶 **Why you might vibe**")
            for reason in result["reasons"]:
                st.write(f"✨ {reason}")

    st.caption(
        "🧪 Prototype: matches use a transparent rule-based "
        "algorithm and sample student profiles. Scores show "
        "profile compatibility, not guaranteed team performance."
    )

st.divider()

# ---------------- CREATE OR JOIN A TEAM ----------------

# Save teams during the current Streamlit session

# Load saved teams from the database
if "teams" not in st.session_state:
    st.session_state["teams"] = database.load_teams()

st.divider()
st.header("👥 Create or Join a Team")
st.caption("💖 Find your crew. Build your next big idea together.")

if "user" not in st.session_state:
    st.info("🎀 Please create your student profile first.")
else:
    current_user = st.session_state["user"]

    create_tab, explore_tab, manage_tab = st.tabs(
        ["✨ Create a Team", "🔎 Explore Teams", "📬 Manage Requests"]
    )

    # 1. CREATE A TEAM
    with create_tab:
        st.subheader("🚀 Start your own team")

        with st.form("create_team_form"):
            team_name = st.text_input(
                "Team name",
                placeholder="e.g. The AI Avengers"
            )

            project_name = st.text_input(
                "Project or hackathon",
                placeholder="e.g. Smart Campus Hackathon"
            )

            description = st.text_area(
                "What will your team build?",
                placeholder="Describe your project idea..."
            )

            needed_skills = st.multiselect(
                "Skills your team needs",
                [
                    "Python", "C", "AI/ML", "Web Development",
                    "UI/UX Design", "Data Analysis", "Research",
                    "Presentation", "IoT", "Cybersecurity"
                ]
            )

            max_members = st.selectbox(
                "Total team size (including you)",
                [2, 3, 4, 5, 6]
            )

            create_button = st.form_submit_button(
                "💗 Create My Team",
                use_container_width=True
            )

        if create_button:
            if not team_name.strip() or not project_name.strip():
                st.error("Please enter a team name and project name.")
            elif not description.strip():
                st.error("Please add a short project description.")
            elif any(
                team["name"].lower() == team_name.strip().lower()
                for team in st.session_state["teams"]
            ):
                st.error("A team with this name already exists.")
            else:
                new_team = {
                    "id": 0,
                    "name": team_name.strip(),
                    "project": project_name.strip(),
                    "description": description.strip(),
                    "skills": needed_skills,
                    "max_members": max_members,
                    "creator": current_user["name"],
                    "members": [current_user["name"]],
                    "requests": []
                }
                
              
                new_team["id"] = database.create_team(new_team)
                st.session_state["teams"] = database.load_teams()
            st.success(
                    f"🎉 Team '{team_name.strip()}' created successfully!"
                )

    # 2. EXPLORE AND JOIN TEAMS
    with explore_tab:
        st.subheader("💫 Discover your next team")

        teams = st.session_state["teams"]

        if not teams:
            st.info("No teams yet. Be the first to create one! 🎀")

        for team in teams:
            with st.container(border=True):
                st.subheader(f"💖 {team['name']}")
                st.caption(f"🚀 Project: {team['project']}")

                st.write(team["description"])
                st.write(f"👑 **Team creator:** {team['creator']}")

                filled = len(team["members"])
                total = team["max_members"]

                st.progress(filled / total)
                st.write(
                    f"👥 **Members:** {filled}/{total} · "
                    f"{total - filled} spot(s) remaining"
                )

                st.write(
                    "**Skills needed:** "
                    + (
                        " · ".join(team["skills"])
                        if team["skills"]
                        else "Open to all skill sets"
                    )
                )

                st.write(
                    "**Current members:** "
                    + " · ".join(team["members"])
                )

                already_member = current_user["name"] in team["members"]
                already_requested = (
                    current_user["name"] in team["requests"]
                )
                is_full = filled >= total

                if already_member:
                    st.info("You're already a member of this team.")
                elif already_requested:
                    st.info("📨 Your join request is pending.")
                elif is_full:
                    st.warning("This team is full.")
                else:
                    if st.button(
                        "💌 Request to Join",
                        key=f"join_team_{team['id']}"
                    ):
                        
                        success, message = database.request_to_join(
                            team["id"], current_user["name"]
                        )

                        if success:
                            st.session_state["teams"] = database.load_teams()
                            st.success(message)
                        else:
                            st.warning(message)

                        st.rerun()


    # 3. MANAGE JOIN REQUESTS
    with manage_tab:
        st.subheader("📬 Your team requests")

        my_teams = [
            team for team in st.session_state["teams"]
            if team["creator"] == current_user["name"]
        ]

        if not my_teams:
            st.info("Create a team first to manage join requests.")
        else:
            for team in my_teams:
                st.markdown(f"### 🎀 {team['name']}")

                if not team["requests"]:
                    st.caption("No pending join requests yet.")
                    continue

                for applicant in team["requests"][:]:
                    st.write(f"👤 **{applicant}** wants to join.")

                    filled = len(team["members"])
                    is_full = filled >= team["max_members"]

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button(
                            "✅ Accept",
                            key=f"accept_{team['id']}_{applicant}",
                            disabled=is_full
                        ):
                            team["members"].append(applicant)
                            team["requests"].remove(applicant)
                            st.success(f"{applicant} joined your team!")
                            st.rerun()

                    with col2:
                        if st.button(
                            "❌ Decline",
                            key=f"decline_{team['id']}_{applicant}"
                        ):
                            team["requests"].remove(applicant)
                            st.info("Request declined.")
                            st.rerun()

                    if is_full:
                        st.caption(
                            "This team is full. Add a spot before accepting."
                        )

# ---------------- AI PROJECT IDEA GENERATOR ----------------

st.divider()
st.header("🚀 AI Project Idea Generator")
st.caption(
    "💗 Turn your team's skills and interests into your next big idea!"
)

project_catalog = [
    {
        "title": "AI Study Buddy",
        "description": "A study assistant that helps students organize topics, "
                       "plan revision, and practice questions.",
        "skills": ["Python", "AI/ML", "Web Development", "Research"],
        "interests": ["Education", "AI", "Productivity"],
        "difficulty": "Beginner",
        "stack": ["Python", "Streamlit", "Pandas"],
        "roles": ["Python developer", "UI designer", "Content researcher"],
        "plan": [
            "Create a page where students enter a subject.",
            "Build a topic and revision checklist.",
            "Add practice questions for each topic.",
            "Test the app with sample subjects."
        ]
    },
    {
        "title": "Smart Campus Assistant",
        "description": "A campus helper that organizes useful information "
                       "about events, facilities, and student resources.",
        "skills": ["Python", "Web Development", "Data Analysis", "UI/UX Design"],
        "interests": ["Education", "Productivity", "Web Apps"],
        "difficulty": "Intermediate",
        "stack": ["Python", "Streamlit", "Pandas"],
        "roles": ["Python developer", "UI/UX designer", "Data researcher"],
        "plan": [
            "List common campus questions and resources.",
            "Create a searchable information page.",
            "Add categories for events and facilities.",
            "Test the search using sample campus information."
        ]
    },
    {
        "title": "Student Skill Matcher",
        "description": "A tool that recommends project teammates based on "
                       "skills, interests, and complementary abilities.",
        "skills": ["Python", "AI/ML", "Data Analysis", "Web Development"],
        "interests": ["AI", "Education", "Web Apps"],
        "difficulty": "Intermediate",
        "stack": ["Python", "Streamlit", "Scikit-learn", "Pandas"],
        "roles": ["Python developer", "Matching algorithm developer",
                  "UI designer"],
        "plan": [
            "Create sample student profiles.",
            "Compare skills and interests between students.",
            "Calculate a compatibility score.",
            "Display ranked recommendations with explanations."
        ]
    },
    {
        "title": "EcoTrack",
        "description": "A sustainability tracker that helps students record "
                       "daily habits and discover ways to reduce waste.",
        "skills": ["Python", "Data Analysis", "UI/UX Design", "Web Development"],
        "interests": ["Environment", "Productivity", "Data"],
        "difficulty": "Beginner",
        "stack": ["Python", "Streamlit", "Pandas", "Matplotlib"],
        "roles": ["Python developer", "Data analyst", "UI designer"],
        "plan": [
            "Choose habits to track, such as reusable bottles.",
            "Create a simple daily entry form.",
            "Display weekly progress using charts.",
            "Suggest small improvements based on recorded habits."
        ]
    },
    {
        "title": "Gesture-Based Safety Alert",
        "description": "A prototype that explores how a detected gesture "
                       "could trigger a safety alert.",
        "skills": ["Python", "AI/ML", "IoT", "Research"],
        "interests": ["AI", "Safety", "Social Impact"],
        "difficulty": "Advanced",
        "stack": ["Python", "OpenCV", "MediaPipe"],
        "roles": ["Computer vision developer", "Python developer",
                  "Research and testing"],
        "plan": [
            "Research gesture detection and privacy considerations.",
            "Test gesture recognition using sample webcam input.",
            "Create a prototype alert screen.",
            "Test false detections and document limitations."
        ]
    },
    {
        "title": "Personal Expense Tracker",
        "description": "A student budgeting tool that records expenses "
                       "and shows spending patterns.",
        "skills": ["Python", "Data Analysis", "Web Development", "UI/UX Design"],
        "interests": ["Finance", "Productivity", "Data"],
        "difficulty": "Beginner",
        "stack": ["Python", "Streamlit", "Pandas", "Matplotlib"],
        "roles": ["Python developer", "Data analyst", "UI designer"],
        "plan": [
            "Create an expense entry form.",
            "Add spending categories and a budget limit.",
            "Display spending summaries and charts.",
            "Test with sample monthly expenses."
        ]
    }
]

with st.form("project_idea_form"):
    idea_skills = st.multiselect(
        "🛠️ What skills does your team have?",
        [
            "Python", "C", "AI/ML", "Web Development",
            "UI/UX Design", "Data Analysis", "Research",
            "Presentation", "IoT", "Cybersecurity"
        ],
        default=["Python", "AI/ML"]
    )

    idea_interests = st.multiselect(
        "💫 What topics interest your team?",
        [
            "AI", "Education", "Productivity", "Web Apps",
            "Data", "Environment", "Finance", "Safety",
            "Social Impact"
        ],
        default=["AI", "Education"]
    )

    idea_level = st.selectbox(
        "🎯 Preferred difficulty",
        ["Any level", "Beginner", "Intermediate", "Advanced"]
    )

    idea_button = st.form_submit_button(
        "✨ Generate Project Ideas",
        use_container_width=True
    )

if idea_button:
    ranked_ideas = []

    for project in project_catalog:
        skill_matches = len(
            set(idea_skills) & set(project["skills"])
        )
        interest_matches = len(
            set(idea_interests) & set(project["interests"])
        )

        score = skill_matches * 2 + interest_matches * 3

        if idea_level != "Any level":
            if project["difficulty"] == idea_level:
                score += 2
            else:
                score -= 2

        ranked_ideas.append((score, project))

    ranked_ideas.sort(key=lambda item: item[0], reverse=True)

    if not idea_skills and not idea_interests:
        st.warning(
            "Choose at least one skill or interest for better suggestions."
        )
    else:
       st.session_state["generated_projects"] = [
          project for score, project in ranked_ideas[:3]
          if score > 0
]

    if not st.session_state["generated_projects"]:
            st.info(
                "Try selecting more skills or interests to find suitable ideas."
            )

if "generated_projects" in st.session_state:
    for number, project in enumerate(
        st.session_state["generated_projects"], start=1
    ):
        with st.container(border=True):
            st.subheader(f"💡 Idea {number}: {project['title']}")
            st.write(project["description"])

            st.write(f"🎯 **Difficulty:** {project['difficulty']}")
            st.write("🛠️ **Suggested tech stack:**")
            st.write(" · ".join(project["stack"]))

            st.write("👥 **Suggested team roles:**")
            for role in project["roles"]:
                st.write(f"• {role}")

            with st.expander("📋 View building plan"):
                for step_number, step in enumerate(
                    project["plan"], start=1
                ):
                    st.write(f"{step_number}. {step}")

            if st.button(
                "💗 Select this idea",
                key=f"select_project_{number}"
            ):
                st.session_state["selected_project"] = project
                st.success(
                    f"Selected '{project['title']}' for your project!"
                )

if "selected_project" in st.session_state:
    selected = st.session_state["selected_project"]
    st.info(f"🌟 Your selected project: {selected['title']}")
