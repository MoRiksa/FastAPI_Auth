from pydantic import BaseModel
from typing import List


class MenuSingleItem(BaseModel):
    id_menu: str
    nama_menu: str
    harga: float
    id_kategori: int

    class Config:
        orm_mode = True
        from_attributes = True


class respondSingleMenu(BaseModel):
    status: str
    message: str
    data: List[MenuSingleItem]

    class Config:
        orm_mode = True
        from_attributes = True
