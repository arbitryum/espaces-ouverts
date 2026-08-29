"""
Geocoding service using geopy for BAN (Base Adresse Nationale) API support.

For French addresses, we use the Nominatim geocoder with a user agent and
timeouts configured appropriately for production use.
"""
import logging
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

logger = logging.getLogger(__name__)


def get_geocoder():
    """Get a Nominatim geocoder instance configured for BAN/French addresses."""
    return Nominatim(
        user_agent="espaces-ouverts/1.0",
        timeout=10,
    )


def geocode_address_with_ban(address_query):
    """
    Geocode an address using Nominatim (which supports BAN addresses in France).
    
    Args:
        address_query: The address to geocode
        
    Returns:
        A dictionary with geocoding results including coordinates, or None if not found
    """
    if not address_query or not address_query.strip():
        return None
    
    try:
        geocoder = get_geocoder()
        logger.debug(f"Geocoding address: {address_query}")
        
        location = geocoder.geocode(address_query)
        
        if not location:
            logger.warning(f"No geocoding result found for: {address_query}")
            return None
        
        logger.debug(f"Geocoding successful for {address_query}: ({location.latitude}, {location.longitude})")
        
        # Extract address components from the raw address string
        raw_address_parts = location.address.split(",")
        
        return {
            "label": location.address,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "raw_address": address_query,
        }
        
    except GeocoderTimedOut:
        logger.error(f"Geocoding timeout for: {address_query}")
        raise RuntimeError(f"Geocoding service timed out for: {address_query}")
    except GeocoderServiceError as exc:
        logger.error(f"Geocoding service error for {address_query}: {exc}")
        raise RuntimeError(f"Geocoding service error: {exc}")
    except Exception as exc:
        logger.error(f"Unexpected geocoding error for {address_query}: {exc}")
        raise RuntimeError(f"Unexpected geocoding error: {exc}")


def resolve_location_query_with_ban(location_query, *, limit=10):
    """
    Search for locations matching a query (autocomplete style).
    
    Args:
        location_query: The search query
        limit: Maximum number of results
        
    Returns:
        A dictionary with search terms, or None if not found
    """
    if not location_query or not location_query.strip():
        return None
    
    try:
        geocoder = get_geocoder()
        logger.debug(f"Searching locations for: {location_query}")
        
        locations = geocoder.geocode(location_query, exactly_one=False, timeout=10)
        
        if not locations:
            logger.warning(f"No locations found for: {location_query}")
            return None
        
        # Limit results
        locations = locations[:limit]
        
        terms = set()
        for location in locations:
            if location.address:
                terms.add(location.address)
                # Add city/postal components
                parts = location.address.split(",")
                for part in parts:
                    part = part.strip()
                    if part:
                        terms.add(part)
        
        return {"terms": sorted(list(terms))}
        
    except (GeocoderTimedOut, GeocoderServiceError) as exc:
        logger.error(f"Geocoding service error for {location_query}: {exc}")
        raise RuntimeError(f"Geocoding service error: {exc}")
    except Exception as exc:
        logger.error(f"Unexpected geocoding error for {location_query}: {exc}")
        raise RuntimeError(f"Unexpected geocoding error: {exc}")


def search_locations_with_ban(location_query, *, limit=6):
    """
    Search for locations with structured results.
    
    Args:
        location_query: The search query
        limit: Maximum number of results
        
    Returns:
        A list of location suggestions with coordinates
    """
    if not location_query or not location_query.strip():
        return []
    
    try:
        geocoder = get_geocoder()
        logger.debug(f"Searching locations for: {location_query}")
        
        locations = geocoder.geocode(location_query, exactly_one=False, timeout=10)
        
        if not locations:
            logger.warning(f"No locations found for: {location_query}")
            return []
        
        # Limit results
        locations = locations[:limit]
        
        suggestions = []
        for location in locations:
            suggestions.append({
                "label": location.address,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "name": location.address.split(",")[0] if location.address else "",
            })
        
        return suggestions
        
    except (GeocoderTimedOut, GeocoderServiceError) as exc:
        logger.error(f"Geocoding service error for {location_query}: {exc}")
        return []
    except Exception as exc:
        logger.error(f"Unexpected geocoding error for {location_query}: {exc}")
        return []
