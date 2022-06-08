# `hyui`

User interface for the HYLODE project Much of the project structure is based
on the[`govcookiecutter` template project][govcookiecutter] but is adapted
for the development of Plotly Dash apps within a hospital environment. A
template application would be split into a frontend and a backend with
communication between the two via HTTP, and the project orchestrated by
docker-compose.

This file (`./readme.md`) is at the root of the project, but the application
code including the backend is in `./src/api/app1`, and the application itself is
kept in `./src/apps/app1`. An annotated figure of the directory structure is shown
below.

## Quick start (deployment not development)

```sh
git clone https://github.com/HYLODE/HyUi.git
cd HyUi
cp .secrets.example .secrets
# Now hand edit the .secrets file with usernames/passwords
pytest # OPTIONAL
docker-compose up -d --build && docker-composes logs -f
```

Go to [](http://my-host-name:8094/docs) for the API
Go to [](http://my-host-name:8095) for the dashboard landing page


## First run

### Installation

You will need to do this twice:

- on your local development machine
- on the UCLH generic application environment

Regardless, open the terminal and **git clone**.

```sh
git clonehttps://github.com/HYLODE/HyUi.git
cd HyUi
```

### Development (Local)

We assume that the majority of the development work will be on your own machine. You will therefore need to set-up your own dev environment. I have been using [conda miniforge](https://github.com/conda-forge/miniforge) because this has the best compatibility with the ARM processor on the Mac. I think it should also work on other machines but I have not tested this.

From within the HyUi directory

```sh
conda env create --file=./dev/steve/environment-short.yml
conda activate hyuiv4
```

Then confirm your set-up is OK

```sh
pytest tests/smoke
```

#### Local development without docker

Backend (all routes)

```sh
cd ./src
uvicorn api.main:app --reload --workers 1 --host 0.0.0.0 --port 8094
```

then navigate to [http://localhost:8094/docs]() to view the API documentation

... `app/main.py` hosts the various routes for the different apps


Frontend (per app)

```sh
cd ./src
python apps/app1/index.py
```


#### Local development with docker


### Development (Hospital)

There are two tasks that _must_ happen within the hospital environment: (1) preparing realistic mock data (2) deployment. The installation steps differ because here we do not have **sudo** (root) access (admin privileges). This means work must be performed using a combination of the default command line tools and docker.

### Preparing mock (synthetic) data

We will use the tooling provided by the [Synthetic Data Lab](https://sdv.dev) from a JupyterLab in a browser on a hospital machine. You will need access to the GAE to run this.

#### Scenario 1 (data via SQL)

Ensure that your database credentials are stored in the `./.secrets` file.
From the GAE commandline, navigate to the `synth` directory (`cd ./synth`), then use the Makefile commands as follows

1. `make mock1build` to build a docker image with JupyterLab and sdv pre-installed.
2. `make mock2run` to spin up JupyterLab (e.g. Working from GAE07 this will be at [](http://UCLVLDDPRAGAE07:8091) but the URL server will depend on the GAE).
3. `make mock3copyin` This will copy the example notebook `synth_test_data.ipynb` into the `./synth/portal` directory that is attached to the JupyterNotebook. Now open the example notebook `synth_test_data.ipynb` using JupyterLab and work through the steps. Create your SQL query and save as `query_live.sql` file must return a *SELECT* statement. Save just the synthesised mock data to `mock.h5`, and the query (`query_live.sql`). Be **careful** and ensure that you specify 'fakers' for all direct identifiers. We recommend the four eyes approach wherein a second person reviews your work before an export.
4. `make mock4copyout` to copy just the query and the synthetic data. Do not copy the notebook out of the `portal` directory unless you are sure you have stripped all personally identifiable data (i.e. clear all cells before saving).
5. `make mock5stop` to stop the JupyterLab instance and clear up

#### Scenario 2 (data via an http `get` request)

This is similar to the steps above but does not depend on the query or database credentials. You are likely to need to use the Python requests library to get the data that will be used by [sdv](https://sdv.dev).

**YOU MUST NOW PREPARE YOUR DATA MODEL IN `./src/api/models.py`**
This is a quality control step that ensures the data you handle is of the correct type.
let's generalise the naming so that query is matched to results which has rows
and results is a pydantic / sqlmodel class
by hand, specify as per ... https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/


A simple Pandas dataframe with two string columns and a timestamp.

```python
>>> df.types
firstname                          object
lastname                           object
admission_datetime                 datetime64[ns]
```

The equivalent SQLModel. Note that `firstname` is optional but that `lastname` and `admission_datetime` are not.

```python
from sqlmodel import SQLModel
from datetime import datetime

class ResultsBase(SQLModel):
    """
    Generic results class to hold data returned from
    the SQL query or the API
    """
    firstname: Optional[str]
    lastname: str
    admission_datetime: datetime

```

You can also use the [`@validator`](https://pydantic-docs.helpmanual.io/usage/validators/) decorator function to add additional validation.
### Deployment

Set the environment variable to *prod*, then run *docker-compose*.

```sh
export ENV=prod
pytest
docker-compose up -d --build && docker-compose logs -f
```

You will need create a local `./.secrets` file with database credentials so preferably set the *ENV* to `prod` there.





## Frontend vs Backend

### Backend
This is a Python FastApi server that is exposed on port 8094 when running `docker-compose up -d` from the project root, or `uvicorn main:app` when running from `src/api/` locally.

### Frontend
This is a Plotly Dash app served on port 8095.

### Orchestrating front and back end

**IMPORTANT**: ensure you have created a ./.secrets file with at least the same info as the ./.secrets.example version

```bash
docker-compose down
docker-compose up -d --build && docker-compose logs -f
```


## Project structure

```
.
|
|-- readme.md           // this file and the project root
|-- Makefile            // standard project commands to be run from the shell
|-- config files        // e.g. requirements.txt, .gitignore
|-- .secrets            // e.g. .secrets etc excluded from version control
|-- secrets.example     // an example version of .secrets above
|-- docker-compose.yml  // orchestrate front/backend
|-- src
    |-- frontend
        |-- Dockerfile
        |-- dash_app.py
    |-- backend
        |-- Dockerfile
        |-- query.sql   // SQL used to drive the backend API
|-- synth               // Synthetic data generation for testing
    |-- work
|-- tests
|-- docs
|-- data
|-- outputs
|-- notebooks           // jupyter notebooks etc
|-- try                 // ideas playground


```


## Development environments

### Local machine

Your own laptop etc. without access to personally identifiable information (PII) etc.
You wish to be able to build and run applications with test data.


### Live machine

An NHS machine or similar within sensitive environment with access to PII.
You wish to be able to deploy the actual application.

## Development workflow

### 1. Make synthetic version of the data

We imagine that the developer has the appropriate permissions to view the raw data including patient identifiable information (either themselves, or in partnership with a colleague). A justification for this position is [here][provisioning]. Practically, this means early interactive data exploration using the UCLH Datascience Desktop and similar tools, and in turn access to EMAP and Clarity/Caboodle.

This should generate an initial data specification, and this can be used to generate synthetic data. The synthetic data can then be used to drive the rest of the pathway.

### 2. Develop with synthetic data
### 3. Write some tests and quality control
### 4. Update the plot to run live
### 5. Allow inspection over the last months
### 6. Split by specialty






```{warning}
Where this documentation refers to the root folder we mean where this README.md is
located.
```

## Getting started

To start using this project, [first make sure your system meets its
requirements](#requirements).

To be added.

### Requirements

```{note} Requirements for contributors
[Contributors have some additional requirements][contributing]!
```

- Python 3.6.1+ installed
- a `.secrets` file with the [required secrets and
  credentials](#required-secrets-and-credentials)
- [load environment variables][docs-loading-environment-variables] from `.envrc`

To install the Python requirements, open your terminal and enter:

```shell
pip install -r requirements.txt
```

## Required secrets and credentials

To run this project, [you need a `.secrets` file with secrets/credentials as
environmental variables][docs-loading-environment-variables-secrets]. The
secrets/credentials should have the following environment variable name(s):

| Secret/credential | Environment variable name | Description                                |
|-------------------|---------------------------|--------------------------------------------|
| Secret 1          | `SECRET_VARIABLE_1`       | Plain English description of Secret 1.     |
| Credential 1      | `CREDENTIAL_VARIABLE_1`   | Plain English description of Credential 1. |

Once you've added, [load these environment variables using
`.envrc`][docs-loading-environment-variables].

## Licence

Unless stated otherwise, the codebase is released under the MIT License. This covers
both the codebase and any sample code in the documentation. The documentation is ©
Crown copyright and available under the terms of the Open Government 3.0 licence.

## Contributing

[If you want to help us build, and improve `hyui`, view our
contributing guidelines][contributing].

## Acknowledgements

[This project structure is based on the `govcookiecutter` template
project][govcookiecutter].

[contributing]: ./docs/contributor_guide/CONTRIBUTING.md
[govcookiecutter]: https://github.com/best-practice-and-impact/govcookiecutter
[docs-loading-environment-variables]: ./docs/user_guide/loading_environment_variables.md
[docs-loading-environment-variables-secrets]: ./docs/user_guide/loading_environment_variables.md#storing-secrets-and-credentials
[provisioning]: ./docs/notes/provisioning_data.md
