-- ===========================================================================
-- Module 36: Similar Patient Case Retrieval System
-- SQL Equivalent Documentation
-- ===========================================================================
-- NOTE: This module uses MongoDB. The SQL below shows the EQUIVALENT
-- relational database operations for academic reference.
-- ===========================================================================


-- ===========================================================================
-- 1. TABLE CREATION (DDL) — Equivalent of collections.py
-- ===========================================================================

CREATE TABLE PatientProfile (
    Patient_ID    INT PRIMARY KEY AUTO_INCREMENT,
    Age           INT NOT NULL,
    Gender        VARCHAR(10) NOT NULL CHECK (Gender IN ('Male', 'Female', 'Other')),
    Blood_Group   VARCHAR(5) NOT NULL,
    Address       VARCHAR(100),
    Lifestyle_Data VARCHAR(200)
);

CREATE TABLE ClinicalCase (
    Case_ID       INT PRIMARY KEY AUTO_INCREMENT,
    Patient_ID    INT NOT NULL,
    Symptom_Vector VARCHAR(50) NOT NULL,  -- e.g. "7,3,8,5,2"
    Severity_Level INT NOT NULL CHECK (Severity_Level BETWEEN 1 AND 10),
    FOREIGN KEY (Patient_ID) REFERENCES PatientProfile(Patient_ID)
);

CREATE TABLE Prognosis (
    Prognosis_ID  INT PRIMARY KEY AUTO_INCREMENT,
    Patient_ID    INT NOT NULL UNIQUE,
    Treatment     VARCHAR(200),
    Prognosis_Data VARCHAR(200),
    Survival_Rate DECIMAL(5,2),
    FOREIGN KEY (Patient_ID) REFERENCES PatientProfile(Patient_ID)
);

CREATE TABLE SimilarityAlgorithm (
    Algo_ID       INT PRIMARY KEY AUTO_INCREMENT,
    Algo_Name     VARCHAR(100) NOT NULL
);

CREATE TABLE SimilarityMatch (
    Match_ID      INT PRIMARY KEY AUTO_INCREMENT,
    Source_Patient_ID  INT NOT NULL,
    Matched_Patient_ID INT NOT NULL,
    Similarity_Score   DECIMAL(6,4),
    Confidence_Score   DECIMAL(6,4),
    Algo_ID            INT,
    Created_At         DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Source_Patient_ID) REFERENCES PatientProfile(Patient_ID),
    FOREIGN KEY (Matched_Patient_ID) REFERENCES PatientProfile(Patient_ID),
    FOREIGN KEY (Algo_ID) REFERENCES SimilarityAlgorithm(Algo_ID)
);

CREATE TABLE Feedback (
    Feedback_ID   INT PRIMARY KEY AUTO_INCREMENT,
    Match_ID      INT NOT NULL,
    Is_Useful     BOOLEAN,
    Survival_Rate DECIMAL(5,2),
    Doctor_Comments TEXT,
    Created_At    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Match_ID) REFERENCES SimilarityMatch(Match_ID)
);


-- ===========================================================================
-- 2. INDEXES — Performance Optimization
-- ===========================================================================

CREATE INDEX idx_clinical_patient ON ClinicalCase(Patient_ID);
CREATE UNIQUE INDEX idx_prognosis_patient ON Prognosis(Patient_ID);
CREATE INDEX idx_match_score ON SimilarityMatch(Similarity_Score DESC);
CREATE INDEX idx_match_source ON SimilarityMatch(Source_Patient_ID);
CREATE INDEX idx_feedback_match ON Feedback(Match_ID);


-- ===========================================================================
-- 3. VIEW — Patient Similarity Dashboard
-- ===========================================================================
-- MongoDB Equivalent: get_dashboard_view() in service.py
-- Uses: $lookup (JOIN), $sort, $project, $size

CREATE VIEW vw_patient_similarity_dashboard AS
SELECT 
    sm.Match_ID,
    pp1.Patient_ID AS Source_ID,
    pp1.Age AS Source_Age,
    pp1.Gender AS Source_Gender,
    pp2.Patient_ID AS Matched_ID,
    pp2.Age AS Matched_Age,
    pp2.Gender AS Matched_Gender,
    sm.Similarity_Score,
    sm.Confidence_Score,
    pr.Treatment,
    pr.Survival_Rate,
    (SELECT COUNT(*) FROM Feedback f WHERE f.Match_ID = sm.Match_ID) AS Feedback_Count
FROM SimilarityMatch sm
JOIN PatientProfile pp1 ON sm.Source_Patient_ID = pp1.Patient_ID
JOIN PatientProfile pp2 ON sm.Matched_Patient_ID = pp2.Patient_ID
LEFT JOIN Prognosis pr ON pp2.Patient_ID = pr.Patient_ID
ORDER BY sm.Similarity_Score DESC;


-- ===========================================================================
-- 4. STORED PROCEDURE — Find Similar Patients (Weighted Euclidean Distance)
-- ===========================================================================
-- MongoDB Equivalent: find_similar_patients() in service.py
-- Uses: $lookup, $addFields, $sqrt, $pow, $sort, $limit

DELIMITER //

CREATE PROCEDURE sp_find_similar_patients(
    IN p_source_id INT,
    IN p_w_age DECIMAL(3,2),
    IN p_w_severity DECIMAL(3,2),
    IN p_w_gender DECIMAL(3,2),
    IN p_w_blood DECIMAL(3,2)
)
BEGIN
    DECLARE v_min_age INT;
    DECLARE v_max_age INT;
    DECLARE v_source_age INT;
    DECLARE v_source_severity INT;
    DECLARE v_source_gender VARCHAR(10);
    DECLARE v_source_blood VARCHAR(5);

    -- Step 1: Get min/max age for normalization (Aggregate Function)
    SELECT MIN(Age), MAX(Age) INTO v_min_age, v_max_age FROM PatientProfile;

    -- Step 2: Get source patient data
    SELECT Age, Gender, Blood_Group
    INTO v_source_age, v_source_gender, v_source_blood
    FROM PatientProfile WHERE Patient_ID = p_source_id;

    SELECT Severity_Level INTO v_source_severity
    FROM ClinicalCase WHERE Patient_ID = p_source_id LIMIT 1;

    -- Step 3: Compute Weighted Euclidean Distance
    SELECT 
        pp.Patient_ID,
        pp.Age,
        pp.Gender,
        pp.Blood_Group,
        cc.Severity_Level,
        cc.Symptom_Vector,
        ROUND(
            1.0 / (1.0 + SQRT(
                p_w_age * POW((pp.Age - v_min_age) / GREATEST(v_max_age - v_min_age, 1) 
                              - (v_source_age - v_min_age) / GREATEST(v_max_age - v_min_age, 1), 2) +
                p_w_severity * POW((cc.Severity_Level - 1) / 9.0 
                                   - (v_source_severity - 1) / 9.0, 2) +
                p_w_gender * POW(CASE WHEN pp.Gender = v_source_gender THEN 0 ELSE 1 END, 2) +
                p_w_blood * POW(CASE WHEN pp.Blood_Group = v_source_blood THEN 0 ELSE 1 END, 2)
            )),
            4
        ) AS Similarity_Score,
        pr.Treatment,
        pr.Survival_Rate,
        pr.Prognosis_Data
    FROM PatientProfile pp
    JOIN ClinicalCase cc ON pp.Patient_ID = cc.Patient_ID
    LEFT JOIN Prognosis pr ON pp.Patient_ID = pr.Patient_ID
    WHERE pp.Patient_ID != p_source_id
    ORDER BY Similarity_Score DESC
    LIMIT 10;
END //

DELIMITER ;


-- ===========================================================================
-- 5. TRIGGER — Auto-update Confidence after Feedback Insert
-- ===========================================================================
-- MongoDB Equivalent: submit_feedback() in service.py (post-insert hook)
-- Uses: $match, $group, $avg → update_one

DELIMITER //

CREATE TRIGGER trg_after_feedback_insert
AFTER INSERT ON Feedback
FOR EACH ROW
BEGIN
    UPDATE SimilarityMatch
    SET Confidence_Score = (
        SELECT AVG(CASE WHEN Is_Useful = TRUE THEN 1.0 ELSE 0.0 END)
        FROM Feedback
        WHERE Match_ID = NEW.Match_ID
    )
    WHERE Match_ID = NEW.Match_ID;
END //

DELIMITER ;


-- ===========================================================================
-- 6. SAMPLE QUERIES
-- ===========================================================================

-- Get all patients
SELECT * FROM PatientProfile ORDER BY Patient_ID;

-- Get patient with clinical case and prognosis (JOIN)
SELECT pp.*, cc.Symptom_Vector, cc.Severity_Level, pr.Treatment, pr.Survival_Rate
FROM PatientProfile pp
JOIN ClinicalCase cc ON pp.Patient_ID = cc.Patient_ID
JOIN Prognosis pr ON pp.Patient_ID = pr.Patient_ID
WHERE pp.Patient_ID = 1;

-- Execute similarity search
CALL sp_find_similar_patients(1, 0.3, 0.3, 0.2, 0.2);

-- View dashboard
SELECT * FROM vw_patient_similarity_dashboard;

-- Get statistics (Aggregate Functions)
SELECT 
    (SELECT COUNT(*) FROM PatientProfile) AS Total_Patients,
    (SELECT COUNT(*) FROM ClinicalCase) AS Total_Cases,
    (SELECT COUNT(*) FROM SimilarityMatch) AS Total_Matches,
    (SELECT COUNT(*) FROM Feedback) AS Total_Feedback,
    (SELECT ROUND(AVG(Survival_Rate), 1) FROM Prognosis) AS Avg_Survival_Rate;
