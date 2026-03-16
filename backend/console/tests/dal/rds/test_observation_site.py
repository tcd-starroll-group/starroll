from backend.console.dal.rds.observation_site import ObservationSite


def test_list_active_observation_sites(db_session):
    sites = ObservationSite.list_active(db_session)

    assert len(sites) >= 3
    assert all(site.is_active == 1 for site in sites)


def test_get_observation_site_by_id(db_session):
    sites = ObservationSite.list_active(db_session)

    fetched = ObservationSite.get_by_id(db_session, sites[0].id)

    assert fetched is not None
    assert fetched.id == sites[0].id
