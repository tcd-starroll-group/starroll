from unittest.mock import patch, MagicMock
from backend.cronjob.identify_stars import (
    identify_stars_handler,
    handle_one_identify_star_job,
    get_astronomy_net_session_key,
    submit_astronomy_net_job,
    get_astronomy_net_job_status,
    get_calibration,
    get_annotations
)
from backend.console.dal.rds.identify_stars_job import IdentifyStarsJob
from backend.constant.star_identify import *


def test_identify_stars_handler(monkeypatch):
    """Test the identify_stars_handler function."""
    mock_db_session = MagicMock()
    mock_job = MagicMock()
    mock_job.id = 1
    mock_job.status = STAR_IDENTIFY_JOB_STATUS_PENDING

    mock_list_by_job_status = MagicMock(return_value=[mock_job])
    monkeypatch.setattr(
        IdentifyStarsJob, "list_by_job_status", mock_list_by_job_status)

    mock_handle_job = MagicMock()
    monkeypatch.setattr(
        "backend.cronjob.identify_stars.handle_one_identify_star_job", mock_handle_job)

    def mock_get_db():
        yield mock_db_session

    monkeypatch.setattr("backend.cronjob.identify_stars.get_db", mock_get_db)

    identify_stars_handler()

    mock_list_by_job_status.assert_called_once()
    mock_handle_job.assert_called_once_with(mock_db_session, mock_job)


def test_handle_one_identify_star_job(monkeypatch):
    """Test the handle_one_identify_star_job function."""
    mock_db_session = MagicMock()
    mock_job = MagicMock()
    mock_job.id = 1
    mock_job.status = STAR_IDENTIFY_JOB_STATUS_PENDING

    mock_handle_pending = MagicMock()
    monkeypatch.setattr(
        "backend.cronjob.identify_stars.handle_one_identify_star_job_pending", mock_handle_pending)

    handle_one_identify_star_job(mock_db_session, mock_job)

    mock_handle_pending.assert_called_once_with(mock_db_session, mock_job)


def test_get_astronomy_net_session_key(monkeypatch):
    """Test the get_astronomy_net_session_key function."""
    mock_response = MagicMock()
    mock_response.text = '{"status": "success", "session": "test_session"}'

    mock_post = MagicMock(return_value=mock_response)
    monkeypatch.setattr("requests.post", mock_post)

    session_key = get_astronomy_net_session_key()

    assert session_key == "test_session"
    mock_post.assert_called_once()


def test_submit_astronomy_net_job(monkeypatch):
    """Test the submit_astronomy_net_job function."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"subid": 123}

    mock_post = MagicMock(return_value=mock_response)
    monkeypatch.setattr("requests.post", mock_post)

    result = submit_astronomy_net_job(b"image_data", "test_session")

    assert result["subid"] == 123
    mock_post.assert_called_once()


def test_get_astronomy_net_job_status(monkeypatch):
    """Test the get_astronomy_net_job_status function."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '{"status": "success"}'

    mock_get = MagicMock(return_value=mock_response)
    monkeypatch.setattr("requests.get", mock_get)

    status = get_astronomy_net_job_status(123)

    assert status == "success"
    mock_get.assert_called_once()


def test_get_calibration(monkeypatch):
    """Test the get_calibration function."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "parity": 1.0,
        "orientation": 45.0,
        "pixscale": 0.5,
        "radius": 2.0,
        "ra": 180.0,
        "dec": -45.0
    }

    mock_get = MagicMock(return_value=mock_response)
    monkeypatch.setattr("requests.get", mock_get)

    calibration = get_calibration(123)

    assert calibration.parity == 1.0
    assert calibration.orientation == 45.0
    assert calibration.pixscale == 0.5
    assert calibration.radius == 2.0
    assert calibration.ra == 180.0
    assert calibration.dec == -45.0
    mock_get.assert_called_once()


def test_get_annotations(monkeypatch):
    """Test the get_annotations function."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"annotations": [{
        "radius": 1.0,
        "names": ["Star A"],
        "pixelx": 100.0,
        "pixely": 200.0,
        "vmag": 5.5,
        "type": "star"
    }]}

    mock_get = MagicMock(return_value=mock_response)
    monkeypatch.setattr("requests.get", mock_get)

    annotations = get_annotations(123)

    assert annotations.annotations[0].names == ["Star A"]
    mock_get.assert_called_once()
