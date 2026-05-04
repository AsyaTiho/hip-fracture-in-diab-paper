import pandas as pd
import pickle
import time
"""Purpose of this script is to aggregate the data from the PHE2024 database into a single DataFrame.
The input is a pickle file containing the patient information with the PHE codes and the corresponding intdays.
The output is a pickle file containing the aggregated DataFrame."""
# Start timing
start_time = time.time()

# ========================================
# STEP 1: Load the data
# ========================================
print("Loading patient_info_phe_intday_2024.pkl...")
load_start = time.time()

with open('/Users/annagerasimenko/phe_2024_updated_scripts_and_models/patient_info_phe_intday_2024.pkl', 'rb') as f:
    data = pickle.load(f)

patient_info_phe = data["phe_patients"]

print(f"Loaded in {time.time() - load_start:.2f} seconds")

# ========================================
# STEP 2: Convert to aggregated DataFrame
# ========================================
print("\nConverting to aggregated DataFrame...")
convert_start = time.time()

rows = []
for enrolid, diagnoses in patient_info_phe.items():
    for phecode, intdays in diagnoses.items():
        rows.append({
            'enrolid': enrolid,
            'phecode': phecode,
            'first_intday': min(intdays),
            'last_intday': max(intdays),
            'count': len(intdays),
            'all_intdays': intdays 
        })

df_aggregated = pd.DataFrame(rows)

print(f"Conversion completed in {time.time() - convert_start:.2f} seconds")

# ========================================
# STEP 3: Save the aggregated DataFrame
# ========================================
print("\n" + "="*80)
print("SAVING AGGREGATED DATAFRAME")
print("="*80)

save_start = time.time()

# Save as pickle (faster loading, preserves data types)
df_aggregated.to_pickle('/Users/annagerasimenko/phe_2024_updated_scripts_and_models/phe_aggregated_2024.pkl')
print("Saved: phe_aggregated_2024.pkl") 

# Save as CSV (human-readable, but loses list format for all_intdays)
df_aggregated.to_csv('/Users/annagerasimenko/phe_2024_updated_scripts_and_models/phe_aggregated_2024.csv', index=False)
print("Saved: phe_aggregated_2024.csv")

print(f"Saving completed in {time.time() - save_start:.2f} seconds")

# ========================================
# STEP 4: Total time
# ========================================
total_time = time.time() - start_time
print("\n" + "="*80)
print(f"TOTAL EXECUTION TIME: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
print("="*80)

# print("\nTo load the aggregated data later:")
# print("  df = pd.read_pickle('phe_aggregated_2024.pkl')")