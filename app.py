import streamlit as st
from supabase import create_client
import json

# 👇 Direct Supabase config for now
url = "https://gieqacigvysfoghrdcqj.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpZXFhY2lndnlzZm9naHJkY3FqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4ODM0NDMsImV4cCI6MjA2NzQ1OTQ0M30.ltaod_JhmV27DMkG_a1QMAYL3MCm5DHEiAowJPan8Po"
supabase = create_client(url, key)

st.title("💘 Amorly: Your Matches")

# Load users
users_data = supabase.table("users").select("id", "first_name", "email").execute().data
user_options = [f"{user['first_name']} ({user['email']})" for user in users_data]
selected_user = st.selectbox("Choose a user to view their matches:", user_options)

if selected_user:
    selected_email = selected_user.split("(")[-1][:-1]
    current_user = next(user for user in users_data if user["email"] == selected_email)

    # Load matches where current user is the viewer
    matches_data = (
        supabase.table("matches")
        .select("*, matched_user:users(*), compatibility_score(*)")
        .eq("user_id", current_user["id"])
        .execute()
        .data
    )

    if matches_data:
        shown_users = set()
        for match in matches_data:
            matched_user = match["matched_user"]
            if matched_user["id"] in shown_users:
                continue  # Skip duplicate users

            shown_users.add(matched_user["id"])
            score_data = match["compatibility_score"]
            score = score_data["score"] if score_data and "score" in score_data else None

            if score is None or score < 60:
                continue  # Skip matches below 60% score

            match_type = score_data.get("match_type", "Unknown")
            shared = score_data.get("shared_values", "None")

            # 👉 Fix shared values formatting
            if isinstance(shared, str):
                try:
                    shared_list = json.loads(shared)
                    if isinstance(shared_list, list):
                        shared_values = ", ".join(shared_list)
                    else:
                        shared_values = shared
                except json.JSONDecodeError:
                    shared_values = shared
            else:
                shared_values = ", ".join(shared) if isinstance(shared, list) else str(shared)

            st.markdown(f"""
                ### 💞 Match with {matched_user['first_name']}
                **Match Type:** {match_type}  
                **Shared Values:** {shared_values if shared_values else "None"}  
                **Compatibility Score:** {score}%
            """)
    else:
        st.info("No matches found for this user.")
