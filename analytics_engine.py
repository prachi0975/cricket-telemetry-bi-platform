import pandas as pd
import logging
import sys
from sqlalchemy import create_engine

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def run_sql_analytics():
    try:
        logging.info("Connecting to PostgreSQL database...\n")
        engine = create_engine('postgresql://localhost/cricket_analytics')
        
        # Query 1: Finding the Top 5 Run Scorers in our current dataset
        query1 = """
        SELECT batter, SUM(batter_runs) as total_runs
        FROM telemetry_deliveries
        GROUP BY batter
        ORDER BY total_runs DESC
        LIMIT 5;
        """
        
        # Query 2: Time-Series Analysis - Match Momentum (Runs per Over)
        # Analyzing Chennai Super Kings' batting progression in match '335989'
        query2 = """
        SELECT over, SUM(total_runs) as runs_in_over
        FROM telemetry_deliveries
        WHERE match_id = '335989' AND batting_team = 'Chennai Super Kings'
        GROUP BY over
        ORDER BY over;
        """
        
        # Executing queries and fetching results directly into Pandas DataFrames
        print("--- INSIGHT 1: TOP 5 BATTERS ---")
        top_batters_df = pd.read_sql(query1, engine)
        print(top_batters_df.to_string(index=False))
        print("\n")
        
        print("--- INSIGHT 2: CSK MATCH MOMENTUM (RUNS PER OVER) ---")
        momentum_df = pd.read_sql(query2, engine)
        print(momentum_df.to_string(index=False))
        
    except Exception as e:
        logging.error(f"Incident: SQL Execution Failed. RCA: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_sql_analytics()