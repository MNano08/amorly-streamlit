import streamlit as st
from supabase import create_client, Client
import os
import ast

# Supabase setup
url = st.secrets["https://gieqacigvysfoghrdcqj.supabase.co"]
key = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpZXFhY2lndnlzZm9naHJkY3FqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4ODM0NDMsImV4cCI6MjA2NzQ1OTQ0M30.ltaod_JhmV27DMkG_a1QMAYL3MCm5DHEiAowJPan8Po"]
supabase: Client = create_client(url, key)

st.title("💘 Amorly: Your Matches")

# Fetch users
users_response = supabase.table("users").select("*").execute()
users = users_response.data

user_options = {f"{user['first_name']} ({user['email']})": user["id"] for user in users}
selected_user_display = st.selectbox("Choose a user to view their matches:", list(user_options.keys()))
selected_user_id = user_options[selected_user_display]

# Fetch matches where selected user is either user1 or user2
match_response = (
    supabase.table("matches")
    .select("*")
    .or_(f"user1_id.eq.{selected_user_id},user2_id.eq.{selected_user_id}")
    .execute()
)
matches = match_response.data

if not matches:
    st.info("No matches found.")
else:
    shown_match_ids = set()
    for match in matches:
        match_id = match["id"]
        if match_id in shown_match_ids:
            continue
        shown_match_ids.add(match_id)

        compatibility = match.get("compatibility_score")
        if compatibility is None or compatibility < 60:
            continue

        # Figure out the other user (not the viewer)
        user1 = match["user1_id"]
        user2 = match["user2_id"]
        matched_user_id = user2 if user1 == selected_user_id else user1
        matched_user = next((u for u in users if u["id"] == matched_user_id), None)
        if not matched_user:
            continue

        # Parse overlap_values safely
        raw_values = match.get("overlap_values")
        if isinstance(raw_values, str):
            try:
                parsed = ast.literal_eval(raw_values)
                overlap_values = parsed if isinstance(parsed, list) else [v.strip() for v in raw_values.split(",")]
            except:
                overlap_values = [v.strip() for v in raw_values.split(",") if v.strip()]
        elif isinstance(raw_values, list):
            overlap_values = raw_values
        else:
            overlap_values = []

        match_type = match.get("match_type", "Unknown")

        st.markdown(f"### 💞 Match with {matched_user['first_name']}")
        st.markdown(f"**Match Type:** {match_type}")
        st.markdown(f"**Shared Values:** {', '.join(overlap_values) if overlap_values else 'None'}")
        st.markdown(f"**Compatibility Score:** {compatibility}%")
        st.markdown("---")
