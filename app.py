import streamlit as st
from supabase import create_client, Client
import ast

# Load credentials from secrets
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.title("💘 Your Matches")

# Step 1: Load all users
users_data = supabase.table("users").select("id", "first_name").execute().data
user_lookup = {user["id"]: user["first_name"] for user in users_data}

# Step 2: Simulate login dropdown
user_options = [user["first_name"] for user in users_data]
selected_name = st.selectbox("Select your profile:", user_options)
selected_id = [uid for uid, name in user_lookup.items() if name == selected_name][0]

# Step 3: Load all matches involving this user
match_data = supabase.table("matches").select("*").execute().data

# Filter matches where selected user is user1 or user2
filtered_matches = [m for m in match_data if m["user1_id"] == selected_id or m["user2_id"] == selected_id]

if not filtered_matches:
    st.warning("No matches found.")
else:
    for match in filtered_matches:
        # Identify the matched person (not the logged-in user)
        matched_user_id = match["user2_id"] if match["user1_id"] == selected_id else match["user1_id"]
        matched_name = user_lookup.get(matched_user_id, "Unknown")

        compatibility = match.get("compatibility_score", 0)
        if compatibility < 60:
            continue  # Skip low matches

        match_type = match.get("match_type", "Unknown")
        raw_values = match.get("overlap_values", "")
        
        # Handle stringified lists like '["security","tradition"]'
        try:
            values = ast.literal_eval(raw_values)
            if isinstance(values, list):
                clean_values = ", ".join(values)
            else:
                clean_values = raw_values
        except:
            clean_values = raw_values

        st.markdown(f"""
        ### 💑 Match with **{matched_name}**
        - **Score:** {compatibility}%
        - **Match Type:** {match_type}
        - **Shared Values:** {clean_values if clean_values else "None"}
        """)

