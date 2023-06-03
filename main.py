from fastapi import FastAPI, Request
from sqlalchemy import Table
from Database.database import engine, metadata_obj
app = FastAPI()
@app.get("/")
async def root():
    return {"tables": engine.table_names}

@app.post("/{table_name}")
async def postTable(table_name, request: Request):
    table = Table(table_name, metadata_obj, autoload_with=engine)
    obj = await request.json()
    with engine.connect() as conn:
        r = list(conn.execute(table.insert().values(**obj).returning(*table.c)))
        conn.commit()
    print(r)
    return {
        "table_name": table_name,
        "items": {zip(table.columns.keys(),i) for i in r},
        "cols": list(table.columns.keys())
        
    }

@app.get("/{table_name}")
async def getTable(table_name, request: Request):
    table = Table(table_name, metadata_obj, autoload_with=engine)
    with engine.connect() as conn:
       # r = list(conn.execute(table.select().filter_by(**params)))
        r = list(conn.execute(table.select().where(*[
            getattr(table.c, key) == value
            for key, value in request.query_params.items()
        ])))
    print(table.columns.keys())
    print(r)
    return {
        "table_name": table.name,
       
        "items" : {zip(table.columns.keys(),i) for i in r},

        "cols": list(table.columns.keys())
    }
