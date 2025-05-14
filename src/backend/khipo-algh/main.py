from fastapi import FastAPI
from pydantic import BaseModel
from estimative import estimativa

class AdressRequest(BaseModel):
    origem: str
    destino: str

app = FastAPI()

@app.post("/estimative")
async def estimative(request: AdressRequest):
    valor = estimativa(request.origem, request.destino)
    valorAround = "{:.2f}".format(valor[0])
    return {f"O valor estimado é de {valorAround}"}