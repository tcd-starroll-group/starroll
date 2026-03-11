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

    # Mock job handlers and trigger constructors used by _register_jobs.
    mock_identify_handler = MagicMock()
    mock_precompute_handler = MagicMock()
    mock_profile_handler = MagicMock()
    mock_email_handler = MagicMock()

    identify_trigger = MagicMock(name="identify_trigger")
    precompute_trigger = MagicMock(name="precompute_trigger")
    profile_trigger = MagicMock(name="profile_trigger")
    email_trigger = MagicMock(name="email_trigger")

    def _interval_trigger_stub(*args, **kwargs):
        if kwargs.get("seconds") == 5:
            return identify_trigger
        if kwargs.get("hours") == 3:
            return precompute_trigger
        if kwargs.get("hours") == 6:
            return profile_trigger
        raise AssertionError(f"Unexpected IntervalTrigger args: {args}, {kwargs}")

    def _cron_trigger_stub(*args, **kwargs):
        if kwargs.get("hour") == 18 and kwargs.get("minute") == 0:
            return email_trigger
        raise AssertionError(f"Unexpected CronTrigger args: {args}, {kwargs}")

    monkeypatch.setattr("backend.cronjob.main.identify_stars_handler", mock_identify_handler)
    monkeypatch.setattr("backend.cronjob.main.precompute_stargazing_handler", mock_precompute_handler)
    monkeypatch.setattr("backend.cronjob.main.update_user_stargazing_profile_handler", mock_profile_handler)
    monkeypatch.setattr("backend.cronjob.main.send_stargazing_recommendation_email_handler", mock_email_handler)
    monkeypatch.setattr("backend.cronjob.main.IntervalTrigger", _interval_trigger_stub)
    monkeypatch.setattr("backend.cronjob.main.CronTrigger", _cron_trigger_stub)

    scheduler._register_jobs()

    # Four jobs should be registered: identify, precompute, profile update, email.
    assert mock_add_job.call_count == 4

    calls = mock_add_job.call_args_list

    identify_call = calls[0]
    assert identify_call.args[0] == mock_identify_handler
    assert identify_call.kwargs["trigger"] == identify_trigger
    assert identify_call.kwargs["id"] == "identify_satrs_job"
    assert identify_call.kwargs["name"] == "Identify Stars Task"
    assert identify_call.kwargs["replace_existing"] is True
    assert identify_call.kwargs["misfire_grace_time"] == 10

    precompute_call = calls[1]
    assert precompute_call.args[0] == mock_precompute_handler
    assert precompute_call.kwargs["trigger"] == precompute_trigger
    assert precompute_call.kwargs["id"] == "precompute_stargazing_job"
    assert precompute_call.kwargs["name"] == "Precompute Stargazing Recommendations"

    profile_call = calls[2]
    assert profile_call.args[0] == mock_profile_handler
    assert profile_call.kwargs["trigger"] == profile_trigger
    assert profile_call.kwargs["id"] == "update_user_stargazing_profile_job"
    assert profile_call.kwargs["name"] == "Update User Stargazing Profiles"

    email_call = calls[3]
    assert email_call.args[0] == mock_email_handler
    assert email_call.kwargs["trigger"] == email_trigger
    assert email_call.kwargs["id"] == "send_stargazing_recommendation_email_job"
    assert email_call.kwargs["name"] == "Send Daily Stargazing Recommendation Emails"


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
