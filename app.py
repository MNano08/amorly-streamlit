import streamlit as st
from supabase import create_client, Client
import json

# Supabase setup
url = "https://gieqacigvysfoghrdcqj.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpZXFhY2lndnlzZm9naHJkY3FqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4ODM0NDMsImV4cCI6MjA2NzQ1OTQ0M30.ltaod_JhmV27DMkG_a1QMAYL3MCm5DHEiAowJPan8Po"
supabase: Client = create_client(url, key)

st.set_page_config(page_title="💘 Amorly: Your Matches", layout="centered")

st.title("💘 Amorly: Your Matches")

# Step 1: User selection
users_data = supabase.table("users").select("id", "first_name", "email").execute().data
user_map = {f"{u['first_name']} ({u['email']})": u["id"] for u in users_data}
selected_user_label = st.selectbox("Choose a user to view their matches:", list(user_map.keys()))
selected_user_id = user_map[selected_user_label]

# Step 2: Fetch all matches for selected user
match_results = supabase.table("matches").select("*").or_(
    f"user1_id.eq.{selected_user_id},user2_id.eq.{selected_user_id}"
).execute().data

# Step 3: Filter matches over 60% and exclude self-identity
filtered = []
for match in match_results:
    if match["compatibility"] >= 60:
        other_user_id = match["user2_id"] if match["user1_id"] == selected_user_id else match["user1_id"]
        other_user = next((u for u in users_data if u["id"] == other_user_id), None)
        if other_user:
            filtered.append({
                "name": other_user["first_name"],
                "match_type": match["match_type"],
                "overlap_values": match.get("overlap_values", []),
                "compatibility": round(match["compatibility"], 1)
            })

# Step 4: Display
if filtered:
    for match in filtered:
        st.markdown(f"""
        ### 👤 Match: {match['name']}
        **Match Type:** {match['match_type']}  
        **Shared Values:** {', '.join(match['overlap_values']) if match['overlap_values'] else 'None'}  
        **Compatibility Score:** {match['compatibility']}%
        """)
else:
    st.info("No matches above 60% compatibility found.")
