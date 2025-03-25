from pydantic import BaseModel, Field
from typing import List, Optional, Union

"""class SizeEntry(BaseModel):
    value: str = Field(..., description="Size measurement value")
    type: str = Field("string", description="Data type of the value")

class ThreadSpecification(BaseModel):
    size: List[SizeEntry] = Field(
        ...,
        description="List of available thread sizes",
        examples=[[{"value": "0-80"}, {"value": "1/4-20 UNC"}]]
    )

class GenericPartsData(BaseModel):
    thread_specification: Union[str, ThreadSpecification] = Field(
        ...,
        description="Standardized thread specification (either simple string or detailed structure)",
        examples=[
            "7/16\"-14 UNS",  
            {"size": [{"value": "M6x1"}]}  
        ]
    )
    surface_material_properties: List[str] = Field(
        ...,
        description="Material composition and surface treatments",
        examples=["Black-Oxide Alloy Steel", "Zinc-Plated Carbon Steel"],
        default_factory=list

        ,examples=["0-80","1/4-20 UNC"]
        ,examples=["Black-Oxide Alloy Steel", "Zinc-Plated Carbon Steel"]
    )
"""
class GenericPartsData(BaseModel):
    thread_size: Optional[List[str]] = Field([], description="measurement value")
    material_surface: Optional[List[str]] = Field([], description="Material composition and surface treatments")