## This is mock service to impersonate the original SCADA system

import requests
import time
import random

BASE_URL = "http://localhost:8000"

ZONES = ["battery_4", "battery_3", "pump_station_p3a"]
GASES = [
    {"gas_type": "CO", "gas_ppm": 2.4},
    {"gas_type": "H2S", "gas_ppm": 6.4},
    {"gas_type": "CO", "gas_ppm": 0.5},
    {"gas_type": "SO2", "gas_ppm": 3.0},
]

def register_permits():
    for zone in ZONES:
        try:
            requests.post(f"{BASE_URL}/permit/", json={
                "zone_id": zone,
                "work_type": "HOT_WORK",
                "assigned_team": "Contractor Team B"
            })
            print(f"[PERMIT] Registered for {zone}")
        except Exception as e:
            print(f"[PERMIT ERROR] {e}")

def inject_loop():
    while True:
        zone = random.choice(ZONES)
        reading = random.choice(GASES)
        try:
            res = requests.post(f"{BASE_URL}/telemetry/event", json={
                "zone_id": zone,
                **reading
            })
            print(f"[TELEMETRY] {zone} - {reading} - {res.status_code}")
        except Exception as e:
            print(f"[TELEMETRY ERROR] {e}")
        time.sleep(3)

if __name__ == "__main__":
    print("=== CERBERUS OS INJECTOR ===")
    register_permits()
    time.sleep(1)
    inject_loop()