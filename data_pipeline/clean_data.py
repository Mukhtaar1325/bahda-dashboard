import pandas as pd
import json

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
        
    clean_df['enumerator_id'] = raw_df.get('004. Enumerator ID', raw_df.get('enumerator_id', 'unknown_enum'))
    clean_df['cluster_id'] = raw_df.get('001. Cluster/Quarter', raw_df.get('cluster_id', 'unknown_cluster'))
    
    # Process interview date
    if 'start' in raw_df.columns:
        clean_df['interview_date'] = pd.to_datetime(raw_df['start'], errors='coerce').dt.date
    else:
        clean_df['interview_date'] = pd.NaT
    
    # Calculate duration
    if 'start' in raw_df.columns and 'end' in raw_df.columns:
        start_dt = pd.to_datetime(raw_df['start'], errors='coerce')
        end_dt = pd.to_datetime(raw_df['end'], errors='coerce')
        clean_df['duration_minutes'] = (end_dt - start_dt).dt.total_seconds() / 60.0
    else:
        clean_df['duration_minutes'] = 0.0

    # Extract GPS reliably using multiple possible patterns
    lat_cols = ['_006. GPS Coordinates_latitude', '006. GPS Coordinates_latitude', 'gps_latitude', '_gps_latitude', '_geolocation_latitude']
    lon_cols = ['_006. GPS Coordinates_longitude', '006. GPS Coordinates_longitude', 'gps_longitude', '_gps_longitude', '_geolocation_longitude']
    
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
            
        combined_col = '006. GPS Coordinates' if '006. GPS Coordinates' in raw_df.columns else 'gps'
        if combined_col in raw_df.columns:
            gps_data = raw_df[combined_col].apply(parse_gps)
            clean_df['gps_lat'] = clean_df['gps_lat'].fillna(gps_data.apply(lambda x: x[0]))
            clean_df['gps_lon'] = clean_df['gps_lon'].fillna(gps_data.apply(lambda x: x[1]))

    # General info
    clean_df['water_source'] = raw_df.get('109. What is the primary source of drinking water?', raw_df.get('water_source', 'unspecified'))
    clean_df['education_level'] = raw_df.get('106. Highest level of education completed by the HH Head?', raw_df.get('education_level', 'unspecified'))
    clean_df['health_indicator'] = raw_df.get('420. Overall, how satisfied are you with the public health and environment in your area? (1-5 Scale)', raw_df.get('health_indicator', 'unspecified'))
    
    # Faculty info
    clean_df['faculty_school'] = raw_df.get('Faculty / School', raw_df.get('Faculty_School', 'unspecified'))

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
