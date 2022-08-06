# src/mock/mock.py
"""
Generates sqlite database with a table holding modelled as per
api.models.Results and then loads the data from the local HDF file
"""

import importlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import sqlalchemy as sa
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from config.settings import settings  # type: ignore
from utils import gen_module_path, get_model_from_route  # type: ignore

# you can use this function in testing but swap in an in memory version
SYNTH_SQLITE_FILE = Path(__file__).parent / "mock.db"
SYNTH_SQLITE_URL = f"sqlite:///{SYNTH_SQLITE_FILE}"
SYNTH_SQLITE_MEM = "sqlite://"
ECHO = False


def path_to_file(route: str, extension: str):
    """Prep path to file based on route"""
    assert extension in ["h5", "db"]
    file = f"mock.{extension}"
    return Path(__file__).parents[1] / "api" / route / file


def make_engine(path=SYNTH_SQLITE_URL, **kwargs):
    engine = create_engine(path, **kwargs)
    return engine


def make_mock_df(f: Path) -> pd.DataFrame:
    """
    Makes a dataframe from the HDF file generated by the code in ./synth
    """
    try:
        assert f.is_file()
    except AssertionError as e:
        print(e)
        print(f"!!! Synthetic data not found at {f}")
        print("!!! Follow the instructions in ./synth/readme.md to generate")
        print("!!! Then check that you've manually copied the HDF file")
        print("!!! from ./synth/portal/ to ./src/mock/")
        raise AssertionError(e)

    df = pd.read_hdf(f)
    return df  # type: ignore


def create_mock_table(engine, model: SQLModel, drop=False):
    # metadata is defined when you run the import statement above
    table = model.__table__  # type: ignore
    if drop:
        SQLModel.metadata.drop_all(engine, tables=[table])
    # force it fail if drop not issued
    try:
        SQLModel.metadata.create_all(engine, tables=[table], checkfirst=False)
    except sa.exc.OperationalError as e:
        print(e)
        print("==============================================================")
        print("??? Try using drop=True to force the table to be deleted first")


def df_from_file(route: str) -> pd.DataFrame:
    """
    generate a dataframe from the mock data stored in the API


    :param      route:  the final part of the path to the data
    :type       route:  str

    :returns:   dataframe with mock data
    :rtype:     pandas dataframe
    """
    if path_to_file(route, "h5").is_file():
        file = path_to_file(route, "h5")
        df = make_mock_df(file)
    elif path_to_file(route, "db").is_file():
        _file = path_to_file(route, "db").as_posix()
        _URL = f"sqlite:///{_file}"
        engine_in = create_engine(_URL)
        with engine_in.connect() as conn:
            df = pd.read_sql(route, conn)
    else:
        raise Exception
    return df


def insert_into_mock_table(engine, df: pd.DataFrame, model: SQLModel):
    df = df.replace(
        {np.NaN: None}
    )  # replace NaN / NaT with Nones as otherwise errors are thrown.

    rows = df.to_dict(orient="records")
    with Session(engine) as session:
        for row in rows:
            session.add(model(**row))  # type: ignore
        session.commit()
    return 0


def make_mock_db_in_memory(route: str):
    """
    Use SQLModel to create a temporary db in memory for testing etc
    Convenience function that wraps others
    Uses route to define the HDF data file and the SQL model
    """
    engine = make_engine(
        path=SYNTH_SQLITE_MEM,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    model = get_model_from_route(route, "Mock")
    df = df_from_file(route)
    create_mock_table(engine, model, drop=True)
    insert_into_mock_table(engine, df, model)
    return engine


if __name__ == "__main__":
    engine = make_engine(echo=True)

    # load mock hymind icu discharges
    model_path = f"{gen_module_path('hymind')}.model"
    model = getattr(importlib.import_module(model_path), "IcuDischarge")
    _ = pd.read_json("../src/api/hymind/data/mock_icu_discharge.json")
    df = pd.DataFrame.from_records(_['data'])
    create_mock_table(engine, model, drop=True)
    insert_into_mock_table(engine, df, model)

    for route in settings.ROUTES:
        try:
            model = get_model_from_route(route, "Mock")
            df = df_from_file(route)
            create_mock_table(engine, model, drop=True)
            insert_into_mock_table(engine, df, model)
        except Exception as e:
            print(e)
            sys.exit(1)
