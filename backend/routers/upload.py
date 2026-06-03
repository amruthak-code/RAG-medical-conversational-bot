import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from models import Patient
from services.excel_parser import parse_excel, PG_COLUMNS, EMBED_COLUMNS
from services.pinecone_service import upsert_patient_docs

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload")
async def upload_excel(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are accepted.")

    file_bytes = await file.read()
    try:
        rows = parse_excel(file_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    patient_ids: list[str] = []

    for row in rows:
        patient_id = str(row["patient_id"]).strip()
        if not patient_id:
            continue

        pg_data = {col: str(row.get(col, "") or "") for col in PG_COLUMNS}
        patient = Patient(**pg_data)
        await session.merge(patient)

        embed_docs = {
            col: str(row.get(col, "") or "")
            for col in EMBED_COLUMNS
        }
        try:
            await asyncio.to_thread(upsert_patient_docs, patient_id, embed_docs)
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Pinecone error for patient {patient_id}: {type(exc).__name__}: {exc}",
            )

        patient_ids.append(patient_id)

    await session.commit()
    return {"patients": patient_ids, "count": len(patient_ids)}
