import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import MetaData, Table, Column, Integer, String, create_engine, select

load_dotenv()

database_url = f"postgresql+psycopg2://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@" \
               f"{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('POSTGRES_DB')}"

async_database_url = f"postgresql+asyncpg://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@" \
                     f"{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('POSTGRES_DB')}"


async def insert_into_invnn(invnn_values):
    metadata_obj = MetaData()
    # engine = create_engine(
    #     url=database_url,
    #     echo=True,
    #     # pool_size=5,
    #     # max_overflow=10,
    # )

    async_engine = create_async_engine(
        url=async_database_url,
        # echo=True,
        # pool_size=5,
        # max_overflow=10,
    )

    invnn = Table(
        "invnn",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("invnn", String(70), unique=True),
    )

    # metadata_obj.create_all(async_engine)

    # with engine.connect() as conn:
    #     for value in invnn_values:
    #         select_statement = invnn.select().where(invnn.c.invnn == value)
    #         result = conn.execute(select_statement).fetchone()
    #
    #         if result is None:
    #             data_to_insert = {"invnn": value}
    #             insert_statement = invnn.insert().values(data_to_insert)
    #             conn.execute(insert_statement)
    #             conn.commit()
    #         else:
    #             print(f"Значение {value} уже существует в таблице и не будет повторно добавлено.")

    inserted_data = []

    async with async_engine.connect() as conn:
        # await conn.run_sync(metadata_obj.drop_all)
        await conn.run_sync(metadata_obj.create_all)

        for value in invnn_values:
            # select_statement = invnn.select().where(invnn.c.invnn == value)
            result = (await conn.execute(select(invnn).where(invnn.c.invnn == value))).fetchone()

            if result is None:
                inserted_data.append(value)
                data_to_insert = {"invnn": value}
                insert_statement = invnn.insert().values(data_to_insert)

                await conn.execute(insert_statement)
                await conn.commit()
            else:
                print(f"The value {value} is already in the table and will not be inserted.")

    return inserted_data
