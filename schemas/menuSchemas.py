from pydantic import BaseModel
from typing import List


# Model untuk item menu (dipecah)
class MenuItem(BaseModel):
    id_menu: str
    nama_menu: str
    harga: float
    id_kategori: int
    nama_kategori: str

    class Config:
        orm_mode = True
        from_attributes = True


# Model untuk respons menu (dalam bentuk responses)
class respondMenu(BaseModel):
    status: str
    message: str
    data: List[MenuItem]

    class Config:
        orm_mode = True
        from_attributes = True


class KategoriItem(BaseModel):
    id_menu: str
    nama_menu: str
    harga: float
    id_kategori: int
    nama_kategori: str

    class Config:
        orm_mode = True
        from_attributes = True


class respondKategori(BaseModel):
    status: str
    message: str
    data: List[KategoriItem]

    class Config:
        orm_mode = True
        from_attributes = True
