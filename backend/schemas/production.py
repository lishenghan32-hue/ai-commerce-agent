"""
Production API schemas
"""
from typing import List
from pydantic import BaseModel


class GenerateScriptFromCommentsRequest(BaseModel):
    """Request model for generating script from comments"""
    product_url: str = ""
    product_name: str = ""
    product_info: str = ""
    selling_points: str = ""
    comments: List[str] = []


class GenerateScriptResponse(BaseModel):
    """Response model for script generation"""
    opening_hook: str
    pain_point: str
    solution: str
    proof: str
    offer: str


class ExportScriptsRequest(BaseModel):
    """Request model for exporting a single script"""
    script: GenerateScriptResponse
    format: str = "txt"


class RewriteScriptRequest(BaseModel):
    """Request model for rewriting script"""
    script: GenerateScriptResponse
    mode: str


class ParseProductRequest(BaseModel):
    """Request model for parsing product URL"""
    url: str


class ParseProductResponse(BaseModel):
    """Response model for product parsing"""
    name: str
    selling_points: str
    ocr_text: str = ""
    structured: dict = {}
    comments: List[str]
    images: List[str] = []


class ParseProductStreamRequest(BaseModel):
    """Request model for streaming product parsing with OCR"""
    name: str = ""
    selling_points: str = ""
    images: List[str] = []
    comments: List[str] = []
