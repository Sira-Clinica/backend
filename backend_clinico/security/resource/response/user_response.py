from pydantic import BaseModel

class MedicoResponse(BaseModel):
    full_name: str

    class Config:
        orm_mode = True
