from unittest.mock import MagicMock, patch
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

    # Mock the identify_stars_handler function and IntervalTrigger
    mock_handler = MagicMock()
    mock_trigger = MagicMock()
    monkeypatch.setattr(
        "backend.cronjob.main.identify_stars_handler", mock_handler)
    monkeypatch.setattr("backend.cronjob.main.IntervalTrigger",
                        lambda seconds: mock_trigger)

    scheduler._register_jobs()

    # Check that the identify_stars_handler job is registered
    mock_add_job.assert_called()  # Ensure the method was called

    # Verify the arguments passed to the call
    call_args = mock_add_job.call_args
    if call_args.kwargs:  # If keyword arguments are used
        kwargs = call_args.kwargs
        assert kwargs["trigger"] == mock_trigger
        assert kwargs["id"] == "identify_satrs_job"
        assert kwargs["name"] == "Identify Stars Task"
        assert kwargs["replace_existing"] is True
        assert kwargs["misfire_grace_time"] == 10
    else:  # If positional arguments are used
        args = call_args.args
        assert args[0] == mock_handler  # func
        assert args[1] == mock_trigger  # trigger
        assert args[2] == "identify_satrs_job"  # id
        assert args[3] == "Identify Stars Task"  # name
        assert args[4] is True  # replace_existing
        assert args[5] == 10  # misfire_grace_time


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
