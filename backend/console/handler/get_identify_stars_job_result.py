import logging
import json
from fastapi import HTTPException

from backend.console.dal.rds.identify_stars_job import IdentifyStarsJob as IdentifyStarsJobDAL
from backend.console.dal.rds.client import db_context
from backend.console.dal.tos import get_presigned_get_url
from backend.console.utils.auth import get_current_user_id
from backend.constant import tos as tos_const

from backend.model.identify_stars import AstronomyNetResult
from backend.console.utils.star_name import get_hip_by_name

from openapi_server.models.api_get_identify_stars_job_result_post_request import ApiGetIdentifyStarsJobResultPostRequest
from openapi_server.models.identify_stars_job_result import IdentifyStarsJobResult
from openapi_server.models.identify_stars_job_result_identified_stars_inner import IdentifyStarsJobResultIdentifiedStarsInner
from openapi_server.models.equatorial_coordinate import EquatorialCoordinate

logger = logging.getLogger(__name__)


async def api_get_identify_stars_job_result_post(
    request: ApiGetIdentifyStarsJobResultPostRequest
) -> IdentifyStarsJobResult:

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
        stars_list = []
        ori_image_url = None
        center_info = None

        if job.result:
            try:
                # Load JSON and parse with AstronomyNetResult
                raw = json.loads(job.result) if isinstance(
                    job.result, str) else job.result
                result = AstronomyNetResult.model_validate(raw)

                # 1. Map Calibration -> Center
                center_info = EquatorialCoordinate(
                    rightAscension=result.calibration.ra,
                    declination=result.calibration.dec,
                )

                # 2. Map Stars -> identifiedStars
                seen_hips: set[int] = set()
                for s in result.stars:
                    hip = next(
                        (h for n in s.names if (h := get_hip_by_name(n)) is not None),
                        None,
                    )
                    if hip is not None:
                        if hip in seen_hips:
                            continue
                        seen_hips.add(hip)
                    stars_list.append(
                        IdentifyStarsJobResultIdentifiedStarsInner(
                            names=s.names,
                            pixelX=s.pixelx,
                            pixelY=s.pixely,
                            vmag=s.vmag,
                            hip=hip,
                        ))
            except Exception as e:
                logger.error(f"Mapping error for job {job.id}: {e}")

        if job.image_key:
            try:
                ori_image_url = get_presigned_get_url(
                    job.image_key,
                    tos_const.IDENTIFY_STARS_BUCKET_NAME,
                )
            except Exception as e:
                logger.error(
                    f"Failed to build presigned image URL for job {job.id}: {e}")

        # 5. Final Return
        return IdentifyStarsJobResult(
            center=center_info,
            identifiedStars=stars_list,
            oriImageUrl=ori_image_url,
        )
