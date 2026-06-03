import io
import pandas as pd

REQUIRED_COLUMNS = [
    "patient_id",
    "patient_name",
    "email",
    "dob",
    "emergency_contact_name",
    "emergency_contact_email",
    "procedure_name",
    "procedure_date",
    "followup_date",
    "followup_contact",
    "discharge_summary",
    "medications",
    "red_flags",
    "diet_restrictions",
    "followup_schedule",
]

PG_COLUMNS = REQUIRED_COLUMNS[:10]
EMBED_COLUMNS = REQUIRED_COLUMNS[10:]


def parse_excel(file_bytes: bytes) -> list[dict]:
    df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl", dtype=str)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = df[REQUIRED_COLUMNS].fillna("")
    return df.to_dict(orient="records")
