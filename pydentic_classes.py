from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, ValidationError, Field


class TableParser:
    thread_size: Optional[List[Optional[str]]]= Field(None, description="Size description")
    materials_surface:Optional[List[Optional[str]]]= Field(None, description="surface teratment material")