import streamlit as st
from supabase import create_client, Client
from geopy.distance import geodesic
from datetime import datetime

# --- Set up page ---
st.set_page_config(page_title="Amorly Dating App", page_icon="💕")

# --- Supabase setup ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- Handle email confirmation redirect ---
query_params = st.query_params
redirect_type = query_params.get("type")

if redirect_type == "signup":
    st.success("✅ Your email has been confirmed. Please log in.")
    supabase.auth.sign_out()

# --- Auth: Login / Sign Up ---
st.title("💕 Amorly Dating App")
st.subheader("Log in or Sign up")
email = st.text_input("Email")
password = st.text_input("Password", type="password")
action = st.radio("Action", ["Login", "Sign Up"])

if st.button("Submit"):
    if action == "Login":
        try:
            result = supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.success("Login successful!")
        except Exception as e:
            st.error(f"Login failed: {e}")
    else:
        try:
            result = supabase.auth.sign_up({"email": email, "password": password})
            st.success("Sign Up successful! Please check your email to confirm.")
        except Exception as e:
            st.error(f"Sign up failed: {e}")

# --- Check for active session ---
session_response = supabase.auth.get_session()
session = session_response.session if session_response and session_response.session else None

if not session or not session.user:
    st.stop()

user = session.user
user_email = user.email

# --- Check profile ---
user_data = supabase.table("users").select("*").eq("email", user_email).execute().data
if not user_data:
    st.header("📝 Complete Your Profile")
    first_name = st.text_input("First Name")
    age = st.number_input("Age", min_value=18, max_value=100)
    gender = st.selectbox("Gender", ["male", "female", "non-binary", "prefer not to say"])
    city = st.text_input("City")
    state = st.text_input("State")
    zip_code = st.text_input("ZIP Code")
    latitude = st.number_input("Latitude", format="%.6f")
    longitude = st.number_input("Longitude", format="%.6f")

    if st.button("Submit Profile"):
        supabase.table("users").insert({
            "email": user_email,
            "first_name": first_name,
            "age": age,
            "gender": gender,
            "city": city,
            "state": state,
            "zip_code": zip_code,
            "latitude": latitude,
            "longitude": longitude
        }).execute()
        st.success("Profile created! Please refresh to continue.")
        st.stop()

user_info = supabase.table("users").select("*").eq("email", user_email).execute().data[0]
st.success(f"Welcome back, {user_info['first_name']}!")

# --- Check if quiz is completed ---
quiz_data = supabase.table("quiz_answers").select("*").eq("user_id", user_info["id"]).execute().data
if not quiz_data:
    st.header("🎓 Quiz")
    questions = supabase.table("quiz_questions").select("*").execute().data
    answers = {}
    for q in questions:
        answers[q["id"]] = st.radio(q["question_text"], ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"], key=q["id"])

    if st.button("Submit Quiz"):
        for qid, response in answers.items():
            supabase.table("quiz_answers").insert({
                "user_id": user_info["id"],
                "question_id": qid,
                "response": response,
                "domain": next((q["domain"] for q in questions if q["id"] == qid), "general")
            }).execute()
        st.success("Quiz submitted! Please refresh.")
        st.stop()

# --- Load and filter matches ---
st.header("💼 Your Matches")
gender_filter = st.selectbox("Show matches who are gender:", ["any", "male", "female", "non-binary"])
age_min, age_max = st.slider("Age range", 18, 100, (25, 40))
distance_limit = st.slider("Max distance (miles)", 1, 100, 25)

matches = supabase.table("matches").select("*").execute().data
filtered = [m for m in matches if m["user1_id"] == user_info["id"] or m["user2_id"] == user_info["id"]]

selected_coords = (user_info.get("latitude"), user_info.get("longitude"))

for match in filtered:
    other_id = match["user2_id"] if match["user1_id"] == user_info["id"] else match["user1_id"]
    other_user = next((u for u in supabase.table("users").select("*").eq("id", other_id).execute().data), None)
    if not other_user:
        continue

    if gender_filter != "any" and other_user.get("gender") != gender_filter:
        continue
    age = other_user.get("age")
    if not age or not (age_min <= age <= age_max):
        continue

    other_coords = (other_user.get("latitude"), other_user.get("longitude"))
    distance = geodesic(selected_coords, other_coords).miles if None not in other_coords else None
    if distance is not None and distance > distance_limit:
        continue

    score = match.get("compatibility_score", 0)
    if score < 60:
        continue
    match_type = match.get("match_type", "Unknown")
    shared = match.get("shared_values") or "None"

    location = f"{other_user.get('city')}, {other_user.get('state')} {other_user.get('zip_code')}"
    distance_str = f"{round(distance)} miles away" if distance else "Distance unknown"

    st.markdown(f"""
    ### 💑 Match with **{other_user['first_name']}**
    - **Score:** {score}%
    - **Match Type:** {match_type}
    - **Shared Values:** {shared}
    - **📍 Location:** {location} — *{distance_str}*
    """)
    col1, col2 = st.columns(2)
    with col1:
        st.button(f"🔥 Like {other_user['first_name']}", key=f"like_{other_id}")
    with col2:
        st.button(f"💬 Message", key=f"msg_{other_id}")
    st.divider()
