# built in imports
# pip3 install imports
from fastapi import FastAPI, status

# user created modules
from Service_health_check.code_folder.models import ReportLogRequestBody

app = FastAPI()


@app.get("/")
async def root():
    return status.HTTP_200_OK


@app.post(
    "/report",
    responses={
        201: {"description": "Log created :)"},
        501: {"description": "Mr.Sum Ting Wong suggests, Not Implemented"},
    },
)
async def report(body: ReportLogRequestBody):
    """Unified point to send all logs to. Use this as proxy for logging services.
    Having this architecture we can easily change logging providers or extend functionalities of logging by changing
    only this module.
    Below example tree of logging levels.
    """

    # @TODO JIRA-Ticket logging to https://sentry.io/welcome/
    # response = (await request.body()).decode("UTF-8")
    try:
        print(f"{body.level}:{body.service}:{body.status}:{body.data}")
        return status.HTTP_201_CREATED
    except Exception:
        return status.HTTP_501_NOT_IMPLEMENTED


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9050)
