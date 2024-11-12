from pydantic import BaseModel, Field


class Item(BaseModel):
    item: int = Field(..., description="Número del ítem")
    description: str = Field(..., description="Descripción del ítem")
    specifications: str = Field(..., description="Especificaciones del ítem en formato JSON sin caracteres de escaping")
    quantity: int = Field(..., description="Cantidad requerida")
    unit: str = Field(..., description="Unidad de medida (ej. 'Unidad')")

class Tender(BaseModel):
    items: list[Item] = Field(..., description="Lista de ítems de la licitación")