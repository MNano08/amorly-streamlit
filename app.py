import streamlit as st
from supabase import create_client

# Supabase setup
url = "https://gieqacigvysfoghrdcqj.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpZXFhY2lndnlzZm9naHJkY3FqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4ODM0NDMsImV4cCI6MjA2NzQ1OTQ0M30.ltaod_JhmV27DMkG_a1QMAYL3MCm5DHEiAowJPan8Po"
supabase = create_client(url, key)

st.title("💘 Amorly: Values-Based Matches")

# Choose a user (simulate login for now)
users = supabase.table("users").select("id, first_name, email").execute().data
user_names = {f"{u['first_name']} ({u['email']})": u['id'] for u in users}
selected_name = st.selectbox("Choose a user to view matches:", list(user_names.keys()))
current_user_id = user_names[selected_name]

# Fetch matches where current_user is user1
matches = supabase.table("matches").select("*").eq("user1_id", current_user_id).execute().data

if matches:
    st.subheader("Your Matches:")
    for m in matches:
        match_user = supabase.table("users").select("first_name").eq("id", m["user2_id"]).execute().data[0]
        st.markdown(f"""
        **Name:** {match_user['first_name']}  
        **Match Type:** {m['match_type']}  
        **Shared Values:** {m['overlap_values']}  
        **Compatibility Score:** {m['compatibility_score']}%
        """)
else:
    st.info("No matches found.")
