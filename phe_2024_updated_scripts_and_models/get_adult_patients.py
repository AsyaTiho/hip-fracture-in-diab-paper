import sqlite3
import pickle
import time
import sys

def main():
    # 1. Connect to the main database (enrollment data)

    main_db_name = '/Volumes/FastSSD_2/ENROL_INTERVALS_2024.db'
    demographics_db_name = '/Volumes/FastSSD_2/DEMO_2024.db'
    
    print(f"Connecting to {main_db_name} and attaching {demographics_db_name}...")
    
    start_time = time.time()
    
    conn = sqlite3.connect(main_db_name)
    c_enrol = conn.cursor()

    # Attach your DEMOGRAPHICS database
    c_enrol.execute(f"ATTACH DATABASE '{demographics_db_name}' AS db2")

    # Write the query to JOIN the two tables across the databases
    query = """
        SELECT e.enrolid 
        FROM main.ENROL_INTERVAL e
        JOIN db2.DEMO d ON e.enrolid = d.enrolid
        WHERE (e.startyear - d.dobyr) >= 20
    """

    print("Executing query...")
    query_start_time = time.time()
    
    # Execute and fetch into a list
    c_enrol.execute(query)
    more_than_20_at_enrolment = [row[0] for row in c_enrol.fetchall()]
    
    query_end_time = time.time()
    query_duration = query_end_time - query_start_time
    print(f"Query finished. It took {query_duration:.2f} seconds to execute.")

    # Detach database and close connection
    c_enrol.execute("DETACH DATABASE db2")
    conn.close()

    # Save variables to a file (using pickle so it's easy to import)
    output_filename = 'more_than_20_at_enrolment.pkl'
    print(f"Saving {len(more_than_20_at_enrolment)} enrolids to {output_filename}...")
    
    with open(output_filename, 'wb') as f:
        pickle.dump(more_than_20_at_enrolment, f)
        
    total_time = time.time() - start_time
    
    print(f"Found {len(more_than_20_at_enrolment)} patients who were >= 20 at enrollment.")
    print(f"Successfully saved to {output_filename}")
    print(f"Total script runtime: {total_time:.2f} seconds.")

if __name__ == "__main__":
    main()
