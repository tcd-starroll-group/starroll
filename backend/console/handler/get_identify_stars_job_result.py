import logging
import json
from fastapi import HTTPException

from backend.console.dal.rds.identify_stars_job import IdentifyStarsJob as IdentifyStarsJobDAL
from backend.console.dal.rds.client import db_context
from backend.console.utils.auth import get_current_user_id

from openapi_server.models.api_get_identify_stars_job_result_post_request import ApiGetIdentifyStarsJobResultPostRequest
from openapi_server.models.api_get_identify_stars_job_result_post200_response import ApiGetIdentifyStarsJobResultPost200Response

logger = logging.getLogger(__name__)


async def api_get_identify_stars_job_result_post(
    request: ApiGetIdentifyStarsJobResultPostRequest
) -> ApiGetIdentifyStarsJobResultPost200Response:

    user_id = get_current_user_id()

    with db_context() as db_session:
        # 2. Fetch Job
        job = IdentifyStarsJobDAL.get_by_id(db_session, int(request.job_id))
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # 3. Secure check
        if job.user_id != int(user_id):
            raise HTTPException(status_code=403, detail="Unauthorized")

        # 4. Data Processing
        # Default empty structures to satisfy the OpenAPI model
        center_info = {
            "rightAscension": 0.0,
            "declination": 0.0,
            "radius": 0.0,
            "orientation": 0.0
        }
        stars_list = []

        if job.result:
            try:
                # Load JSON (Handle string or dict)
                data = json.loads(job.result) if isinstance(
                    job.result, str) else job.result

                # 1. Map Calibration -> Center
                cal = data.get("calibration", {})
                if cal:
                    center_info = {
                        "rightAscension": float(cal.get("ra", 0.0)),
                        "declination": float(cal.get("dec", 0.0)),
                        "radius": float(cal.get("radius", 0.0)),
                        "orientation": float(cal.get("orientation", 0.0))
                    }

                # 2. Map Stars -> identifiedStars
                raw_stars = data.get("stars", [])
                for s in raw_stars:
                    stars_list.append({
                        # The schema expects "names" (list of strings), "pixelX", "pixelY", "vmag"
                        "names": s.get("names", []),
                        "pixelX": float(s.get("pixelx", 0.0)),
                        "pixelY": float(s.get("pixely", 0.0)),
                        "vmag": float(s.get("vmag", 0.0)),
                        # Add this if your schema includes Hipparcos IDs
                        "HIP": s.get("HIP")
                    })
            except Exception as e:
                logger.error(f"Mapping error for job {job.id}: {e}")

        # 5. Final Return
        return ApiGetIdentifyStarsJobResultPost200Response(
            identify_stars_jobs_list=[{
                "jobID": str(job.id),
                "status": job.status,
                "center": center_info,
                "identifiedStars": stars_list,
                "imageKey": job.image_key or "",
                "createTime": job.created_at.isoformat() if job.created_at else None
            }]
        )
