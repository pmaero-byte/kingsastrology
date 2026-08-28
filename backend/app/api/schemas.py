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


class BirthDataRequest(BaseModel):
    datetime_iso: str = Field(
        ...,
        description="Birth moment, ISO 8601 with offset, e.g. "
                    "1990-01-01T06:30:00+05:30 (assumed UTC if no offset)",
    )
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    elev_m: float = Field(default=0.0, ge=-430, le=9000)
    place: str = Field(default="")
    ayanamsa: str = Field(default="Lahiri")
