import math
from haversine import haversine
from django.conf import settings
from django.db.models import Q
from dal import autocomplete
from address.models import (
    InconsistentDictError,
    State,
    Locality,
    Country,
    Address,
)
from pygeocoder import Geocoder, GeocoderError
from users.models import User
from chapters.models import Chapter
from forms.models import DisciplinaryProcess


def xstr(s):
    return s or ""


def process_value(value):
    raw = xstr(value.get("raw", ""))
    country = xstr(value.get("country", ""))
    country_code = xstr(value.get("country_code", ""))
    state = xstr(value.get("state", ""))
    state_code = xstr(value.get("state_code", ""))
    locality = xstr(value.get("locality", ""))
    sublocality = xstr(value.get("sublocality", ""))
    postal_code = xstr(value.get("postal_code", ""))
    street_number = xstr(value.get("street_number", ""))
    route = xstr(value.get("route", ""))
    formatted = xstr(value.get("formatted", ""))
    latitude = value.get("latitude", None)
    longitude = value.get("longitude", None)

    # If there is no value (empty raw) then return None.
    if not raw:
        return None

    # Fix issue with NYC boroughs (https://code.google.com/p/gmaps-api-issues/issues/detail?id=635)
    if not locality and sublocality:
        locality = sublocality

    # If we have an inconsistent set of value bail out now.
    if (country or state or locality) and not (country and state and locality):
        raise InconsistentDictError

    # Handle the country.
    try:
        country_obj = Country.objects.get(name=country)
    except Country.DoesNotExist:
        if country:
            if len(country_code) > Country._meta.get_field("code").max_length:
                if country_code != country:
                    raise ValueError(
                        "Invalid country code (too long): %s" % country_code
                    )
                country_code = ""
            country_obj = Country.objects.create(name=country, code=country_code)
        else:
            country_obj = None

    # Handle the state.
    try:
        state_obj = State.objects.get(name=state, country=country_obj)
    except State.DoesNotExist:
        if state:
            if len(state_code) > State._meta.get_field("code").max_length:
                if state_code != state:
                    raise ValueError("Invalid state code (too long): %s" % state_code)
                state_code = ""
            state_obj = State.objects.create(
                name=state, code=state_code, country=country_obj
            )
        else:
            state_obj = None

    # Handle the locality.
    try:
        locality_obj = Locality.objects.get(
            name=locality, postal_code=postal_code, state=state_obj
        )
    except Locality.DoesNotExist:
        if locality:
            locality_obj = Locality.objects.create(
                name=locality, postal_code=postal_code, state=state_obj
            )
        else:
            locality_obj = None

    return (
        street_number,
        route,
        raw,
        locality_obj,
        formatted,
        latitude,
        longitude,
    )


def deduplicate(addresses):
    addresses_list = list(addresses)
    main_address = addresses_list[0]
    address_ids = addresses.values("id")
    # print("    Total to fix:", address_ids.count())
    update_objs = set()
    users = User.objects.filter(address__in=address_ids)
    update_objs.update(list(users))
    chapters = Chapter.objects.filter(address__in=address_ids)
    update_objs.update(list(chapters))
    disciplinary = DisciplinaryProcess.objects.filter(address__in=address_ids)
    update_objs.update(list(disciplinary))
    # print("        objs found: ", update_objs)
    for update_obj in update_objs:
        update_obj.address = main_address
    if users:
        User.objects.bulk_update(users, ["address"])
    if chapters:
        Chapter.objects.bulk_update(chapters, ["address"])
    if disciplinary:
        DisciplinaryProcess.objects.bulk_update(disciplinary, ["address"])
    for old_address in addresses_list[1:]:
        old_address.delete()


def fix_duplicate_address(value):
    (
        street_number,
        route,
        raw,
        locality_obj,
        formatted,
        latitude,
        longitude,
    ) = process_value(value)
    addresses = Address.objects.filter(
        street_number=street_number, route=route, locality=locality_obj
    )
    deduplicate(addresses)


def update_address(value, address_obj):
    """
    from address.models import _to_python
    Original function from django_address does not allow
        for updating existing address with new address data
    :param value:
    :param address_obj:
    :return:
    """
    (
        street_number,
        route,
        raw,
        locality_obj,
        formatted,
        latitude,
        longitude,
    ) = process_value(value)

    # Handle the address.
    address_obj.street_number = street_number
    address_obj.route = route
    address_obj.raw = raw
    address_obj.locality = locality_obj
    address_obj.formatted = formatted
    address_obj.latitude = latitude
    address_obj.longitude = longitude
    # If "formatted" is empty try to construct it from other values.
    if not address_obj.formatted:
        address_obj.formatted = str(address_obj)

    # Need to save.
    address_obj.save()

    # Done.
    return address_obj


def fix_address(address):
    coder = Geocoder(settings.GOOGLE_API_KEY)
    try:
        parsed = coder.geocode(address.raw)
    except GeocoderError:
        # print("    !!! Bad address")
        address.delete()
        return None
    # print("    ", address.raw, parsed.formatted_address, sep="\n    ")
    postal_code = parsed.postal_code
    if parsed.postal_code_suffix:
        postal_code = f"{postal_code}-{parsed.postal_code_suffix}"
    parsed_values = dict(
        raw=address.raw,
        country=parsed.country,
        state=parsed.state,
        locality=parsed.locality,
        sublocality=parsed.county,
        postal_code=postal_code,
        street_number=parsed.street_number,
        route=parsed.route,
        formatted=parsed.formatted_address,
        latitude=parsed.latitude,
        longitude=parsed.longitude,
    )
    try:
        address = update_address(parsed_values, address)
    except InconsistentDictError:
        # print("    !!! Bad address")
        address.delete()
        return None
    return address


def isinradius(zip, distance):
    """Takes a zip, and a distance in miles.
    Returns a list of zipcodes near the zip."""
    zips_in_radius = list()
    if not distance:
        distance = 1
    try:
        locality = Locality.objects.filter(postal_code=zip).first()
        if locality:
            address = locality.addresses.exclude(longitude=0).first()
        else:
            raise Locality.DoesNotExist
    except Locality.DoesNotExist:
        return []

    point = (address.latitude, address.longitude)

    dist_btwn_lat_deg = 69.172
    dist_btwn_lng_deg = math.cos(point[0]) * 69.172
    lat_degr_rad = float(distance) / dist_btwn_lat_deg
    lng_degr_rad = float(distance) / dist_btwn_lng_deg

    latmin = point[0] - lat_degr_rad
    latmax = point[0] + lat_degr_rad
    lngmin = point[1] - lng_degr_rad
    lngmax = point[1] + lng_degr_rad

    if latmin > latmax:
        latmin, latmax = latmax, latmin
    if lngmin > lngmax:
        lngmin, lngmax = lngmax, lngmin

    zips = Address.objects.filter(
        Q(longitude__gt=lngmin)
        & Q(longitude__lt=lngmax)
        & Q(latitude__gt=latmin)
        & Q(latitude__lt=latmax)
    ).prefetch_related("user_set")

    for z in zips:
        if haversine(point, (z.latitude, z.longitude)) <= float(distance):
            zips_in_radius.append(z)
    return zips_in_radius


class ZipCodeAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Locality.objects.none()
        if self.request.user.is_authenticated:
            if self.q:
                qs = Locality.objects.all()
                qs = qs.filter(
                    Q(name__icontains=self.q) | Q(postal_code__icontains=self.q)
                )
        return qs.order_by("postal_code")
