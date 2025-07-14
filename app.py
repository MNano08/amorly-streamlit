import streamlit as st
from supabase import create_client, Client
import json

# Supabase credentials
url = st.secrets["https://gieqacigvysfoghrdcqj.supabase.co"]
key = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpZXFhY2lndnlzZm9naHJkY3FqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4ODM0NDMsImV4cCI6MjA2NzQ1OTQ0M30.ltaod_JhmV27DMkG_a1QMAYL3MCm5DHEiAowJPan8Po"]
supabase: Client = create_client(url, key)

st.title("💘 Amorly: Your Matches")

# Get list of users
users_data = supabase.table("users").select("id", "first_name", "email").execute().data
user_options = {f"{user['first_name']} ({user['email']})": user["id"] for user in users_data}
selected_label = st.selectbox("Choose a user to view their matches:", list(user_options.keys()))
selected_user_id = user_options[selected_label]

# Get all matches
matches_data = supabase.table("matches").select("*").execute().data

# Filter matches involving the selected user
filtered_matches = []
seen = set()

for match in matches_data:
    ids = (match["user1_id"], match["user2_id"])
    if selected_user_id in ids and ids not in seen and tuple(reversed(ids)) not in seen:
        seen.add(ids)

        # Determine the other person
        other_id = match["user2_id"] if match["user1_id"] == selected_user_id else match["user1_id"]
        other_user = next((u for u in users_data if u["id"] == other_id), None)
        if not other_user:
            continue

        # Ensure compatibility is a number and ≥ 60
        try:
            score = float(match["compatibility_score"])
        except (KeyError, ValueError, TypeError):
            continue

        if score < 60:
            continue

        # Parse overlap values robustly
        raw = match.get("overlap_values")
        parsed = []

        if isinstance(raw, list):
            parsed = raw
        elif isinstance(raw, str):
            try:
                parsed = json.loads(raw)
                if not isinstance(parsed, list):
                    parsed = []
            except json.JSONDecodeError:
                parsed = []
        else:
            parsed = []

        # Display match block
        st.markdown(f"""
        ### 💞 Match with {other_user['first_name']}
        **Match Type:** {match.get('match_type', 'Unknown')}  
        **Shared Values:** {'None' if not parsed else ', '.join(parsed)}  
        **Compatibility Score:** {score}%
        """)

if not any(selected_user_id in (m["user1_id"], m["user2_id"]) and float(m.get("compatibility_score", 0)) >= 60 for m in matches_data):
    st.info("No matches above 60% compatibility found.")
