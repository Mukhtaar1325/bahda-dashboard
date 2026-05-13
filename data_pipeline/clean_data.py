import pandas as pd
import json
import re

def clean_submissions(raw_df):
    """Cleans raw Kobo dataframe to match our schema using specific CSV headers."""
    if raw_df.empty:
        return pd.DataFrame()
    
    clean_df = pd.DataFrame()
    
    if '_id' in raw_df.columns:
        clean_df['_id'] = raw_df['_id'].astype(str)
    elif 'deviceid' in raw_df.columns:
        clean_df['_id'] = raw_df['deviceid'].astype(str) + '_' + raw_df.index.astype(str)
    else:
        clean_df['_id'] = raw_df.index.astype(str)
        
    # Get Enumerator ID (Try column with leading space first, then others)
    clean_df['enumerator_id'] = raw_df.get(' Enumerator ID', 
                                   raw_df.get('003. Enumerator ID', 
                                   raw_df.get('004. Enumerator ID', 'unknown_enum')))
    
    # If it's a string like "D1.3 18063", extract just the numeric ID
    def extract_id(val):
        if pd.isna(val) or str(val).strip() == '': return "MISSING"
        match = re.search(r'(\d{4,10})$', str(val).strip()) # Look for 4-10 digits at the end
        if match: return match.group(1)
        return str(val).strip()
    
    clean_df['enumerator_id'] = clean_df['enumerator_id'].apply(extract_id)
    
    clean_df['cluster_id'] = raw_df.get('001. Cluster/Quarter', raw_df.get('cluster_id', 'unknown_cluster'))
    
    # Process interview date (Try multiple columns and pick the best one)
    date_cols = ['start', 'Start time', '_submission_time']
    clean_df['interview_date'] = pd.NaT
    active_date_col = None
    
    for col in date_cols:
        if col in raw_df.columns:
            temp_dates = pd.to_datetime(raw_df[col], errors='coerce').dt.date
            if not temp_dates.isnull().all():
                clean_df['interview_date'] = temp_dates
                active_date_col = col
                break
    
    # Calculate duration
    end_col = next((c for c in ['end', 'End time'] if c in raw_df.columns), None)
    if active_date_col and end_col:
        start_dt = pd.to_datetime(raw_df[active_date_col], errors='coerce')
        end_dt = pd.to_datetime(raw_df[end_col], errors='coerce')
        clean_df['duration_minutes'] = (end_dt - start_dt).dt.total_seconds() / 60.0
    else:
        clean_df['duration_minutes'] = 0.0

    # Extract GPS reliably using multiple possible patterns
    lat_cols = ['_004. GPS Coordinates_latitude', '_006. GPS Coordinates_latitude', '006. GPS Coordinates_latitude', 'gps_latitude', '_gps_latitude', '_geolocation_latitude']
    lon_cols = ['_004. GPS Coordinates_longitude', '_006. GPS Coordinates_longitude', '006. GPS Coordinates_longitude', 'gps_longitude', '_gps_longitude', '_geolocation_longitude']
    
    clean_df['gps_lat'] = pd.Series(dtype=float)
    clean_df['gps_lon'] = pd.Series(dtype=float)
    
    for lat_col in lat_cols:
        if lat_col in raw_df.columns:
            clean_df['gps_lat'] = pd.to_numeric(raw_df[lat_col], errors='coerce')
            break
            
    for lon_col in lon_cols:
        if lon_col in raw_df.columns:
            clean_df['gps_lon'] = pd.to_numeric(raw_df[lon_col], errors='coerce')
            break
            
    # Fallback: Parse combined GPS string if individual columns are empty/missing
    if clean_df['gps_lat'].isnull().all() or '006. GPS Coordinates' in raw_df.columns:
        def parse_gps(val):
            try:
                if pd.isna(val) or not isinstance(val, str): return None, None
                parts = val.split()
                if len(parts) >= 2:
                    return float(parts[0]), float(parts[1])
            except: pass
            return None, None
            
        combined_col = next((c for c in ['004. GPS Coordinates', '006. GPS Coordinates', 'gps'] if c in raw_df.columns), None)
        if combined_col in raw_df.columns:
            gps_data = raw_df[combined_col].apply(parse_gps)
            clean_df['gps_lat'] = clean_df['gps_lat'].fillna(gps_data.apply(lambda x: x[0]))
            clean_df['gps_lon'] = clean_df['gps_lon'].fillna(gps_data.apply(lambda x: x[1]))

    # General info
    clean_df['water_source'] = raw_df.get('109. What is the primary source of drinking water?', raw_df.get('water_source', 'unspecified'))
    clean_df['education_level'] = raw_df.get('106. Highest level of education completed by the HH Head?', raw_df.get('education_level', 'unspecified'))
    clean_df['health_indicator'] = raw_df.get('420. Overall, how satisfied are you with the public health and environment in your area? (1-5 Scale)', raw_df.get('health_indicator', 'unspecified'))
    
    # Faculty info
    clean_df['faculty_school'] = raw_df.get('003. Faculty_School', raw_df.get('Faculty / School', raw_df.get('Faculty_School', 'unspecified')))

    # --- Supervisor ID & Subzone Extraction ---
    sup_val = raw_df.get('Supervisor ID', '')
    
    # Defaults
    clean_df['supervisor_id'] = 'MISSING'
    clean_df['subzone_letter'] = None
    clean_df['zone_num'] = None
    clean_df['subzone_num'] = None
    clean_df['cluster_match_flag'] = True # Default to true, will validate below

    # Mapping based on user input
    cluster_mapping = {
        'A': 'Sh. Osman',
        'B': 'Sh. Ali Jauhar',
        'C': 'Sh. Ahmed Salan',
        'D': 'Sh. Makahil'
    }

    def parse_supervisor(val, current_cluster):
        if pd.isna(val) or str(val).strip() == '' or str(val).lower() == 'nan':
            return 'MISSING', None, None, None, False
        
        val_str = str(val).strip()
        
        # 1. Look for Subzone + 7-digit ID: ([A-Z]\d\.?\d?)\D*(\d{7})
        # This handles A1.1 4511559, C1.1.1234567, B12-9876543, etc.
        match = re.search(r'([A-Z])(\d)\.?(\d)?\D*(\d{7})', val_str, re.IGNORECASE)
        if match:
            letter = match.group(1).upper()
            zone = int(match.group(2))
            sub = int(match.group(3)) if match.group(3) else 1
            sup_id = match.group(4)
            
            # Validate Cluster
            expected_cluster = cluster_mapping.get(letter)
            match_flag = True
            if expected_cluster and current_cluster:
                if expected_cluster.lower() not in str(current_cluster).lower():
                    match_flag = False
                    
            return sup_id, letter, zone, sub, match_flag
            
        # 2. Fallback: Just look for any 7 digits
        match_id_only = re.search(r'(\d{7})', val_str)
        if match_id_only:
            return match_id_only.group(1), None, None, None, True
            
        # 3. Last fallback: Capture anything numeric
        match_any_num = re.search(r'(\d+)', val_str)
        if match_any_num:
            return match_any_num.group(1), None, None, None, True
            
        return 'UNPARSEABLE', None, None, None, False

    # Apply parsing
    # Need to pass cluster_id for validation
    for idx, row in raw_df.iterrows():
        c_id = clean_df.at[idx, 'cluster_id']
        s_id, s_letter, z_num, sz_num, m_flag = parse_supervisor(row.get('Supervisor ID'), c_id)
        
        clean_df.at[idx, 'supervisor_id'] = s_id
        clean_df.at[idx, 'subzone_letter'] = s_letter
        clean_df.at[idx, 'zone_num'] = z_num
        clean_df.at[idx, 'subzone_num'] = sz_num
        clean_df.at[idx, 'cluster_match_flag'] = m_flag

    return clean_df

def prepare_raw_for_db(raw_df):
    """Prepares raw_submissions table format."""
    if raw_df.empty:
        return pd.DataFrame()
        
    out = pd.DataFrame()
    if '_id' in raw_df.columns:
        out['_id'] = raw_df['_id'].astype(str)
    elif 'deviceid' in raw_df.columns:
        out['_id'] = raw_df['deviceid'].astype(str) + '_' + raw_df.index.astype(str)
    else:
        out['_id'] = raw_df.index.astype(str)
        
    out['submitter'] = raw_df.get('003. Enumerator Name', raw_df.get('_submitted_by', 'unknown'))
    out['submission_time'] = raw_df.get('start', raw_df.get('_submission_time', None))
    # Don't fail json encode if containing NaNs
    out['raw_json'] = raw_df.apply(lambda row: json.dumps({k: str(v) for k, v in row.to_dict().items()}), axis=1)
    return out
