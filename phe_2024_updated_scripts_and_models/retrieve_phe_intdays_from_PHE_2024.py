import sqlite3
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import roc_auc_score, confusion_matrix, roc_curve
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import os
import time

"""Purpose of this script:
Step 1: 
From pickle file eligible_patients.pkl, we extract list of patient ids that match the following criteria:
a) have been enrolled in the insurance plan for at least 1 consecutive year
b) are older than 20 years old
c) have diabetes.
Step 2. 
From the database PHE_2024.db, we extact the patients, all of their PHE codes, and INTDAYs - days when those phecodes were diagnosed and we save them as pkl"""

os.chdir('/Volumes/FastSSD_2/')

with open('/Users/annagerasimenko/phe_2024_updated_scripts_and_models/eligible_patients.pkl', "rb") as f:
    list_of_ids = pickle.load(f)

# Load dobyr for eligible patients to filter diagnoses by age
print("Loading demographics for age filtering...")
demo_con = sqlite3.connect('DEMO_2024.db')
demo_cursor = demo_con.cursor()
demo_cursor.execute("SELECT enrolid, dobyr FROM DEMO")
dobyr_lookup = {}
for eid, dob in demo_cursor:
    if eid in list_of_ids:
        dobyr_lookup[eid] = dob
demo_con.close()
print(f"Loaded dobyr for {len(dobyr_lookup):,} eligible patients")

def build_dict_phe_chunked_v2(list_of_ids, dobyr_lookup, db2, table, chunk_size=10000):

    """Extract PHE codes from PHE_2024.db and their intday - days of diagnosis.
    Only includes diagnoses where the patient was >= 20 years old."""
    conn_dx = sqlite3.connect(db2)
    c2 = conn_dx.cursor()
    
    query = f"""
    SELECT enrolid, intday, phecode
    FROM {table}
    """
    
    c2.execute(query)
    
    phe_patients = {}
    all_dxs = set()
    
    total_processed = 0
    total_matched = 0
    total_age_filtered = 0
    
    while True:
        chunk = c2.fetchmany(chunk_size)
        
        if not chunk:
            break
        
        for id, intday, dx in chunk:
            total_processed += 1
            
            if id in list_of_ids:
                dobyr = dobyr_lookup.get(id)
                if dobyr is None:
                    continue
                age = int(2003 + intday / 365.25 - dobyr)
                
                if age < 20:
                    total_age_filtered += 1
                    continue
                
                total_matched += 1
                
                if id not in phe_patients:
                    phe_patients[id] = {}
                
                if dx not in phe_patients[id]:
                    phe_patients[id][dx] = []
                
                phe_patients[id][dx].append(intday)
                all_dxs.add(dx)
        
        if total_processed % 100000 == 0:
            print(f"Processed {total_processed} rows, matched {total_matched}, age-filtered {total_age_filtered}...")
    
    conn_dx.close()
    
    print(f"Total processed: {total_processed}")
    print(f"Total matched: {total_matched}")
    print(f"Total filtered (age < 20): {total_age_filtered}")
    print(f"Unique patients: {len(phe_patients)}")
    print(f"Unique diagnoses: {len(all_dxs)}")
    
    return phe_patients, all_dxs

# Usage remains the same
start_time = time.time()
phe_patients, all_dxs = build_dict_phe_chunked_v2(list_of_ids, dobyr_lookup, 'PHE_2024.db', 'PHE')
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Script execution time: {elapsed_time:.4f} seconds")


with open('patient_info_phe_intday_2024.pkl', 'wb') as f:
    pickle.dump(
        {'phe_patients': phe_patients,
         'all_dxs': all_dxs},
        f
    )