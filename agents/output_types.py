from pydantic import BaseModel, Field
from typing import Optional


# Classes and functions from the original script
class CompanyName(BaseModel):
    company_name: str = Field(
        description="Company name extraction from the query",
        pattern="""^\w[\w.\-#&\s]*$""",
    )


class Ticker(BaseModel):
    company_symbol: str = Field(description="Company symbol from NSE/BSE, should only contain capital letters.")


class FinalOutput(BaseModel):
    company_summary: str = Field(description="A short summary of the company / business in question")
    pros: str = Field(description="A detailed list of pros of the company, based on the analysis")
    cons: str = Field(description="A detailed list of cons of the company, based on the analysis")
    additional_info: Optional[str] = Field(description="Additional notes based on the analysis")
