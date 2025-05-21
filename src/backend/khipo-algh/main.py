from fastapi import FastAPI
from pydantic import BaseModel
from estimative import estimativa

class AdressRequest(BaseModel):
    origem: str
    destino: str

class EstimativeResponse(BaseModel):
    uberX: str
    uberComfort: str
    uberBlack: str

app = FastAPI()

@app.post("/estimative", response_model=EstimativeResponse)
async def get_estimative(request: AdressRequest):
    valor = estimativa(request.origem, request.destino)
    uber_x = valor[0]
    uber_comfort = uber_x * 1.15
    uber_black= uber_comfort * 1.15

    return EstimativeResponse(
        uberBlack=f"{uber_black:.2f}",
        uberComfort=f"{uber_comfort:.2f}",
        uberX=f"{uber_x:.2f}"
    )
