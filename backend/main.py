from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated

import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

# from fastapi import Request, Form
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class DetailsBase(BaseModel):
    detail_name: str
    detail_type: str
    
class CountryBase(BaseModel):
    country_code: int
    country_name: str
    country_details: List[DetailsBase]
    
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependencies = Annotated[Session, Depends(get_db)]    

@app.get("/")
async def root():
    return {'message': 'hello world'}

@app.post("/create_configuration")
async def create_configuration(country: CountryBase, db: db_dependencies):
    db_country = models.Country(country_name=country.country_name, country_code=country.country_code)
    
    db.add(db_country)
    db.commit()
    db.refresh(db_country)
    
    for detail in country.country_details:
        db_detail = models.Detail(detail_name=detail.detail_name, detail_type=detail.detail_type, country_id=db_country.id)
        db.add(db_detail)
        db.commit()

@app.get("/get_configuration/{country_code}")
async def get_configuration(country_code: int, db: db_dependencies):
    country_config = db.query(models.Country).filter(models.Country.country_code == country_code).first()
    
    if not country_config:
        raise HTTPException(status_code=404, detail="No such country found")
    
    return country_config

@app.put("/update_configuration/{country_code}")
async def update_configuration(country_code: str, updated_country: CountryBase, db: db_dependencies):
    country_config = db.query(models.Country).filter(models.Country.country_code == country_code).first()

    if not country_config:
        raise HTTPException(status_code=404, detail="No such country found")

    country_config.country_name = updated_country.country_name
    db.commit()
    db.refresh(country_config)

    # Delete existing details
    db.query(models.Detail).filter(models.Detail.country_id == country_config.id).delete()
    db.commit()

    # Add new details
    for detail in updated_country.country_details:
        db_detail = models.Detail(detail_name=detail.detail_name, detail_type=detail.detail_type, country_id=country_config.id)
        db.add(db_detail)
    db.commit()

    return country_config

@app.delete("/delete_configuration/{country_code}")
async def delete_configuration(country_code: str, db: db_dependencies):
    country_config = db.query(models.Country).filter(models.Country.country_code == country_code).first()

    if not country_config:
        raise HTTPException(status_code=404, detail="No such country found")

    # Delete details associated with the country
    db.query(models.Detail).filter(models.Detail.country_id == country_config.id).delete()
    db.commit()

    # Delete the country
    db.delete(country_config)
    db.commit()

    return {"detail": "Country configuration deleted"}

