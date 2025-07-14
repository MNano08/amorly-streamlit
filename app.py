import streamlit as st
from supabase import create_client, Client
import json

# Set up Supabase client
url = "https://gieqacigvysfoghrdcqj.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpZXFhY2lndnlzZm9naHJkY3FqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4ODM0NDMsImV4cCI6MjA2NzQ1OTQ0M30.ltaod_JhmV27DMkG_a1QMAYL3MCm5DHEiAowJPan8Po"
supabase: Client = create_client(url, key)

# Title
st.title("💘 Amorly: Your Matches")

# Get all users (so we can show them as options)
users_data = supabase.table("users").select("id", "first_name", "email").execute().data
user_email_map = {f"{user['first_name']} ({user['email']})": user["id"] for user in users_data}

# Dropdown to choose who you want to see matches for
selected_user_label = st.selectbox("Choose a user to view their matches:", list(user_email_map.keys()))
selected_user_id = user_email_map[selected_user_label]

# Fetch matches where selected user is user1 or user2
match_query = supabase.table("compatibility_score").select("*").or_(
    f"user1_id.eq.{selected_user_id},user2_id.eq.{selected_user_id}"
).execute().data

# Filter by 60%+ compatibility
filtered_matches = [m for m in match_query if m["compatibility"] >= 60]

if filtered_matches:
    st.subheader("💞 Your Matches:")
    for match in filtered_matches:
        match_user_id = match["user2_id"] if match["user1_id"] == selected_user_id else match["user1_id"]
        match_user = next((u for u in users_data if u["id"] == match_user_id), None)
        if match_user:
            st.markdown(f"""
            **Name:** {match_user['first_name']}  
            **Match Type:** {match['match_type']}  
            **Shared Values:** {', '.join(match['overlap_values']) if match['overlap_values'] else 'None'}  
            **Compatibility Score:** {match['compatibility']}%
            """)
else:
    st.info("No matches above 60% compatibility found.")
