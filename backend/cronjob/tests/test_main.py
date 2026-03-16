from unittest.mock import MagicMock
from backend.cronjob.main import CronJobScheduler, get_scheduler


def test_scheduler_initialization():
    """Test that the scheduler initializes correctly."""
    scheduler = CronJobScheduler()
    assert scheduler.scheduler is not None


def test_register_jobs(monkeypatch):
    """Test that jobs are registered correctly."""
    scheduler = CronJobScheduler()
    mock_add_job = MagicMock()
    scheduler.scheduler.add_job = mock_add_job

    # Mock the registered handlers and triggers
    mock_identify_handler = MagicMock()
    mock_email_handler = MagicMock()
    mock_interval_trigger = MagicMock()
    mock_cron_trigger = MagicMock()
    monkeypatch.setattr(
        "backend.cronjob.main.identify_stars_handler", mock_identify_handler)
    monkeypatch.setattr(
        "backend.cronjob.main.email_recommendation_handler", mock_email_handler)
    monkeypatch.setattr("backend.cronjob.main.IntervalTrigger",
                        lambda seconds: mock_interval_trigger)
    monkeypatch.setattr(
        "backend.cronjob.main.CronTrigger",
        lambda hour, minute: mock_cron_trigger,
    )

    scheduler._register_jobs()

    assert mock_add_job.call_count == 2
    expected_calls = [
        {
            "func": mock_identify_handler,
            "trigger": mock_interval_trigger,
            "id": "identify_satrs_job",
            "name": "Identify Stars Task",
            "replace_existing": True,
            "misfire_grace_time": 10,
        },
        {
            "func": mock_email_handler,
            "trigger": mock_cron_trigger,
            "id": "email_recommendation_job",
            "name": "Email Recommendation Task",
            "replace_existing": True,
            "misfire_grace_time": 10,
        },
    ]

    for expected in expected_calls:
        assert any(
            call.args == (expected["func"],)
            and call.kwargs == {
                "trigger": expected["trigger"],
                "id": expected["id"],
                "name": expected["name"],
                "replace_existing": expected["replace_existing"],
                "misfire_grace_time": expected["misfire_grace_time"],
            }
            for call in mock_add_job.call_args_list
        )


def test_start_scheduler(monkeypatch):
    """Test starting the scheduler."""
    mock_scheduler = MagicMock()
    monkeypatch.setattr(
        "backend.cronjob.main.BackgroundScheduler", lambda daemon: mock_scheduler)

    scheduler = CronJobScheduler()
    scheduler.scheduler = mock_scheduler  # Ensure the mock is used
    scheduler.start()


def test_shutdown_scheduler(monkeypatch):
    """Test shutting down the scheduler."""
    mock_scheduler = MagicMock()
    monkeypatch.setattr(
        "backend.cronjob.main.BackgroundScheduler", lambda daemon: mock_scheduler)

    scheduler = CronJobScheduler()
    scheduler.shutdown()

    mock_scheduler.shutdown.assert_called_once()


def test_pause_and_resume_jobs(monkeypatch):
    """Test pausing and resuming jobs."""
    mock_scheduler = MagicMock()
    monkeypatch.setattr(
        "backend.cronjob.main.BackgroundScheduler", lambda daemon: mock_scheduler)

    scheduler = CronJobScheduler()
    scheduler.pause_job("test_job")
    scheduler.resume_job("test_job")

    mock_scheduler.pause_job.assert_called_once_with("test_job")
    mock_scheduler.resume_job.assert_called_once_with("test_job")


def test_list_jobs(monkeypatch):
    """Test listing jobs."""
    mock_scheduler = MagicMock()
    mock_scheduler.get_jobs.return_value = [MagicMock(id="test_job")]
    monkeypatch.setattr(
        "backend.cronjob.main.BackgroundScheduler", lambda daemon: mock_scheduler)

    scheduler = CronJobScheduler()
    jobs = scheduler.list_jobs()

    assert len(jobs) == 1
    assert jobs[0].id == "test_job"


def test_get_scheduler():
    """Test the global scheduler instance."""
    scheduler1 = get_scheduler()
    scheduler2 = get_scheduler()

    assert scheduler1 is scheduler2  # Ensure the same instance is returned
