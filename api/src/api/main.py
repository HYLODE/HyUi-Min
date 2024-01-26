# type: ignore
"""
Entry point and main file for the FastAPI backend
"""
import time

import arrow
from fastapi import APIRouter, FastAPI
from fastapi.responses import ORJSONResponse

from api.beds.router import mock_router as mock_beds_router
from api.beds.router import router as beds_router
from api.census.router import mock_router as mock_census_router
from api.census.router import router as census_router
from api.consults.router import router as consults_router
from api.demo.router import mock_router as mock_demo_router
from api.demo.router import router as demo_router
from api.electives.router import mock_router as mock_electives_router
from api.electives.router import router as electives_router
from api.hospital.router import mock_router as mock_hospital_router
from api.hospital.router import router as hospital_router
from api.logger import logger
from api.ros.router import router as ros_router
from api.sitrep.router import mock_router as mock_sitrep_router
from api.sitrep.router import router as sitrep_router


logger.info("API app starting")

app = FastAPI(
    default_response_class=ORJSONResponse,
)

mock_router = APIRouter(
    prefix="/mock",
)

app.include_router(demo_router)
mock_router.include_router(mock_demo_router)

app.include_router(hospital_router)
mock_router.include_router(mock_hospital_router)

app.include_router(census_router)
mock_router.include_router(mock_census_router)

app.include_router(sitrep_router)
mock_router.include_router(mock_sitrep_router)

app.include_router(electives_router)
mock_router.include_router(mock_electives_router)

app.include_router(beds_router)
mock_router.include_router(mock_beds_router)

app.include_router(consults_router)

app.include_router(ros_router)

# Finally include the mock router.
app.include_router(mock_router)


@app.get("/ping")
def ping() -> dict[str, str]:
    return {"ping": "pong"}


@app.get("/ping/slow")
def pong_slow() -> dict[str, str]:
    notnow = arrow.utcnow().format("YYYY-MM-DD HH:mm:ss.SSS")
    time.sleep(5)
    return notnow


@app.get("/ping/fast")
def pong_fast() -> dict[str, str]:
    now = arrow.utcnow().format("YYYY-MM-DD HH:mm:ss.SSS")
    return now
