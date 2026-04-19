# Escalation Model

This directory contains the trained ML model used for automatic complaint escalation.

## Model: `escalation_model.pkl`

A **GradientBoostingClassifier** serialized with `joblib`. The model predicts whether an unresolved complaint should be escalated to senior officials.

### Inputs (3 features)

| # | Feature         | Encoding                                                            |
|---|----------------|---------------------------------------------------------------------|
| 1 | `status`       | `assigned` (case-insensitive) -> 0, all other statuses -> 1        |
| 2 | `urgency`      | `low` -> 0, `medium` -> 1, `high` -> 2, `critical` -> 3           |
| 3 | `cluster_count`| Integer -- number of complaints sharing the same category + location|

### Output

| Value | Meaning                  |
|-------|--------------------------|
| 0     | Do not escalate          |
| 1     | Escalate the complaint   |

### Encoding Details

- **Status** is binary: `assigned` is encoded as 0; `open`, `in_progress`, etc. are 1.
- **Urgency** is ordinal: mapped to integers 0-3 in ascending severity.
- **Cluster count** is a raw integer representing geographic/category clustering of similar complaints.

### Training

The current model was trained on synthetic data for development purposes. For production use:

1. Export real complaint data from the `raw_complaints` Supabase table
2. Label rows with `escalated` = 1 where escalation was appropriate
3. Train a new GradientBoostingClassifier (or other classifier) using the 3-feature schema above
4. Serialize with `joblib.dump(model, "escalation_model.pkl")`
5. Place the `.pkl` file in this directory

### Performance

| Metric    | Score  |
|-----------|--------|
| F1 Score  | 0.9273 |
| Algorithm | GradientBoostingClassifier (scikit-learn) |

### Usage

The model is loaded lazily by `services/escalation.py` and called every 30 minutes by the `services/escalation_cron.py` scheduler job.
