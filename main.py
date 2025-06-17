from fastapi import FastAPI, Query
from pydantic import BaseModel
from math import radians, sin, cos, sqrt, atan2
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum  # for Vercel handler

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Haversine Formula ----------
def calculate_distance_km(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# ---------- Request Schema ----------
class LocationData(BaseModel):
    user_lat: float
    user_lng: float
    store_lat: float
    store_lng: float

# ---------- Delivery Price Logic ----------
def calculate_delivery_charge(distance_km: float) -> int:
    if distance_km <= 5:
        return 50
    elif distance_km <= 7:
        return 50 + 20
    else:
        extra_km = max(0, distance_km - 7)
        extra_charge = int(extra_km) * 10  # ₹10 per km after 7 km
        return 70 + extra_charge

# ---------- POST Endpoint ----------
@app.post("/calculate-delivery")
def get_delivery_info(location: LocationData):
    print(f"Received POST request: {location}")
    distance = calculate_distance_km(
        location.user_lat, location.user_lng,
        location.store_lat, location.store_lng
    )
    delivery_price = calculate_delivery_charge(distance)
    return {
        "distance_km": round(distance, 2),
        "delivery_price": delivery_price
    }

# ---------- Optional GET Endpoint ----------
@app.get("/calculate-delivery")
def get_delivery_by_query(
    user_lat: float = Query(...),
    user_lng: float = Query(...),
    store_lat: float = Query(...),
    store_lng: float = Query(...)
):
    print(f"Received GET request: user=({user_lat}, {user_lng}), store=({store_lat}, {store_lng})")
    distance = calculate_distance_km(user_lat, user_lng, store_lat, store_lng)
    delivery_price = calculate_delivery_charge(distance)
    return {
        "distance_km": round(distance, 2),
        "delivery_price": delivery_price
    }

# ---------- Vercel Handler ----------
handler = Mangum(app)
