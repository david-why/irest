# iREST: macOS REST API

Expose macOS Reminders and Calendar via a local FastAPI REST service using PyObjC.

## Usage

You need [Poetry](https://python-poetry.org/docs/#installation) to install the dependencies. After you install Poetry, you can clone this repository and install the dependencies with the following command:

```bash
git clone https://github.com/david-why/irest.git
cd irest
poetry install
```

### Run the server

You can run the server with the following command:

```bash
poetry run python run.py
```

This will start a development server on `http://localhost:8120`.
