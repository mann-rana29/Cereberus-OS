import asyncio
import random
from services.telemetry_service import ingest_sensor_log
from models.telemetry import SensorLogCreate, GasType

ZONES = ["battery_4", "battery_3", "pump_station_p3a"]

async def run_stream_consumer():
    while True:
        zone = random.choice(ZONES)
        gas = random.choice(["CO", "H2S", "SO2"])
        ppm = round(random.uniform(0.5, 5.0), 2)

        log = SensorLogCreate(
            zone_id=zone,
            gas_type=GasType(gas),
            gas_ppm=ppm
        )

        try:
            ingest_sensor_log(log)
        except Exception as e:
            print(f"[stream_consumer] Error ingesting log: {e}")

        await asyncio.sleep(5)