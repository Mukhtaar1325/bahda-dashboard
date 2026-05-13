-- Minimum tables recommended

-- 1. All original Kobo records
CREATE TABLE IF NOT EXISTS raw_submissions (
    _id TEXT PRIMARY KEY,
    submitter TEXT,
    submission_time DATETIME,
    raw_json TEXT
);

-- 2. Cleaned and standardized version
CREATE TABLE IF NOT EXISTS clean_submissions (
    _id TEXT PRIMARY KEY,
    enumerator_id TEXT,
    cluster_id TEXT,
    interview_date DATE,
    duration_minutes REAL,
    gps_lat REAL,
    gps_lon REAL,
    water_source TEXT,
    education_level TEXT,
    health_indicator TEXT,
    faculty_school TEXT,
    supervisor_id TEXT,
    subzone_letter TEXT,
    zone_num INTEGER,
    subzone_num INTEGER,
    cluster_match_flag BOOLEAN,
    FOREIGN KEY(_id) REFERENCES raw_submissions(_id)
);

-- 3. Derived indicators
CREATE TABLE IF NOT EXISTS indicators_household (
    _id TEXT PRIMARY KEY,
    child_filter BOOLEAN,
    school_filter BOOLEAN,
    poverty_band TEXT,
    fies_score INTEGER,
    water_safe_flag BOOLEAN,
    education_risk_flag BOOLEAN,
    business_flag BOOLEAN,
    FOREIGN KEY(_id) REFERENCES clean_submissions(_id)
);

-- 4. One row per issue found
CREATE TABLE IF NOT EXISTS quality_flags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id TEXT,
    flag_type TEXT, -- e.g., missing GPS, short interview, duplicate household ID
    description TEXT,
    FOREIGN KEY(submission_id) REFERENCES raw_submissions(_id)
);

-- 5. Daily totals and trends
CREATE TABLE IF NOT EXISTS daily_summary (
    date DATE PRIMARY KEY,
    total_submissions INTEGER,
    completed_interviews INTEGER,
    partial_interviews INTEGER
);

-- 6. Indicators by area
CREATE TABLE IF NOT EXISTS cluster_summary (
    cluster_id TEXT PRIMARY KEY,
    total_submissions INTEGER,
    avg_duration_minutes REAL
);

-- 7. Performance and quality by enumerator
CREATE TABLE IF NOT EXISTS enumerator_summary (
    enumerator_id TEXT PRIMARY KEY,
    total_submissions INTEGER,
    avg_duration_minutes REAL,
    incomplete_records INTEGER,
    suspicious_patterns INTEGER
);

-- 8. Submissions by Faculty
CREATE TABLE IF NOT EXISTS faculty_summary (
    faculty_school TEXT PRIMARY KEY,
    total_submissions INTEGER
);

-- 9. Supervisor Performance and Mapping
CREATE TABLE IF NOT EXISTS supervisor_summary (
    supervisor_id TEXT,
    subzone_code TEXT,
    faculty_school TEXT,
    cluster_id TEXT,
    total_submissions INTEGER,
    missing_count INTEGER
);
