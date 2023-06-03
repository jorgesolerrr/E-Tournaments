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
    return {
        "table_name": table.name,
       
        "items" : {zip(table.columns.keys(),i) for i in r},

        "cols": list(table.columns.keys())
    }

@app.put("/{table_name}")
async def updateTable(table_name, request: Request):
    table = Table(table_name, metadata_obj, autoload_with=engine)
    params = request.query_params
    upd = await request.json()
    with engine.connect() as conn:
        r = list(conn.execute(table.update().where(*[
            getattr(table.c, key) == value
            for key, value in params.items()
        ]).values(**upd).returning(*table.c)))
        conn.commit()
    return {
        "table_name": table_name,
        "items":  {zip(table.columns.keys(),i) for i in r}, "cols": list(table.columns.keys())
    }

@app.delete("/{table_name}")
async def deleteFromTable(table_name, request: Request):
    table = Table(table_name, metadata_obj, autoload_with=engine)
    params = request.query_params
    if len(params.keys()) <= 0:
        raise Exception("No query parameters")
    with engine.connect() as conn:
        r = conn.execute(table.delete().where(*[
            getattr(table.c, key) == value
            for key, value in params.items()
        ]))
        conn.commit()
    
    return {
        "table_name": table_name,
        "items": r,
         "cols": list(table.columns.keys())
    }