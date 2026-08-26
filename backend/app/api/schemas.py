from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ComposeReadingRequest(BaseModel):
    matched_rule_ids: List[str] = Field(default_factory=list, min_length=1)
    allow_draft: bool = False


class PlanetPlacement(BaseModel):
    name: str
    sign: Optional[str] = None
    house: Optional[int] = Field(default=None, ge=1, le=12)
    nakshatra: Optional[str] = None
    navamsa_sign: Optional[str] = None
    dignity: Optional[str] = None
    retrograde: Optional[bool] = None
    conjunct: List[str] = Field(default_factory=list)


class ChartFactBundleRequest(BaseModel):
    lagna_sign: Optional[str] = None
    moon_sign: Optional[str] = None
    moon_nakshatra: Optional[str] = None
    moon_navamsa_sign: Optional[str] = None
    sun_navamsa_sign: Optional[str] = None
    planets: List[PlanetPlacement] = Field(default_factory=list)
    aspects_to_moon: List[str] = Field(default_factory=list)
    aspects_to_sun: List[str] = Field(default_factory=list)
    include_static_rules: bool = False
    compose: bool = False
    allow_draft: bool = False


class SaveRuleReviewRequest(BaseModel):
    decision: str = "unreviewed"
    comments: str = ""
    improvements: str = ""
    reviewer: str = ""
