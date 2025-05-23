from fastapi import FastAPI
from pydantic import BaseModel
from estimative import estimativa
from fastapi.middleware.cors import CORSMiddleware


class AdressRequest(BaseModel):
    origem: str
    destino: str

class EstimativeResponse(BaseModel):
    uberX: str
    uberComfort: str
    uberBlack: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou substitua por ["http://localhost:3000"] se quiser restringir
    allow_credentials=True,
    allow_methods=["*"],  # ou ["POST", "OPTIONS"]
    allow_headers=["*"],
)


@app.post("/estimative", response_model=EstimativeResponse)
async def get_estimative(request: AdressRequest):
    valor = estimativa(request.origem, request.destino)
    uber_x = valor[0]
    uber_comfort = uber_x * 1.25
    uber_black= uber_comfort * 1.25

    return EstimativeResponse(
        uberBlack=f"{uber_black:.2f}",
        uberComfort=f"{uber_comfort:.2f}",
        uberX=f"{uber_x:.2f}"
    )
