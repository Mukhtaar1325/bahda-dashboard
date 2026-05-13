import pandas as pd

def calculate_indicators(clean_df):
    """Calculates household indicators from clean data."""
    if clean_df.empty:
        return pd.DataFrame()
        
    indicators = pd.DataFrame()
    indicators['_id'] = clean_df['_id']
    
    indicators['child_filter'] = False 
    indicators['school_filter'] = False
    indicators['poverty_band'] = 'medium'
    indicators['fies_score'] = 0
    indicators['water_safe_flag'] = clean_df['water_source'].str.contains('pipe|tap', case=False, na=False)
    indicators['education_risk_flag'] = clean_df['education_level'].str.contains('none|primary', case=False, na=False)
    indicators['business_flag'] = False
    
    return indicators

def generate_daily_summary(clean_df):
    if clean_df.empty:
        return pd.DataFrame()
    daily = clean_df.groupby('interview_date', dropna=False).agg(
        total_submissions=('_id', 'count'),
        avg_duration=('duration_minutes', 'mean')
    ).reset_index()
    daily['completed_interviews'] = daily['total_submissions']
    daily['partial_interviews'] = 0
    daily.rename(columns={'interview_date': 'date'}, inplace=True)
    return daily

def generate_cluster_summary(clean_df):
    if clean_df.empty:
        return pd.DataFrame()
    cluster = clean_df.groupby('cluster_id').agg(
        total_submissions=('_id', 'count'),
        avg_duration_minutes=('duration_minutes', 'mean')
    ).reset_index()
    return cluster

def generate_enumerator_summary(clean_df):
    if clean_df.empty:
        return pd.DataFrame()
    enum = clean_df.groupby('enumerator_id').agg(
        total_submissions=('_id', 'count'),
        avg_duration_minutes=('duration_minutes', 'mean')
    ).reset_index()
    enum['incomplete_records'] = 0
    enum['suspicious_patterns'] = 0
    return enum

def generate_faculty_summary(clean_df):
    if clean_df.empty or 'faculty_school' not in clean_df.columns:
        return pd.DataFrame()
    fac = clean_df.groupby('faculty_school').agg(
        total_submissions=('_id', 'count')
    ).reset_index()
    return fac

def generate_supervisor_summary(clean_df):
    if clean_df.empty:
        return pd.DataFrame()
    
    # Helper to join unique values (if needed, but here we group by them)
    def join_unique(series):
        return ", ".join(sorted(set(str(x) for x in series if pd.notna(x))))

    # Group by supervisor_id, faculty, and cluster to see distinct combinations
    summary = clean_df.groupby(['supervisor_id', 'faculty_school', 'cluster_id']).agg(
        total_submissions=('_id', 'count'),
        subzone_code=('subzone_letter', lambda x: join_unique(x))
    ).reset_index()
    
    # Calculate missing count
    summary['missing_count'] = 0
    summary.loc[summary['supervisor_id'] == 'MISSING', 'missing_count'] = summary['total_submissions']
    
    return summary

def generate_quality_flags(clean_df):
    """Detects data quality issues, specifically GPS anomalies."""
    if clean_df.empty:
        return pd.DataFrame()
        
    flags = []
    
    # Bounding box for Somaliland (approximate)
    MIN_LAT, MAX_LAT = 8.0, 12.0
    MIN_LON, MAX_LON = 42.0, 49.0
    
    # Group by cluster to find outliers
    cluster_centers = clean_df.groupby('cluster_id')[['gps_lat', 'gps_lon']].median().to_dict('index')
    
    for _, row in clean_df.iterrows():
        sub_id = row['_id']
        lat = row.get('gps_lat')
        lon = row.get('gps_lon')
        cluster = row.get('cluster_id')
        
        # 1. Check for Missing/Zero GPS
        if pd.isna(lat) or pd.isna(lon) or (abs(lat) < 0.1 and abs(lon) < 0.1):
            flags.append({
                'submission_id': sub_id,
                'flag_type': 'Missing GPS',
                'description': 'GPS coordinates are missing or zero.'
            })
            continue # No need to check other GPS flags if it's missing
            
        # 2. Check for Out of Bounds
        if not (MIN_LAT <= lat <= MAX_LAT and MIN_LON <= lon <= MAX_LON):
            flags.append({
                'submission_id': sub_id,
                'flag_type': 'Out of Bounds GPS',
                'description': f'Coordinates ({lat}, {lon}) are outside Somaliland region.'
            })
            
        # 3. Cluster Mismatch (Point is far from its cluster median)
        center = cluster_centers.get(cluster)
        if center and not pd.isna(center['gps_lat']):
            dist_sq = (lat - center['gps_lat'])**2 + (lon - center['gps_lon'])**2
            # ~0.05 deg squared is roughly 5.5km distance
            if dist_sq > 0.0025: 
                flags.append({
                    'submission_id': sub_id,
                    'flag_type': 'Location Mismatch',
                    'description': f'Point is far from the center of cluster {cluster}. Possible data entry error.'
                })
                
    return pd.DataFrame(flags)
