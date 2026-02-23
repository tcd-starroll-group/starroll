import logging
import json
from fastapi import HTTPException

from backend.console.dal.rds.identify_stars_job import IdentifyStarsJob as IdentifyStarsJobDAL
from backend.console.dal.rds.client import get_db
from backend.console.utils.auth import verify_user_id_and_token

from gen.py.src.openapi_server.models.api_get_identify_stars_job_result_post_request import ApiGetIdentifyStarsJobResultPostRequest
from gen.py.src.openapi_server.models.api_get_identify_stars_job_result_post200_response import ApiGetIdentifyStarsJobResultPost200Response

logger = logging.getLogger(__name__)

async def api_get_identify_stars_job_result_post(
    request: ApiGetIdentifyStarsJobResultPostRequest
) -> ApiGetIdentifyStarsJobResultPost200Response:

    # 1. Auth
    verify_user_id_and_token(request.user_credentials.token, request.user_credentials.user_id)

    db_session = next(get_db())
    try:
        # 2. Fetch Job
        job = IdentifyStarsJobDAL.get_by_id(db_session, int(request.job_id))
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # 3. Secure check
        if job.user_id != int(request.user_credentials.user_id):
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
                data = json.loads(job.result) if isinstance(job.result, str) else job.result
                
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
                        "HIP": s.get("HIP") # Add this if your schema includes Hipparcos IDs
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

    except HTTPException as he:
        raise he
    except Exception as e:
        # This will print the EXACT line and error in your terminal
        logger.error("CRITICAL ERROR IN HANDLER", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")
    finally:
        db_session.close()