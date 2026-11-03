"""Local HTTP facade for the same transport adapter used by Nubi's authenticated MCP relay."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from nubi_transit import Transit, TransitError
from rail_journey import query
from express_bus import query as express_query, intercity_query
from tago_catalog import call as catalog_call
from kakao_location import places as kakao_places, taxi as kakao_taxi
from public_info import tourism, weather, air

app = FastAPI(title='Nubi Transport', docs_url=None, redoc_url=None, openapi_url=None)

class RailSearch(BaseModel):
    model_config = ConfigDict(extra='forbid')
    departure_city: str
    departure_station: str
    arrival_city: str
    arrival_station: str
    date: str
    after_time: str = '00:00'

class BusArrivals(BaseModel):
    model_config = ConfigDict(extra='forbid')
    city_code: str
    stop_id: str
    page: int = 1

class ExpressSearch(BaseModel):
    model_config = ConfigDict(extra='forbid')
    departure_terminal: str
    arrival_terminal: str
    date: str
    after_time: str = '00:00'

class PlaceSearch(BaseModel):
    model_config = ConfigDict(extra='forbid')
    query: str

class TaxiSearch(BaseModel):
    model_config = ConfigDict(extra='forbid')
    origin: str
    destination: str

class WeatherSearch(BaseModel):
    model_config = ConfigDict(extra='forbid')
    place: str

class AirSearch(BaseModel):
    model_config = ConfigDict(extra='forbid')
    province: str

def invoke(operation, arguments):
    client = Transit()
    try:
        if operation == 'rail': return query(client, **arguments)
        if operation == 'express': return express_query(client, **arguments)
        if operation == 'intercity': return intercity_query(client, **arguments)
        if operation == 'places': return kakao_places(client, **arguments)
        if operation == 'taxi': return kakao_taxi(client, **arguments)
        if operation == 'tourism': return tourism(client, **arguments)
        if operation == 'weather': return weather(client, **arguments)
        if operation == 'air': return air(client, **arguments)
        if operation.startswith('catalog:'): return catalog_call(client, operation.removeprefix('catalog:'), arguments)
        return client.call('bus_arrivals', arguments)
    except TransitError as exc:
        status = 400 if exc.state in ('invalid_arguments', 'selection_required') else 503
        raise HTTPException(status_code=status, detail={'state': exc.state, 'message': str(exc)}) from None
    finally:
        client.db.close()

@app.post('/v1/rail/search')
def rail_search(body: RailSearch):
    return invoke('rail', body.model_dump())

@app.post('/v1/bus/arrivals')
def bus_arrivals(body: BusArrivals):
    return invoke('bus', body.model_dump())

@app.post('/v1/bus/express/search')
def express_search(body: ExpressSearch):
    return invoke('express', body.model_dump())

@app.post('/v1/bus/intercity/search')
def intercity_search(body: ExpressSearch):
    return invoke('intercity', body.model_dump())

@app.post('/v1/catalog/{operation}')
def catalog_search(operation: str, body: dict):
    return invoke('catalog:' + operation, body)

@app.post('/v1/places/search')
def place_search(body: PlaceSearch):
    return invoke('places', body.model_dump())

@app.post('/v1/taxi/estimate')
def taxi_search(body: TaxiSearch):
    return invoke('taxi', body.model_dump())

@app.post('/v1/tourism/search')
def tourism_search(body: PlaceSearch):
    return invoke('tourism', body.model_dump())

@app.post('/v1/weather/now')
def weather_search(body: WeatherSearch):
    return invoke('weather', body.model_dump())

@app.post('/v1/air/quality')
def air_search(body: AirSearch):
    return invoke('air', body.model_dump())
