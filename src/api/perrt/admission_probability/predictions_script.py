import xgboost
import pickle
import pandas as pd
import os, re, sched, time
import datetime
from config.settings import settings
from sqlalchemy import create_engine
from functions import run_pipeline

def get_emapdb_engine():
    uds_user = settings.EMAP_DB_USER    
    uds_passwd = settings.EMAP_DB_PASSWORD
    uds_host = settings.EMAP_DB_HOST
    uds_name = settings.EMAP_DB_NAME
    uds_port = "5432"

    return create_engine(f"postgresql://{uds_user}:{uds_passwd}@{uds_host}:{uds_port}/{uds_name}")

def get_predictions(dataset):
    # Load the model and shap model
    model = pickle.load(open("final_model.pkl", "rb"))

    # Remove columns with 'ward' in them (these may cause model drift)
    ward_columns = [i for i in dataset.columns if re.match(".*_ward$", i)]
    ward_columns.extend(["icu_admission"])
    cols_for_use = [i for i in dataset.columns if not i in ward_columns]

    # Make our predictions
    predictions = model.predict_proba(dataset.loc[:, cols_for_use])[:, 1]

    return dict(zip(dataset.index.map(str), predictions))

def write_predictions(predictions_map):
    if not os.path.exists("generated_data"):
        os.makedirs("generated_data")

    with open("generated_data/id_to_admission_prediction.pkl", "wb") as f:
        print("Pickling predictions map")
        pickle.dump(predictions_map, f)

def run_prediction_pipeline(db_engine, scheduler, interval):
    # most return variables unused for our use case
    dataset, _, _, _, _ = run_pipeline(list([pd.to_datetime("now").date()]), db_engine, now=True)
    
    predictions_map = get_predictions(dataset)
    write_predictions(predictions_map)

    scheduler.enter(interval, 1, run_prediction_pipeline, (db_engine, scheduler, interval))


dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)


scheduler = sched.scheduler(time.time, time.sleep)

emapdb_engine = get_emapdb_engine()

run_prediction_pipeline(emapdb_engine, scheduler, interval=1800)

scheduler.run()
