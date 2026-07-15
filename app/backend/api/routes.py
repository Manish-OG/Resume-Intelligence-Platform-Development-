from fastapi import APIRouter, UploadFile

router = APIRouter()


@router.post("/upload-job")
async def upload_job(file: UploadFile):
    raise NotImplementedError


@router.post("/upload-resume")
async def upload_resume(file: UploadFile):
    raise NotImplementedError


@router.post("/rank")
async def rank_candidates(job_id: int):
    raise NotImplementedError


@router.get("/results")
async def get_results(job_id: int):
    raise NotImplementedError


@router.get("/download")
async def download_results(job_id: int, fmt: str = "csv"):
    raise NotImplementedError
