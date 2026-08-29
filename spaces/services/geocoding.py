import json
import time
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings

BAN_SEARCH_URL = "https://api-adresse.data.gouv.fr/search/"


def _extract_department_info(context):
    parts = [part.strip() for part in context.split(",") if part.strip()]
    if len(parts) < 2:
        return "", "", ""
    if len(parts) < 3:
        return parts[0], parts[1], ""
    return parts[0], parts[1], parts[2]


def _ban_search(query_text, *, limit, autocomplete, timeout_seconds, max_retries=3):
    query = urlencode(
        {
            "q": query_text,
            "limit": limit,
            "autocomplete": autocomplete,
        }
    )
    ban_search_url = getattr(settings, "BAN_API_SEARCH_URL", BAN_SEARCH_URL)
    request_timeout = getattr(settings, "BAN_API_TIMEOUT_SECONDS", timeout_seconds)
    
    last_error = None
    last_error_detail = None
    
    for attempt in range(max_retries):
        try:
            request = Request(
                f"{ban_search_url}?{query}",
                headers={"User-Agent": "espaces-ouverts/1.0"},
            )
            with urlopen(request, timeout=request_timeout) as response:
                if response.status != 200:
                    error_detail = f"HTTP {response.status}"
                    raise RuntimeError(error_detail)
                payload = json.loads(response.read().decode("utf-8"))
                return payload
        except URLError as exc:
            last_error = exc
            last_error_detail = str(exc.reason) if hasattr(exc, 'reason') else str(exc)
            if attempt < max_retries - 1:
                time.sleep(1 * (attempt + 1))  # Exponential backoff
                continue
            raise RuntimeError(
                f"BAN API request failed (attempt {attempt + 1}/{max_retries}): {last_error_detail}"
            ) from exc
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"BAN API response could not be decoded: {str(exc)}"
            ) from exc
        except RuntimeError as exc:
            last_error = exc
            last_error_detail = str(exc)
            if attempt < max_retries - 1:
                time.sleep(1 * (attempt + 1))
                continue
            raise RuntimeError(
                f"BAN API request failed (attempt {attempt + 1}/{max_retries}): {last_error_detail}"
            ) from exc
    
    raise RuntimeError(
        f"BAN API request failed after {max_retries} attempts: {last_error_detail}"
    ) from last_error


def geocode_address_with_ban(address_query, *, timeout_seconds=5):
    normalized_query = " ".join(address_query.split())
    if not normalized_query:
        return None

    payload = _ban_search(
        normalized_query,
        limit=1,
        autocomplete=0,
        timeout_seconds=timeout_seconds,
    )

    features = payload.get("features") or []
    if not features:
        return None

    first_feature = features[0]
    properties = first_feature.get("properties") or {}
    geometry = first_feature.get("geometry") or {}
    coordinates = geometry.get("coordinates") or [None, None]
    longitude, latitude = coordinates[0], coordinates[1]

    department_code, department_name, region_name = _extract_department_info(
        properties.get("context", "")
    )

    return {
        "label": properties.get("label", ""),
        "city": properties.get("city", ""),
        "postal_code": properties.get("postcode", ""),
        "city_code": properties.get("citycode", ""),
        "department_code": department_code,
        "department_name": department_name,
        "region_name": region_name,
        "latitude": latitude,
        "longitude": longitude,
        "ban_id": properties.get("id", ""),
        "ban_score": properties.get("score"),
    }


def resolve_location_query_with_ban(location_query, *, timeout_seconds=5, limit=10):
    normalized_query = " ".join(location_query.split())
    if not normalized_query:
        return None

    payload = _ban_search(
        normalized_query,
        limit=limit,
        autocomplete=1,
        timeout_seconds=timeout_seconds,
    )
    features = payload.get("features") or []
    if not features:
        return None

    terms = set()
    for feature in features:
        properties = feature.get("properties") or {}
        department_code, department_name, region_name = _extract_department_info(
            properties.get("context", "")
        )
        for term in (
            properties.get("label", ""),
            properties.get("name", ""),
            properties.get("city", ""),
            properties.get("postcode", ""),
            properties.get("citycode", ""),
            department_code,
            department_name,
            region_name,
        ):
            if term:
                terms.add(term)

    return {"terms": sorted(terms)}


def search_locations_with_ban(location_query, *, timeout_seconds=5, limit=6):
    normalized_query = " ".join(location_query.split())
    if not normalized_query:
        return []

    payload = _ban_search(
        normalized_query,
        limit=limit,
        autocomplete=1,
        timeout_seconds=timeout_seconds,
    )
    features = payload.get("features") or []
    suggestions = []
    for feature in features:
        properties = feature.get("properties") or {}
        geometry = feature.get("geometry") or {}
        coordinates = geometry.get("coordinates") or [None, None]
        longitude, latitude = coordinates[0], coordinates[1]
        department_code, department_name, region_name = _extract_department_info(
            properties.get("context", "")
        )
        suggestions.append(
            {
                "label": properties.get("label", ""),
                "name": properties.get("name", ""),
                "city": properties.get("city", ""),
                "postcode": properties.get("postcode", ""),
                "type": properties.get("type", ""),
                "department_code": department_code,
                "department_name": department_name,
                "region_name": region_name,
                "latitude": latitude,
                "longitude": longitude,
                "score": properties.get("score", 0),
            }
        )

    type_priority = {
        "municipality": 0,
        "city": 0,
        "locality": 1,
        "postcode": 2,
        "street": 3,
        "housenumber": 4,
    }
    suggestions.sort(
        key=lambda item: (
            type_priority.get(item.get("type", ""), 9),
            -float(item.get("score") or 0),
        )
    )

    for suggestion in suggestions:
        suggestion.pop("score", None)

    return suggestions
