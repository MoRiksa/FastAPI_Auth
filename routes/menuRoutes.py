from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schemas.menuSchemas import (
    respondKategori,
    respondMenu,
    MenuItem,
)
from schemas.menusingleSchemas import respondSingleMenu, MenuSingleItem
from models.menuModels import Menu, Kategori
from database.database_session import get_db
import logging

# Konfigurasi logging
logging.basicConfig(
    filename="log/server/server.log",
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
)

router = APIRouter(prefix="/menu", tags=["Menu Management Data"])


# Get menu
@router.get(
    "/",
    summary="Get Semua Menu",
    description="Mengambil semua item yang ada dalam daftar menu",
    response_model=respondSingleMenu,
)
def get_menu_items(db: Session = Depends(get_db)):
    try:
        # Mengambil semua data dari tabel menu
        items = db.query(Menu).all()
        if not items:
            raise HTTPException(status_code=404, detail="Menu Tidak Ada")
        # Konversi hasil query response yang sudah disesuaikan dengan schema
        response_data = [
            {
                "id_menu": item.id_menu,
                "nama_menu": item.nama_menu,
                "harga": item.harga,
                "id_kategori": item.id_kategori,
            }
            for item in items
        ]
        logging.info("Menampilkan Daftar Menu")
        # Memanggil schema respondMenu untuk response dalam format JSON
        return respondSingleMenu(
            status="success", message="Menampilkan Daftar Menu", data=response_data
        )

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/menu-kategori",
    summary="Get Menu dengan Kategori",
    description="Mengambil semua item menu beserta kategorinya",
    response_model=respondKategori,
)
def get_menu_with_category(db: Session = Depends(get_db)):
    try:
        # Mengambil data hasil join antara Menu dan Kategori
        menukategori = (
            db.query(Menu, Kategori.nama_kategori)
            .join(Kategori, Menu.id_kategori == Kategori.id_kategori)
            .all()
        )

        if not menukategori:
            raise HTTPException(
                status_code=404, detail="Menu dengan Kategori Tidak Ada"
            )

        response_data = [
            {
                "id_menu": item.Menu.id_menu,
                "nama_menu": item.Menu.nama_menu,
                "harga": item.Menu.harga,
                "id_kategori": item.Menu.id_kategori,
                "nama_kategori": item[1],
            }
            for item in menukategori
        ]

        logging.info(f"Menampilkan Daftar Menu dengan Kategori {response_data}")

        # Mengembalikan response dengan schema yang sesuai
        return respondKategori(
            status="success",
            message="Menampilkan Daftar Menu dengan Kategori",
            data=response_data,
        )

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Terjadi Kesalahan: {str(e)}")


# Post menu
@router.post(
    "/",
    summary="Tambah Menu",
    description="Menambahkan item baru ke dalam data menu",
    response_model=respondSingleMenu,
)
def add_menu_item(item: MenuSingleItem, db: Session = Depends(get_db)):
    try:
        # validasi apakah menu sudah ada
        menu_tersedia = db.query(Menu).filter(Menu.nama_menu == item.nama_menu).first()
        if menu_tersedia:
            raise HTTPException(status_code=400, detail="Menu Sudah Ada")

        # Menambahkan menu baru ke database
        data_menu = Menu(
            id_menu=item.id_menu,
            nama_menu=item.nama_menu,
            harga=item.harga,
            id_kategori=item.id_kategori,
        )
        db.add(data_menu)
        db.commit()

        logging.info(f"Menu berhasil ditambahkan dengan data yang dikirim {item}")
        return respondSingleMenu(
            status="success", message="Menu berhasil ditambahkan", data=[item]
        )

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Get menu berdasar nama
@router.get(
    "/name/{nama_menu}",
    summary="Get Menu Berdasarkan Nama",
    description="Mengambil item berdasarkan nama menu",
    response_model=respondSingleMenu,
)
def get_menu_item_by_name(nama_menu: str, db: Session = Depends(get_db)):
    try:
        # Mencari item berdasarkan nama menu
        item = db.query(Menu).filter(Menu.nama_menu == nama_menu).first()
        if not item:
            raise HTTPException(status_code=404, detail="Menu Tidak Ada")
        logging.info(f"Menampilkan Menu dengan nama {nama_menu} berhasil")
        return respondSingleMenu(
            status="success",
            message="Menu Ditampilkan Berdasarkan Nama",
            data=[
                {
                    "id_menu": item.id_menu,
                    "nama_menu": item.nama_menu,
                    "harga": item.harga,
                    "id_kategori": item.id_kategori,
                }
            ],
        )

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Delete menu
@router.delete(
    "/{id_menu}",
    summary="Delete Menu",
    description="Menghapus item dalam daftar menu berdasarkan id_menu",
)
def delete_menu_item(id_menu: str, db: Session = Depends(get_db)):
    try:
        item = db.query(Menu).filter(Menu.id_menu == id_menu).first()
        if not item:
            raise HTTPException(status_code=404, detail="Menu Tidak Ditemukan")

        db.delete(item)
        db.commit()
        logging.info(f"Menghapus Menu dengan id {id_menu} berhasil")
        return respondMenu(status="success", message="Menu berhasil dihapus", data=[])

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
