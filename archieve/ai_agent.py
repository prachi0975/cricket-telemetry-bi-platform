import os
import sys
import pandas as pd
from sqlalchemy import create_engine
from google import genai

def run_custom_ai_agent():
    print("Initializing Custom AI Cricket Scout...\n")
    
    # 1. Database Connection
    try:
        engine = create_engine('postgresql://localhost/cricket_analytics')
    except Exception as e:
        print(f"Incident: Database Connection Failed. RCA: {e}")
        sys.exit(1)
        
    # 2. Initialize new Google GenAI Client
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Incident: GOOGLE_API_KEY not found in environment variables.")
        sys.exit(1)
        
    client = genai.Client(api_key=api_key)
    
    # 3. Define the Database Schema & User Question
    schema = """
    Table Name: telemetry_deliveries
    Columns: match_id (text), batting_team (text), over (int), ball (int), batter (text), bowler (text), batter_runs (int), extras (int), total_runs (int)
    """
    
    question = "Who are the top 3 run-scorers in this dataset and how many total runs did each score?"
    
    # 4. Prompt Engineering: Forcing AI to strictly act as a SQL Generator
    prompt = f"""
    Given this PostgreSQL database schema:
    {schema}
    
    Write a valid PostgreSQL query to answer this question: '{question}'.
    CRITICAL: Return ONLY the raw SQL query string. Do not use markdown blocks like ```sql. Do not add any explanations.
    """
    
    print(f"User Question: '{question}'")
    print("AI is generating SQL...")
    
    try:
        # Using the latest Gemini 2.0 Flash model compatible with new keys
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        
        # Clean up the output just in case AI adds markdown
        sql_query = response.text.strip().replace("```sql", "").replace("```", "").strip()
        print(f"\nGenerated SQL Query:\n{sql_query}\n")
        
        # 5. Run the SQL and display results using Pandas
        print("Fetching data from PostgreSQL...")
        result_df = pd.read_sql(sql_query, engine)
        
        print("\n--- Final AI Assistant Output ---")
        print(result_df.to_string(index=False))
        
    except Exception as e:
        print(f"\nIncident: AI Execution failed. RCA: {e}")

if __name__ == "__main__":
    run_custom_ai_agent()