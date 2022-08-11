# src/apps/pages/sitrep/widgets.py
from dash import dcc, html
import dash_bootstrap_components as dbc
from apps.pages.sitrep import BPID

ward_radio_button = html.Div(
    [
        html.Div(
            [
                dbc.RadioItems(
                    id=f"{BPID}ward_radio",
                    className="dbc d-grid d-md-flex justify-content-md-end btn-group",
                    # inputClassName="btn-check",
                    # labelClassName="btn btn-outline-primary",
                    # labelCheckedClassName="active btn-primary",
                    inline=True,
                    options=[
                        {"label": "T03", "value": "UCH T03 INTENSIVE CARE"},
                        {"label": "T06", "value": "UCH T06 SOUTH PACU"},
                        {"label": "GWB", "value": "GWB L01 CRITICAL CARE"},
                        {"label": "WMS", "value": "WMS W01 CRITICAL CARE"},
                        {"label": "NHNN0", "value": "NHNN C0 NCCU"},
                        {"label": "NHNN1", "value": "NHNN C1 NCCU"},
                    ],
                    value="UCH T03 INTENSIVE CARE",
                )
            ],
            className="dbc",
        ),
    ],
    className="radio-group",
)

closed_beds_switch = html.Div(
    [
        html.Div(
            [
                dbc.Switch(
                    id=f"{BPID}closed_beds_switch",
                    className="dbc d-grid d-md-flex justify-content-md-end",
                    label="Reveal closed beds",
                    value=False,
                )
            ],
            className="dbc",
        ),
    ],
    # className="radio-group",
)
