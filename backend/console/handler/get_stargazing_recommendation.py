import json
import logging
import math
import httpx
from collections import Counter
from datetime import datetime, date, timedelta
from typing import Optional

from fastapi import HTTPException

from openapi_server.models.api_get_stargazing_recommendation_post_request import ApiGetStargazingRecommendationPostRequest
from openapi_server.models.stargazing_recommendation import StargazingRecommendation
from openapi_server.models.stargazing_recommendation_best_time_slots_inner import StargazingRecommendationBestTimeSlotsInner
from openapi_server.models.stargazing_recommendation_recommended_constellations_inner import StargazingRecommendationRecommendedConstellationsInner
from openapi_server.models.stargazing_recommendation_moon_phase import StargazingRecommendationMoonPhase

from backend.console.dal.rds.client import get_db
from backend.console.dal.rds.identify_stars_job import IdentifyStarsJob
from backend.console.dal.rds.user import User
from backend.console.utils.auth import verify_user_id_and_token
from backend.constant.star_identify import STAR_IDENTIFY_JOB_STATUS_SUCCEEDED
from backend.console.handler.request_stargazing_time import (
    OPEN_METEO_URL,
    CACHE_TTL_SECONDS,
    _get_cache_key,
    _get_redis,
    _calculate_moon_illumination,
    _score_hour,
    _is_night_hour,
    _get_sky_condition,
)

logger = logging.getLogger(__name__)

# Top N time slots to return
TOP_SLOTS = 3

# Common proper star names → constellation (case-insensitive lookup)
PROPER_STAR_NAMES: dict[str, str] = {
    "sirius": "Canis Major", "rigel": "Orion", "vega": "Lyra",
    "betelgeuse": "Orion", "polaris": "Ursa Minor", "aldebaran": "Taurus",
    "antares": "Scorpius", "arcturus": "Boötes", "spica": "Virgo",
    "altair": "Aquila", "deneb": "Cygnus", "regulus": "Leo",
    "castor": "Gemini", "pollux": "Gemini", "capella": "Auriga",
    "canopus": "Carina", "procyon": "Canis Minor", "achernar": "Eridanus",
    "fomalhaut": "Piscis Austrinus", "bellatrix": "Orion", "alnilam": "Orion",
    "alnitak": "Orion", "mintaka": "Orion", "algol": "Perseus",
    "mira": "Cetus", "hadar": "Centaurus", "acrux": "Crux",
    "gacrux": "Crux", "mimosa": "Crux", "alioth": "Ursa Major",
    "dubhe": "Ursa Major", "merak": "Ursa Major", "phecda": "Ursa Major",
    "alkaid": "Ursa Major", "mizar": "Ursa Major", "alcor": "Ursa Major",
    "kochab": "Ursa Minor", "alphard": "Hydra", "alpheratz": "Andromeda",
    "mirach": "Andromeda", "almach": "Andromeda",
}

# IAU 3-letter abbreviation → full constellation name
IAU_ABBR_TO_CONSTELLATION = {
    "And": "Andromeda", "Aql": "Aquila", "Aqr": "Aquarius", "Ari": "Aries",
    "Aur": "Auriga", "Boo": "Boötes", "Cnc": "Cancer", "CMa": "Canis Major",
    "CMi": "Canis Minor", "Cap": "Capricornus", "Car": "Carina", "Cas": "Cassiopeia",
    "Cen": "Centaurus", "Cep": "Cepheus", "Cet": "Cetus", "Com": "Coma Berenices",
    "CrB": "Corona Borealis", "Crv": "Corvus", "Cru": "Crux", "Cyg": "Cygnus",
    "Del": "Delphinus", "Dra": "Draco", "Eri": "Eridanus", "Gem": "Gemini",
    "Her": "Hercules", "Hya": "Hydra", "Leo": "Leo", "LMi": "Leo Minor",
    "Lep": "Lepus", "Lib": "Libra", "Lup": "Lupus", "Lyr": "Lyra",
    "Mon": "Monoceros", "Oph": "Ophiuchus", "Ori": "Orion", "Pav": "Pavo",
    "Peg": "Pegasus", "Per": "Perseus", "Phe": "Phoenix", "Psc": "Pisces",
    "PsA": "Piscis Austrinus", "Pup": "Puppis", "Sge": "Sagitta",
    "Sgr": "Sagittarius", "Sco": "Scorpius", "Ser": "Serpens", "Sex": "Sextans",
    "Tau": "Taurus", "Tri": "Triangulum", "UMa": "Ursa Major", "UMi": "Ursa Minor",
    "Vel": "Vela", "Vir": "Virgo", "Vul": "Vulpecula",
}

# Seasonal visible constellations per month (Northern Hemisphere)
# Each entry: (constellation_name, highlight_reason)
SEASONAL_CONSTELLATIONS: dict[int, list[tuple[str, str]]] = {
    1:  [("Orion", "winter showpiece, Betelgeuse and Rigel"), ("Taurus", "Pleiades and Hyades clusters"), ("Gemini", "Castor & Pollux"), ("Auriga", "Capella near zenith"), ("Canis Major", "Sirius, brightest star in the sky")],
    2:  [("Orion", "best month for Orion"), ("Gemini", "high overhead"), ("Leo", "rising in the east"), ("Cancer", "Beehive Cluster M44")],
    3:  [("Leo", "the Lion rising"), ("Virgo", "Spica visible"), ("Cancer", "Beehive Cluster"), ("Hydra", "largest constellation")],
    4:  [("Leo", "high overhead"), ("Virgo", "Spica bright"), ("Boötes", "Arcturus, brightest spring star"), ("Coma Berenices", "rich galaxy field")],
    5:  [("Virgo", "Spica at its best"), ("Boötes", "Arcturus high overhead"), ("Ursa Major", "Big Dipper overhead"), ("Coma Berenices", "Virgo galaxy cluster nearby")],
    6:  [("Boötes", "Arcturus near zenith"), ("Scorpius", "rising in the south"), ("Hercules", "Great Globular Cluster M13"), ("Corona Borealis", "Northern Crown")],
    7:  [("Scorpius", "summer scorpion, bright Antares"), ("Sagittarius", "Milky Way core, many nebulae"), ("Lyra", "Vega in Summer Triangle"), ("Cygnus", "Deneb in Summer Triangle")],
    8:  [("Sagittarius", "Milky Way core glowing"), ("Aquila", "Altair in Summer Triangle"), ("Cygnus", "Summer Triangle high"), ("Scorpius", "scorpion tail setting")],
    9:  [("Cygnus", "Summer Triangle overhead"), ("Pegasus", "Great Square rising"), ("Aquarius", "autumn constellation"), ("Capricornus", "sea goat")],
    10: [("Pegasus", "Great Square high"), ("Andromeda", "Andromeda Galaxy M31 well-placed"), ("Perseus", "Double Cluster"), ("Pisces", "autumn sky")],
    11: [("Andromeda", "Andromeda Galaxy M31 best view"), ("Perseus", "Double Cluster, Algol"), ("Aries", "first zodiac constellation"), ("Taurus", "Pleiades rising")],
    12: [("Orion", "winter king rises in the east"), ("Taurus", "Pleiades overhead"), ("Perseus", "Double Cluster"), ("Auriga", "pentagon of stars")],
}


def _extract_constellations_from_result(result_data: dict) -> list[str]:
    """
    Parse a job result JSON and extract constellation names from star names.

    Strategy (in order):
    1. Check the full name against known proper star names (case-insensitive).
    2. Scan every 3-character window in the name against IAU abbreviations.
       This handles Bayer names (alphOri → Ori), Flamsteed (108Vir → Vir),
       and composite names (alphaCMa → CMa).
    """
    constellations = set()
    for star in result_data.get("stars", []):
        for name in star.get("names", []):
            # 1. Proper name match
            if name.lower() in PROPER_STAR_NAMES:
                constellations.add(PROPER_STAR_NAMES[name.lower()])
                continue
            # 2. Sliding 3-char window — finds IAU suffix wherever it appears
            for i in range(len(name) - 2):
                window = name[i:i + 3]
                if window in IAU_ABBR_TO_CONSTELLATION:
                    constellations.add(IAU_ABBR_TO_CONSTELLATION[window])
                    break
    return list(constellations)


def _get_moon_info(target_date: date) -> StargazingRecommendationMoonPhase:
    """Return moon illumination and phase name for the given date."""
    known_new_moon = datetime(2000, 1, 6, 18, 14)
    lunar_cycle_days = 29.53058867

    dt = datetime(target_date.year, target_date.month, target_date.day)
    days_since = (dt - known_new_moon).total_seconds() / 86400
    cycle_pos = (days_since % lunar_cycle_days) / lunar_cycle_days
    illumination = round((1 - math.cos(2 * math.pi * cycle_pos)) / 2, 3)

    if cycle_pos < 0.03 or cycle_pos > 0.97:
        phase = "New Moon"
    elif cycle_pos < 0.22:
        phase = "Waxing Crescent"
    elif cycle_pos < 0.28:
        phase = "First Quarter"
    elif cycle_pos < 0.47:
        phase = "Waxing Gibbous"
    elif cycle_pos < 0.53:
        phase = "Full Moon"
    elif cycle_pos < 0.72:
        phase = "Waning Gibbous"
    elif cycle_pos < 0.78:
        phase = "Last Quarter"
    else:
        phase = "Waning Crescent"

    return StargazingRecommendationMoonPhase(illumination=illumination, phase=phase)


async def _fetch_top_slots(
    lat: float, lon: float, target_date: date, moon_illumination: float
) -> list[StargazingRecommendationBestTimeSlotsInner]:
    """
    Fetch weather from Open-Meteo (with Redis cache) and return the top N
    non-overlapping 2-hour stargazing windows, sorted by score descending.
    """
    cache_key = _get_cache_key(lat, lon, target_date)
    redis = _get_redis()
    raw_hourly = None

    # Try hourly cache (separate key to store raw data)
    hourly_cache_key = cache_key + ":hourly"
    if redis:
        try:
            cached = redis.get(hourly_cache_key)
            if cached:
                raw_hourly = json.loads(cached)
        except Exception as e:
            logger.warning(f"Redis read failed: {e}")

    if raw_hourly is None:
        end_date = target_date + timedelta(days=1)
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "cloud_cover,precipitation_probability",
            "timezone": "auto",
            "start_date": target_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(OPEN_METEO_URL, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Failed to fetch weather data from Open-Meteo")
        hourly = response.json().get("hourly", {})
        raw_hourly = {
            "time": hourly.get("time", []),
            "cloud_cover": hourly.get("cloud_cover", []),
            "precipitation_probability": hourly.get("precipitation_probability", []),
        }
        if redis:
            try:
                redis.set(hourly_cache_key, json.dumps(raw_hourly), ex=CACHE_TTL_SECONDS)
            except Exception as e:
                logger.warning(f"Redis write failed: {e}")

    times = raw_hourly["time"]
    cloud_covers = raw_hourly["cloud_cover"]
    precip_probs = raw_hourly["precipitation_probability"]

    # Build an index: datetime → (cloud, precip) for fast lookup
    hour_data: dict[datetime, tuple[float, float]] = {}
    for i, t in enumerate(times):
        dt = datetime.fromisoformat(t)
        cloud = cloud_covers[i] if i < len(cloud_covers) else 100.0
        precip = precip_probs[i] if i < len(precip_probs) else 100.0
        hour_data[dt] = (cloud, precip)

    # Score every 2-hour nighttime window by the AVERAGE of both hours
    # Only consider windows where the START hour is a valid night hour
    two_hour_windows: list[tuple[datetime, float]] = []
    for dt, (cloud0, precip0) in hour_data.items():
        if not _is_night_hour(dt.hour):
            continue
        dt1 = dt + timedelta(hours=1)
        cloud1, precip1 = hour_data.get(dt1, (100.0, 100.0))
        avg_cloud = (cloud0 + cloud1) / 2
        avg_precip = (precip0 + precip1) / 2
        avg_score = _score_hour(avg_cloud, avg_precip, moon_illumination)
        two_hour_windows.append((dt, avg_score))

    if not two_hour_windows:
        return []

    # Greedy pick: top N non-overlapping windows by avg score
    sorted_windows = sorted(two_hour_windows, key=lambda x: x[1], reverse=True)
    selected: list[StargazingRecommendationBestTimeSlotsInner] = []
    used_hours: set[datetime] = set()

    for dt, avg_score in sorted_windows:
        if len(selected) >= TOP_SLOTS:
            break
        window_hours = {dt, dt + timedelta(hours=1)}
        if window_hours & used_hours:
            continue
        used_hours.update(window_hours)
        cloud0, _ = hour_data.get(dt, (100.0, 100.0))
        cloud1, _ = hour_data.get(dt + timedelta(hours=1), (100.0, 100.0))
        avg_cloud = (cloud0 + cloud1) / 2
        selected.append(
            StargazingRecommendationBestTimeSlotsInner(
                start_time=dt,
                end_time=dt + timedelta(hours=2),
                score=round(avg_score, 1),
                sky_condition=_get_sky_condition(avg_cloud),
            )
        )

    return sorted(selected, key=lambda s: s.start_time)


def _build_constellation_recommendations(
    user_constellation_counter: Counter,
    target_date: date,
) -> list[StargazingRecommendationRecommendedConstellationsInner]:
    """
    Merge user history preferences with seasonal recommendations.
    User-observed constellations get priority; seasonal fill the rest.
    """
    results: list[StargazingRecommendationRecommendedConstellationsInner] = []
    seen: set[str] = set()

    # 1. User's top personally observed constellations
    for name, count in user_constellation_counter.most_common(3):
        results.append(StargazingRecommendationRecommendedConstellationsInner(
            name=name,
            reason=f"You've observed this {count} time{'s' if count > 1 else ''} before",
        ))
        seen.add(name)

    # 2. Fill with seasonal constellations (skip already added)
    month = target_date.month
    for name, reason in SEASONAL_CONSTELLATIONS.get(month, []):
        if name not in seen:
            results.append(StargazingRecommendationRecommendedConstellationsInner(
                name=name,
                reason=f"Seasonal highlight: {reason}",
            ))
            seen.add(name)
        if len(results) >= 5:
            break

    return results


def _generate_tips(
    moon_phase: StargazingRecommendationMoonPhase,
    best_slots: list[StargazingRecommendationBestTimeSlotsInner],
    preferred_hours: Counter,
    target_date: date,
) -> list[str]:
    """Generate personalized observation tips based on conditions and user history."""
    tips: list[str] = []

    # Moon phase tip
    if moon_phase.illumination < 0.1:
        tips.append("New Moon tonight — ideal darkness for deep-sky objects and the Milky Way.")
    elif moon_phase.illumination < 0.35:
        tips.append(f"{moon_phase.phase}: low moon interference, good conditions for faint objects.")
    elif moon_phase.illumination > 0.85:
        tips.append(f"Full Moon approaching ({int(moon_phase.illumination * 100)}% illuminated) — best for lunar observation; avoid faint nebulae.")
    else:
        tips.append(f"{moon_phase.phase} ({int(moon_phase.illumination * 100)}% illuminated) — moon sets early, leaving dark skies after midnight.")

    # Sky condition tip — use the highest-scored slot (not the earliest in time)
    if best_slots:
        top = max(best_slots, key=lambda s: s.score or 0)
        if top.sky_condition == "clear":
            tips.append(f"Clear skies expected — prime conditions around {top.start_time.strftime('%H:%M')}.")
        elif top.sky_condition == "partly-cloudy":
            tips.append(f"Partly cloudy around {top.start_time.strftime('%H:%M')}, but still worth trying between gaps.")
        else:
            tips.append("Heavy cloud cover forecast — consider checking again tomorrow.")

    # User habit tip
    if preferred_hours:
        top_hour, count = preferred_hours.most_common(1)[0]
        tips.append(f"You usually observe around {top_hour:02d}:00 — keep the habit tonight!")

    # Seasonal tip
    month_names = ["", "January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    seasonal = SEASONAL_CONSTELLATIONS.get(target_date.month, [])
    if seasonal:
        top_name, top_reason = seasonal[0]
        tips.append(f"{month_names[target_date.month]} highlight: {top_name} — {top_reason}.")

    return tips


async def api_get_stargazing_recommendation_post(
    req: ApiGetStargazingRecommendationPostRequest,
) -> StargazingRecommendation:
    if req is None or req.gps is None:
        raise HTTPException(status_code=400, detail="GPS location is required")
    if req.user_credentials is None:
        raise HTTPException(status_code=400, detail="User credentials are required")

    verify_user_id_and_token(req.user_credentials.token, req.user_credentials.user_id)

    user_id = int(req.user_credentials.user_id)
    lat = req.gps.latitude
    lon = req.gps.longitude
    target_date: date = req.target_date or date.today()

    db_session = next(get_db())
    try:
        constellation_counter: Counter = Counter()
        hour_counter: Counter = Counter()

        # Prefer pre-computed profile written by the cronjob (fast path)
        user = User.get_by_id(db_session, user_id)
        profile_loaded = False
        if user and user.profile and "stargazing_profile" in user.profile:
            sg = user.profile["stargazing_profile"]
            for i, name in enumerate(sg.get("preferred_constellations", [])):
                # Weight by position: most-observed gets highest count
                constellation_counter[name] = max(5 - i, 1)
            for h in sg.get("preferred_hours", []):
                hour_counter[h] = 10
            profile_loaded = True
            logger.debug(f"Loaded stargazing profile from cache for user {user_id}")

        if not profile_loaded:
            # Fallback: scan recent SUCCEEDED jobs directly
            jobs = IdentifyStarsJob.list_by_user_id(db_session, user_id, limit=100)
            for job in jobs:
                if job.status != STAR_IDENTIFY_JOB_STATUS_SUCCEEDED:
                    continue
                if job.created_at:
                    hour_counter[job.created_at.hour] += 1
                if job.result:
                    try:
                        data = json.loads(job.result) if isinstance(job.result, str) else job.result
                        for constellation in _extract_constellations_from_result(data):
                            constellation_counter[constellation] += 1
                    except Exception as e:
                        logger.warning(f"Failed to parse job result for job {job.id}: {e}")

        moon_phase = _get_moon_info(target_date)
        best_slots = await _fetch_top_slots(lat, lon, target_date, moon_phase.illumination)
        recommended_constellations = _build_constellation_recommendations(
            constellation_counter, target_date
        )
        tips = _generate_tips(moon_phase, best_slots, hour_counter, target_date)

        return StargazingRecommendation(
            best_time_slots=best_slots,
            recommended_constellations=recommended_constellations,
            moon_phase=moon_phase,
            tips=tips,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error generating stargazing recommendation", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    finally:
        db_session.close()
