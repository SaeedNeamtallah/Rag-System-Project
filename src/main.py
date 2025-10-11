from fastapi import FastAPI
from routes import base_router ,datarouter


app = FastAPI()
app.include_router(base_router)
app.include_router(datarouter)

