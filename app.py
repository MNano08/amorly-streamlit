import streamlit as st
from supabase import create_client, Client
import os

# Step 1: Setup Supabase
url = "https://gieqacigvysfoghrdcqj.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpZXFhY2lndnlzZm9naHJkY3FqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4ODM0NDMsImV4cCI6MjA2NzQ1OTQ0M30.ltaod_JhmV27DMkG_a1QMAYL3MCm5DHEiAowJPan8Po"
supabase: Client = create_client(url, key)

# Step 2: Fetch users for dropdown
users_data = supabase.table("users").select("id", "first_name", "email").execute().data

st.title("💘 Amorly: Your Matches")
selected_user = st.selectbox(
    "Choose a user to view their matches:",
    users_data,
    format_func=lambda user: f"{user['first_name']} ({user['email']})"
)
selected_user_id = selected_user["id"]

# Step 3: Fetch matches where user is either side
match_results = supabase.table("matches").select("*").or_(
    f"user1_id.eq.{selected_user_id},user2_id.eq.{selected_user_id}"
).execute().data

# Step 4: Filter and display matches above 60% (excluding self-identity)
filtered = []
for match in match_results:
    compatibility_score = match.get("compatibility_score", 0)
    if compatibility_score >= 60:
        other_user_id = match["user2_id"] if match["user1_id"] == selected_user_id else match["user1_id"]
        other_user = next((u for u in users_data if u["id"] == other_user_id), None)
        if other_user:
            filtered.append({
                "name": other_user["first_name"],
                "match_type": match.get("match_type", "Unknown"),
                "overlap_values": match.get("overlap_values", []),
                "compatibility": round(compatibility_score, 1)
            })

# Step 5: Display matches
if filtered:
    for match in filtered:
        st.markdown(f"""
        ### 💞 Match with {match['name']}
        **Match Type:** {match['match_type']}  
        **Shared Values:** {', '.join(match['overlap_values']) if match['overlap_values'] else 'None'}  
        **Compatibility Score:** {match['compatibility']}%
        """)
else:
    st.info("No matches above 60% compatibility found.")
