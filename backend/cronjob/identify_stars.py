import logging
import requests
import json
from backend.console.dal.rds.client import db_context
from backend.console.dal.rds.identify_stars_job import IdentifyStarsJob
from backend.constant.sort import SORT_ORDER_ASC
from backend.constant.star_identify import *
from backend.constant import tos as tos_const
from backend.console.dal.tos import download_bytes
from backend.config.settings import Settings
from backend.model.identify_stars import *

logger = logging.getLogger(__name__)


def identify_stars_handler():
    with db_context() as db_session:
        db_jobs = IdentifyStarsJob.list_by_job_status(
            db=db_session,
            statuses=[STAR_IDENTIFY_JOB_STATUS_PENDING,
                      STAR_IDENTIFY_JOB_STATUS_STARTING,
                      STAR_IDENTIFY_JOB_STATUS_RUNNING],
            limit=1000,
            offset=0,
            order=SORT_ORDER_ASC
        )

        for job in db_jobs:
            try:
                handle_one_identify_star_job(db_session, job)
            except Exception as e:
                logger.error(
                    f"Identify stars job failed, job id {job.id}, err: {e}")
                try:
                    IdentifyStarsJob.update(
                        db_session, job.id, status=STAR_IDENTIFY_JOB_STATUS_FAILED)
                    print(f"Job {job.id} status set to FAILED")
                except Exception as update_error:
                    logger.error(
                        f"Failed to update job status to FAILED, job id {job.id}, err: {update_error}")


def handle_one_identify_star_job(db_session, job: IdentifyStarsJob):
    logger.info(f"Processing job {job.id} with status {job.status}")
    if job.status == STAR_IDENTIFY_JOB_STATUS_PENDING:
        logger.info(f"Job {job.id} is in PENDING status, starting processing.")
        handle_one_identify_star_job_pending(db_session, job)
    elif job.status == STAR_IDENTIFY_JOB_STATUS_STARTING:
        logger.info(f"Job {job.id} is in STARTING status, checking progress.")
        handle_one_identify_star_job_starting(db_session, job)
    elif job.status == STAR_IDENTIFY_JOB_STATUS_RUNNING:
        logger.info(
            f"Job {job.id} is in RUNNING status, monitoring execution.")
        handle_one_identify_star_job_running(db_session, job)


def handle_one_identify_star_job_pending(db_session, job: IdentifyStarsJob):
    IdentifyStarsJob.update(
        db_session, job.id, status=STAR_IDENTIFY_JOB_STATUS_STARTING)
    # get photo from minio
    photo_bytes = download_bytes(
        job.image_key, tos_const.IDENTIFY_STARS_BUCKET_NAME)
    astronomy_key = get_astronomy_net_session_key()
    ret = submit_astronomy_net_job(
        photo_bytes, astronomy_key)
    IdentifyStarsJob.update(
        db_session, job.id, astronomy_net_job_id=ret['subid'])


def handle_one_identify_star_job_starting(db_session, job: IdentifyStarsJob):
    status = get_astronomy_net_job_status(job.astronomy_net_job_id)
    if status is not None:
        IdentifyStarsJob.update(
            db_session, job.id, status=STAR_IDENTIFY_JOB_STATUS_RUNNING)


def handle_one_identify_star_job_running(db_session, job: IdentifyStarsJob):
    status = get_astronomy_net_job_status(job.astronomy_net_job_id)
    if status == ASTRONOMY_NET_JOB_STATUS_FAILURE:
        logger.error(
            f"Astronomy.net job failed, astronomy job id {job.astronomy_net_job_id}")
        IdentifyStarsJob.update(
            db_session, job.id, status=STAR_IDENTIFY_JOB_STATUS_FAILED)
    if status == ASTRONOMY_NET_JOB_STATUS_SUCCESS:
        calibration = get_calibration(job.astronomy_net_job_id)
        annotations = get_annotations(job.astronomy_net_job_id)
        ret = AstronomyNetResult(
            calibration=calibration,
            stars=annotations.annotations)
        IdentifyStarsJob.update(db_session, job.id, result=ret.model_dump_json(),
                                status=STAR_IDENTIFY_JOB_STATUS_SUCCEEDED)


def get_astronomy_net_session_key():
    R = requests.post(f'{Settings.astronomy_net_endpoint}/api/login',
                      data={'request-json': json.dumps({"apikey": ""})})

    try:
        response_data = json.loads(R.text)
        if response_data.get("status") == "success":
            return response_data.get("session")
    except json.JSONDecodeError:
        pass

    return None


def submit_astronomy_net_job(image_data, session_token):
    logger.debug(
        f"Submitting astronomy.net job with session token: {session_token}")
    # Prepare the JSON request data
    request_json = {
        "publicly_visible": "y",
        "allow_modifications": "d",
        "session": session_token,
        "allow_commercial_use": "d"
    }

    # Prepare multipart/form-data
    files = {
        'request-json': ('', json.dumps(request_json), 'text/plain'),
        'file': ('test.png', image_data, 'application/octet-stream')
    }

    # Send POST request
    response = requests.post(
        f"{Settings.astronomy_net_endpoint}/api/upload", files=files)

    logger.debug(f"Status Code: {response.status_code}")
    logger.debug(f"Raw Response: {response.text}")

    try:
        return response.json()
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        logger.error(f"Raw Response: {response.text}")
        raise


def get_astronomy_net_job_status(job_id: int) -> str:
    logger.debug(f"Fetching astronomy.net job status for job ID: {job_id}")
    response = requests.get(
        f"{Settings.astronomy_net_endpoint}/api/jobs/{job_id}")

    logger.debug(f"Status Code: {response.status_code}")
    logger.debug(f"Raw Response: {response.text}")

    if response.status_code == 404:
        logger.warning(
            f"Job ID {job_id} not found on astronomy.net (404). Returning None.")
        return None

    try:
        response_data = json.loads(response.text)
        logger.debug(f"Parsed Response: {response_data}")
        return response_data.get("status")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        logger.error(f"Raw Response: {response.text}")
        raise


def get_calibration(job_id: int) -> CalibrationResult:
    url = f"{Settings.astronomy_net_endpoint}/api/jobs/{job_id}/calibration/"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return CalibrationResult(**data)


def get_annotations(job_id: int) -> GetAnnotationResult:
    url = f"{Settings.astronomy_net_endpoint}/api/jobs/{job_id}/annotations/"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return GetAnnotationResult(**data)


if __name__ == "__main__":
    identify_stars_handler()
