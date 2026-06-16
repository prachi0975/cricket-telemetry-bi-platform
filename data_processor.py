import json
import pandas as pd
import os
import logging
import sys
from sqlalchemy import create_engine

# Setting up basic logging for debugging & RCA
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_and_clean_json(folder_path):
    all_deliveries = []
    try:
        logging.info(f"Scanning directory '{folder_path}' for JSON payloads...")
        json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
        
        if not json_files:
            logging.error(f"Incident: No JSON files found in '{folder_path}'.")
            sys.exit(1)
            
        logging.info(f"Found {len(json_files)} files. Processing JSON structures...")

        for file_name in json_files:
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            match_id = file_name.split('.')[0]
            
            for inning in data.get('innings', []):
                team = inning.get('team')
                for over in inning.get('overs', []):
                    over_num = over.get('over')
                    for ball_num, delivery in enumerate(over.get('deliveries', [])):
                        row = {
                            'match_id': match_id,
                            'batting_team': team,
                            'over': over_num,
                            'ball': ball_num + 1,
                            'batter': delivery.get('batter'),
                            'bowler': delivery.get('bowler'),
                            'batter_runs': delivery.get('runs', {}).get('batter', 0),
                            'extras': delivery.get('runs', {}).get('extras', 0),
                            'total_runs': delivery.get('runs', {}).get('total', 0)
                        }
                        all_deliveries.append(row)
        
        df = pd.DataFrame(all_deliveries)
        logging.info(f"Successfully processed nested JSON. Extracted {len(df)} telemetry records.")
        return df
        
    except Exception as e:
        logging.error(f"Incident: JSON processing failed. Root Cause Analysis (RCA): {e}")
        sys.exit(1)

def push_to_database(df):
    try:
        logging.info("Attempting PostgreSQL database connection...")
        engine = create_engine('postgresql://localhost/cricket_analytics')
        
        logging.info("Pushing data to the 'telemetry_deliveries' table...")
        df.to_sql('telemetry_deliveries', engine, if_exists='append', index=False)
        
        logging.info(f"Success! Pipeline execution complete. {len(df)} records stored in database.")
        
    except Exception as e:
        logging.error(f"Incident: Database injection failed. Root Cause Analysis (RCA): {e}")
        sys.exit(1)

if __name__ == "__main__":
    data_folder = 'data' 
    cleaned_df = load_and_clean_json(data_folder)
    
    print("\nData Preview (Parsed from JSON):")
    print(cleaned_df.head())
    
    # Triggering the DB push
    push_to_database(cleaned_df)