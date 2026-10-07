"""Route and nearby-place plan. No live map vendor is called."""

PLACES = {
    'mumbai': (19.076, 72.877),
    'london': (51.507, -0.128),
    'pune': (18.520, 73.856),
}


def route_plan(origin: str, destination: str) -> dict:
    start = PLACES.get(origin.strip().lower())
    end = PLACES.get(destination.strip().lower())
    if not start or not end:
        return {'known': False, 'origin': origin, 'destination': destination, 'points': []}
    return {
        'known': True,
        'origin': origin,
        'destination': destination,
        'points': [start, end],
        'nearby': ['hospital', 'fuel', 'atm'],
    }
