from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, DeclarativeBase, sessionmaker, scoped_session, Query
from configurations.environments import Values
from datetime import datetime
import pytz as pytz
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy import Column, DateTime, Integer, Boolean, func
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import FunctionElement

Model = declarative_base()


class SoftDeleteQuery(Query):
    def get(self, ident):
        # Override get() so that it returns None for deleted objects
        obj = super(SoftDeleteQuery, self).get(ident)
        return obj if obj is None or not obj.is_deleted else None

    def __new__(cls, *args, **kwargs):
        obj = super(SoftDeleteQuery, cls).__new__(cls)
        with_deleted = kwargs.pop('_with_deleted', False)
        if len(args) > 0:
            super(SoftDeleteQuery, obj).__init__(*args, **kwargs)
            return obj.filter(Model.is_deleted == False) if not with_deleted else obj
        return obj

    def __init__(self, *args, **kwargs):
        pass

    def with_deleted(self):
        return self.__class__(self._query_entity, session=self.session, _with_deleted=True)

    def _get(self, ident):
        return super(SoftDeleteQuery, self).get(ident)

    def filter_by(self, **kwargs):
        return super(SoftDeleteQuery, self).filter_by(**kwargs).filter(Model.is_deleted == False)


async_engine = create_async_engine(Values.DB_CONFIG,
                                   future=True, pool_pre_ping=True,
                                   pool_size=10,  # Increased from 5 to 20
                                   max_overflow=15,  # Increased from 10 to 30
                                   pool_recycle=3600, )
SessionLocal = async_sessionmaker(bind=async_engine,
                                  autoflush=False,
                                  autocommit=False, class_=AsyncSession,
                                  expire_on_commit=False,
                                  query_cls=SoftDeleteQuery)


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()


@asynccontextmanager
async def get_db_outside():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()


class GetTzDatetime(FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(GetTzDatetime, 'postgresql')
def compile_get_tz_datetime(element, compiler, **kw):
    tz_name = element.clauses.clauses[0].value
    tz = pytz.timezone(tz_name)
    offset = tz.utcoffset(datetime.now())
    return compiler.process(func.now() + offset)


def generate_uuid():
    return uuid.uuid4


class DbBaseModel(Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False, unique=True)
    created_at = Column(DateTime, default=GetTzDatetime('Asia/Tehran'))
    updated_at = Column(DateTime, onupdate=GetTzDatetime('Asia/Tehran'))
    is_deleted = Column(Boolean, default=False)
