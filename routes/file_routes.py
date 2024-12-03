from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.csv_service import DataService
from typing import List

router = APIRouter()
data_service = DataService()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a new data file (CSV or Excel)"""
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="Only CSV and Excel files are supported"
        )
    
    try:
        result = await data_service.update_data_source(file)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/schema")
async def get_schema():
    """Get the current data schema"""
    try:
        schema = data_service.get_schema()
        return {"schema": schema}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 