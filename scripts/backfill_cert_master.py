import os
import pandas as pd
import re

# Base paths
BASE_DIR = r"C:\Users\min00\OneDrive\바탕 화면\시스템 분석 2학기\vulnerable_groups_RAG"
CERT_MASTER = os.path.join(BASE_DIR, "data", "processed", "master", "cert_master.csv")
RAW_DATA = os.path.join(BASE_DIR, "data", "raw", "csv", "data_cert_rows.csv")

def generate_normalized_key(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = text.strip()
    text = re.sub(r'[\s\-\/\.\·\ㆍ\(\)\[\]]', '_', text)
    text = re.sub(r'_+', '_', text)
    text = text.strip('_')
    return text

def main():
    print("Starting B-5: Backfilling cert_master exam details...")

    # 1. Load Cert Master
    if not os.path.exists(CERT_MASTER):
        print(f"Error: {CERT_MASTER} not found.")
        return
    df_master = pd.read_csv(CERT_MASTER)
    print(f"Loaded {len(df_master)} master records.")

    # 2. Add missing columns if they don't exist
    new_cols = [
        'exam_difficulty', 'exam_type_info', 'exam_fee_info', 
        'exam_pass_rate', 'exam_frequency', 'exam_subject_info', 
        'exam_eligibility_info'
    ]
    for col in new_cols:
        if col not in df_master.columns:
            df_master[col] = None

    # 3. Load Raw Data
    if not os.path.exists(RAW_DATA):
        print(f"Error: {RAW_DATA} not found.")
        return
    
    # Try different encodings
    try:
        # Based on previous tests, utf-8-sig seems correct for the data but console mangles it
        df_raw = pd.read_csv(RAW_DATA, encoding='utf-8-sig')
    except:
        df_raw = pd.read_csv(RAW_DATA, encoding='cp949')

    print(f"Loaded {len(df_raw)} raw records for backfill.")

    # 4. Create lookup Map (normalized_key -> raw_row)
    # We use normalization to be resilient to minor naming differences
    lookup = {}
    for idx, row in df_raw.iterrows():
        cname = str(row.get('자격증명', '')).strip()
        if not cname or cname == 'nan':
            continue
        key = generate_normalized_key(cname)
        lookup[key] = row

    # 5. Backfill
    updated_count = 0
    freq_data = []
    for idx, row in df_master.iterrows():
        key = row['normalized_key']
        if key in lookup:
            raw_row = lookup[key]
            
            # Map columns
            # Difficulty
            diff = str(raw_row.get('난이도', '')).strip()
            if diff and diff != 'nan':
                df_master.at[idx, 'exam_difficulty'] = diff
            
            # Type Info
            etype = str(raw_row.get('시험종류', '')).strip()
            if etype and etype != 'nan':
                df_master.at[idx, 'exam_type_info'] = etype
            
            # Subject Info
            subjects = []
            for sub_col in ['필기', '실기', '면접']:
                val = str(raw_row.get(sub_col, '')).strip()
                if val == '1' or val == '1.0':
                    subjects.append(sub_col)
            if subjects:
                df_master.at[idx, 'exam_subject_info'] = " + ".join(subjects)
            
            # Pass Rate Summary
            pass_rates = []
            for year in ['2024', '2023', '2022']:
                for cha in ['3차', '2차', '1차']:
                    rate_col = f"{year}년 {cha} 합격률"
                    if rate_col in raw_row:
                        val = str(raw_row.get(rate_col, '')).strip()
                        if val and val != 'nan' and val != '0':
                            try:
                                pass_rates.append(float(val))
                            except ValueError:
                                pass
            if pass_rates:
                avg_rate = sum(pass_rates) / len(pass_rates)
                df_master.at[idx, 'exam_pass_rate'] = f"최근 평균 합격률(종합): {avg_rate:.1f}%"
            
            # Exam Frequency
            freq = str(raw_row.get('검정 횟수', '')).strip()
            if freq and freq != 'nan' and freq != '0':
                try:
                    num_freq = int(float(freq))
                    df_master.at[idx, 'exam_frequency'] = f"연 {num_freq}회"
                    # We store grade_name to calculate average later
                    freq_data.append({'grade': str(row.get('grade_name', '')), 'freq': num_freq})
                except ValueError:
                    df_master.at[idx, 'exam_frequency'] = f"연 {freq}회"
                
            updated_count += 1
                
    # Calculate average frequency per grade
    grade_avg_freq = {}
    if freq_data:
        df_freq = pd.DataFrame(freq_data)
        if not df_freq.empty:
            grade_avg_freq = df_freq.groupby('grade')['freq'].mean().round().to_dict()

    # Impute missing frequencies
    imputed_count = 0
    for idx, row in df_master.iterrows():
        current_freq = df_master.at[idx, 'exam_frequency']
        if pd.isna(current_freq) or str(current_freq).strip() == '':
            grade = str(row.get('grade_name', ''))
            if grade in grade_avg_freq and not pd.isna(grade_avg_freq[grade]) and grade_avg_freq[grade] > 0:
                avg_val = int(grade_avg_freq[grade])
                df_master.at[idx, 'exam_frequency'] = f"연 {avg_val}회"
            else:
                df_master.at[idx, 'exam_frequency'] = "연 1회 미만"
            imputed_count += 1
            
    print(f"Imputed missing exam_frequency for {imputed_count} records.")

    # 6. Save updated master
    df_master.to_csv(CERT_MASTER, index=False, encoding='utf-8-sig')
    print(f"Updated {updated_count} records in {CERT_MASTER}.")
    print("Backfill complete.")

if __name__ == "__main__":
    main()
