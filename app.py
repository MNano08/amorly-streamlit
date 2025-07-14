import streamlit as st
from supabase import create_client, Client
import os
import json

# Setup Supabase
url = "https://gieqacigvysfoghrdcqj.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpZXFhY2lndnlzZm9naHJkY3FqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4ODM0NDMsImV4cCI6MjA2NzQ1OTQ0M30.ltaod_JhmV27DMkG_a1QMAYL3MCm5DHEiAowJPan8Po"
supabase: Client = create_client(url, key)

# Load users
users_data = supabase.table("users").select("id", "first_name", "email").execute().data

st.title("💘 Amorly: Your Matches")
selected_user = st.selectbox(
    "Choose a user to view their matches:",
    users_data,
    format_func=lambda user: f"{user['first_name']} ({user['email']})"
)
selected_user_id = selected_user["id"]

# Load matches involving this user
match_results = supabase.table("matches").select("*").or_(
    f"user1_id.eq.{selected_user_id},user2_id.eq.{selected_user_id}"
).execute().data

shown_pairs = set()
filtered_matches = []

for match in match_results:
    # Skip low-compatibility matches
    compatibility = match.get("compatibility_score", 0)
    if compatibility < 60:
        continue

    # Skip duplicates (Alice+Bob == Bob+Alice)
    user_pair = tuple(sorted([match["user1_id"], match["user2_id"]]))
    if user_pair in shown_pairs:
        continue
    shown_pairs.add(user_pair)

    # Identify the other user
    other_user_id = match["user2_id"] if match["user1_id"] == selected_user_id else match["user1_id"]
    other_user = next((u for u in users_data if u["id"] == other_user_id), None)
    if not other_user:
        continue

    # Parse overlap values
    raw = match.get("overlap_values", "[]")
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except:
            parsed = []
    elif isinstance(raw, list):
        parsed = raw
    else:
        parsed = []

    filtered_matches.append({
        "name": other_user["first_name"],
        "match_type": match.get("match_type", "Unknown"),
        "overlap_values": parsed,
        "compatibility": round(compatibility, 1)
    })

# Display
if filtered_matches:
    for match in filtered_matches:
        st.markdown(f"""
        ### 💞 Match with {match['name']}
        **Match Type:** {match['match_type']}  
        **Shared Values:** {', '.join(match['overlap_values']) if match['overlap_values'] else 'None'}  
        **Compatibility Score:** {match['compatibility']}%
        """)
else:
    st.info("No matches above 60% compatibility found.")
