import streamlit as st
import google.generativeai as genai
import pandas as pd
import os
from sqlalchemy import create_engine
import urllib.parse
import plotly.express as px
from dotenv import load_dotenv


# 1. Advanced Page Configuration
st.set_page_config(page_title="Ultimate Cricket Analytics", layout="wide", page_icon="🏏")

st.title("🏏 Ultimate Cricket Match Analytics Platform")
st.markdown("*End-to-End Dynamic Business Intelligence, Predictive Analytics & Export Suite*")
st.markdown("---")

# 2. Secure Data Extraction Layer
load_dotenv()

# Database connection details
def get_db_engine():
    # Agar app Cloud par hai (st.secrets available hai)
    if "user" in st.secrets:
        USER = st.secrets["user"]
        PASSWORD = urllib.parse.quote_plus(st.secrets["password"])
        HOST = st.secrets["host"]
        PORT = st.secrets["port"]
        DBNAME = st.secrets["dbname"]
    # Agar app Local computer par hai (.env available hai)
    else:
        USER = os.getenv("user")
        PASSWORD = urllib.parse.quote_plus(os.getenv("password"))
        HOST = os.getenv("host")
        PORT = os.getenv("port")
        DBNAME = os.getenv("dbname")
    
    db_url = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"
    return create_engine(db_url)

@st.cache_data

def fetch_data(query):
    try:
        # Engine yahan se call karo, directly variable use mat karo
        engine = get_db_engine() 
        return pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Cloud Connection Error: {e}")
        return pd.DataFrame()

# Helper function for CSV Export
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# 3. Load Base Dataset
raw_data_query = "SELECT * FROM telemetry_deliveries;"
df_raw = fetch_data(raw_data_query)

if not df_raw.empty:
    # --- SIDEBAR GLOBAL FILTER ---
    st.sidebar.header("🔍 Global Team Filter")
    teams = df_raw['batting_team'].unique()
    selected_team = st.sidebar.selectbox("Select Batting Team:", teams)
    
    # Filter the primary dataframe based on selection
    df_filtered = df_raw[df_raw['batting_team'] == selected_team]

    # --- MULTI-TAB ARCHITECTURE ---
    # --- MULTI-TAB ARCHITECTURE ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Executive & Predictive Dashboard", 
        "🕵️ Batter Performance", 
        "🥎 Bowler Analytics", 
        "🎯 Matchups & Phases",
        "🧠 Ask AI (Chat with Data)"  # NAYA TAB YAHAN ADD HUA
    ])

    # ==========================================
    # TAB 1: EXECUTIVE & PREDICTIVE DASHBOARD
    # ==========================================
    with tab1:
        st.subheader(f"Live Team Metrics: {selected_team}")
        
        total_runs = df_filtered['total_runs'].sum()
        total_balls = len(df_filtered)
        highest_scorer = df_filtered.groupby('batter')['batter_runs'].sum().idxmax()
        
        # Predictive Analytics Math
        overs_played = (df_filtered['over'].max() + 1) # overs are 0-indexed
        current_run_rate = total_runs / overs_played if overs_played > 0 else 0
        projected_score = current_run_rate * 20
        
        # Displaying 5 KPIs now!
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Runs", int(total_runs))
        col2.metric("Deliveries", total_balls)
        col3.metric("Top Scorer", highest_scorer)
        col4.metric("Current Run Rate", round(current_run_rate, 2))
        col5.metric("Projected 20-Over Score", int(projected_score), delta="Predicted")
        
        st.markdown("---")
        st.markdown("### Match Momentum Tracking")
        momentum_df = df_filtered.groupby('over')['total_runs'].sum().reset_index()
        fig_momentum = px.line(momentum_df, x='over', y='total_runs', 
                               markers=True, line_shape='spline',
                               labels={'over': 'Over Number', 'total_runs': 'Runs Scored'},
                               color_discrete_sequence=['#1f77b4'])
        fig_momentum.add_hline(y=10, line_dash="dot", line_color="red", annotation_text="High Scoring Zone")
        st.plotly_chart(fig_momentum, use_container_width=True)

    # ==========================================
    # TAB 2: BATTER PERFORMANCE
    # ==========================================
    with tab2:
        st.subheader("Leaderboard: Top Batters")
        batter_stats = df_filtered.groupby('batter').agg(
            Runs=('batter_runs', 'sum'),
            Balls_Faced=('ball', 'count')
        ).reset_index().sort_values(by='Runs', ascending=False)
        
        batter_stats['Strike_Rate'] = (batter_stats['Runs'] / batter_stats['Balls_Faced'] * 100).round(2)
        
        # Plotting Top 10
        fig_bar = px.bar(batter_stats.head(10), x='batter', y='Runs', 
                         hover_data=['Strike_Rate', 'Balls_Faced'],
                         color='Runs', color_continuous_scale='Blues')
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Enterprise Export Feature
        st.markdown("**Export Full Batter Telemetry**")
        st.download_button(
            label="⬇️ Download Batter Data as CSV",
            data=convert_df_to_csv(batter_stats),
            file_name=f"{selected_team}_batter_stats.csv",
            mime="text/csv",
        )

    # ==========================================
    # TAB 3: BOWLER ANALYTICS
    # ==========================================
    with tab3:
        st.subheader("Leaderboard: Economy Analysis")
        bowler_stats = df_filtered.groupby('bowler').agg(
            Runs_Conceded=('total_runs', 'sum'),
            Balls_Bowled=('ball', 'count')
        ).reset_index()
        
        bowler_stats = bowler_stats[bowler_stats['Balls_Bowled'] >= 6]
        bowler_stats['Overs'] = (bowler_stats['Balls_Bowled'] / 6).round(1)
        bowler_stats['Economy_Rate'] = (bowler_stats['Runs_Conceded'] / bowler_stats['Overs']).round(2)
        bowler_stats = bowler_stats.sort_values(by='Economy_Rate', ascending=True)
        
        fig_bowler = px.bar(bowler_stats.head(10), x='bowler', y='Economy_Rate',
                            color='Economy_Rate', color_continuous_scale='Viridis_r',
                            hover_data=['Runs_Conceded', 'Overs'])
        st.plotly_chart(fig_bowler, use_container_width=True)
        
        # Enterprise Export Feature
        st.markdown("**Export Full Bowler Telemetry**")
        st.download_button(
            label="⬇️ Download Bowler Data as CSV",
            data=convert_df_to_csv(bowler_stats),
            file_name=f"{selected_team}_bowler_stats.csv",
            mime="text/csv",
        )

    # ==========================================
    # TAB 4: ADVANCED MATCHUPS & PHASES
    # ==========================================
    with tab4:
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("### 📊 Phase of Play")
            def assign_phase(over):
                if over <= 5: return 'Powerplay (0-5)'
                elif over <= 14: return 'Middle Overs (6-14)'
                else: return 'Death Overs (15-19)'
                
            df_filtered['Phase'] = df_filtered['over'].apply(assign_phase)
            phase_df = df_filtered.groupby('Phase')['total_runs'].sum().reset_index()
            
            fig_pie = px.pie(phase_df, values='total_runs', names='Phase', 
                             hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_right:
            st.markdown("### 🎯 Head-to-Head Matrix")
            batters_list = sorted(df_filtered['batter'].unique())
            bowlers_list = sorted(df_filtered['bowler'].unique())
            
            selected_batter = st.selectbox("Select Batter:", batters_list)
            selected_bowler = st.selectbox("Select Bowler:", bowlers_list)
            
            matchup_df = df_filtered[(df_filtered['batter'] == selected_batter) & (df_filtered['bowler'] == selected_bowler)]
            
            if not matchup_df.empty:
                m_runs = matchup_df['batter_runs'].sum()
                m_balls = len(matchup_df)
                m_sr = round((m_runs / m_balls * 100), 2) if m_balls > 0 else 0
                
                st.success(f"**Matchup:** {selected_batter} vs {selected_bowler}")
                st.write(f"🔹 **Runs:** {int(m_runs)}")
                st.write(f"🔹 **Balls Faced:** {m_balls}")
                st.write(f"🔹 **Strike Rate:** {m_sr}")
            else:
                st.warning("No data for this specific matchup.")



    # ==========================================
    # TAB 5: ASK AI (Chat with Data)
    # ==========================================
    with tab5:
        st.subheader("🤖 GenAI Data Assistant")
        st.markdown("Ask anything about the current match data, and AI will analyze it for you.")
        
        # API Key Fetching Engine
        try:
            gemini_api_key = st.secrets["GEMINI_API_KEY"]
        except (KeyError, FileNotFoundError):
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            
        if not gemini_api_key:
            st.warning("⚠️ API Key missing! Please add GEMINI_API_KEY to your secrets.")
        else:
            genai.configure(api_key=gemini_api_key)
            
            user_question = st.text_input("📝 What do you want to know about this match?")
            
            if st.button("Generate Insights ✨"):
                if user_question:
                    with st.spinner("Analyzing telemetry data..."):
                        try:
                            # 1. Data Context Preparation (Top 50 rows + Summary to avoid token overload)
                            data_summary = df_filtered.describe().to_string()
                            recent_plays = df_filtered.tail(50).to_string(index=False)
                            
                            # 2. Prompt Engineering
                            prompt = f"""
                            You are an expert Cricket Data Analyst. You have been given the telemetry data for a cricket match.
                            Here is the statistical summary of the innings:
                            {data_summary}
                            
                            Here are the most recent 50 deliveries:
                            {recent_plays}
                            
                            Based strictly on this data, answer the user's question clearly and concisely. If the data doesn't contain the answer, politely state that.
                            
                            User Question: {user_question}
                            """
                            
                            # 3. Model Generation
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            response = model.generate_content(prompt)
                            
                            # 4. Display Result
                            st.info("📊 AI Analysis Complete")
                            st.write(response.text)
                            
                        except Exception as e:
                            st.error(f"Failed to generate AI insights. Error: {e}")