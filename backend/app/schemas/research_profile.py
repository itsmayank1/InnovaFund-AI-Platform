from pydantic import BaseModel

class ResearchProfileBase(BaseModel):
    research_domains: str | None = None
    keywords: str | None = None
    bio: str | None = None
    publications: str | None = None
    patents: str | None = None
    technology_areas: str | None = None

class ResearchProfileCreate(ResearchProfileBase):
    pass

class ResearchProfileOut(ResearchProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True