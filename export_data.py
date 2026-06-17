from sqlalchemy import create_engine
import pandas as pd

# Local database connection (agar password ho toh @localhost ke baad add kar dena)
engine = create_engine('postgresql://localhost/cricket_analytics')

# Data load karna
df = pd.read_sql("SELECT * FROM telemetry_deliveries", engine)

# CSV mein export karna
df.to_csv('cricket_data_dump.csv', index=False)
print("Data successfully exported to cricket_data_dump.csv")