import warnings

from typing import Any

from dash import Input, Output, callback

from web import SITREP_DEPT2WARD_MAPPING, ids as store_ids
from web.pages.sitrep import ids
from web.logger import logger, logger_timeit

logger.info("Preparing stores for sitrep")


@callback(
    Output(ids.SITREP_STORE, "data"),
    Input(ids.DEPT_SELECTOR, "value"),
    Input(store_ids.SITREP_STORE, "data"),
)
@logger_timeit(level="DEBUG")
def _store_sitrep(dept: str, sitreps: dict) -> Any:
    """
    Args:
        dept: the department
        sitreps: dictionary of sitreps

    Returns:
        additonal patient level data

    """
    logger.warning("PRINTING LOTS OF STUFF NOW!")
    print(f"Sitreps: {sitreps}")
    # ward2dept = {v:k for k,v in SITREP_DEPT2WARD_MAPPING.items()}
    # department = ward2dept.get(dept)
    ward = SITREP_DEPT2WARD_MAPPING.get(dept)
    print(f"{ward=}")
    if not ward:
        warnings.warn(f"No sitrep data available for {ward}")
        return [{}]
    print(f"{sitreps[ward]=}")
    return sitreps[ward]


@callback(Output(ids.SITREP_STORE, "data"), Input(ids.SITREP_STORE, "data"))
def output_store_sitrep(sitrep_store: dict) -> dict:
    """Debugging function"""
    return sitrep_store
