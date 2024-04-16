# Copyright (C) 2012  Lukas Rist
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from sqlalchemy import create_engine, Text, Boolean, Table, Column, Integer, String, MetaData, select
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)

class Database(object):
    DORK_MAX_LENGTH = 200

    def __init__(self, engine):
        self.engine = engine
        self.meta = MetaData()
        self.tables = self.create(self.meta, self.engine)

    @classmethod
    def create(cls, meta, engine):
        tables = {}
        tablenames = ["intitle", "intext", "inurl", "filetype", "ext", "allinurl", "events"]  # Include 'events'
        for name in tablenames:
            if name == "events":
                tables[name] = Table(
                    name, meta,
                    Column('id', Integer, primary_key=True),
                    Column('time', String(30)),
                    Column('source', String(30)),
                    Column('request_url', String(500)),
                    Column('request_raw', Text),
                    Column('pattern', String(20)),
                    Column('filename', String(500)),
                    Column('file_sha256', String(500)),
                    Column('version', String(10)),
                    Column('sensorid', String(36)),
                    Column('known_file', Boolean)
                )
            else:
                tables[name] = Table(
                    name, meta,
                    Column('content', String(cls.DORK_MAX_LENGTH), primary_key=True),
                    Column('count', Integer),
                    Column('firsttime', String(30)),
                    Column('lasttime', String(30))
                )
        meta.create_all(engine)
        return tables

    def get_pattern_requests_sql(self, pattern="rfi"):
        sql = select([self.tables['events'].c.request_url]).where(self.tables['events'].c.pattern == pattern)
        with self.engine.connect() as connection:
            result = connection.execute(sql)
            return [row[0] for row in result]

    def insert_dorks(self, insert_list):
        if not insert_list:
            return
        with self.engine.begin() as connection:
            for item in insert_list:
                tablename = item['table']
                table = self.tables[tablename]
                content = item['content'][:self.DORK_MAX_LENGTH]
                sql = select(table).where(table.c.content == content)
                db_content = connection.execute(sql).fetchone()
                if not db_content:
                    connection.execute(table.insert(), {'content': content, 'count': 1, 'firsttime': datetime.now(), 'lasttime': datetime.now()})
                else:
                    connection.execute(table.update().where(table.c.content == content).values(lasttime=datetime.now(), count=table.c.count + 1))

    def get_dork_list(self, tablename, starts_with=None):
        table = self.tables[tablename]
        if starts_with:
            sql = select(table).where(table.c.content.like(f"%{starts_with}%"))
        else:
            sql = select(table)
        with self.engine.connect() as connection:
            result = connection.execute(sql)
            return [row[0] for row in result]

    def select_data(self, pattern="rfi"):
        # Get the reference to the 'events' table
        table = self.tables['events']
        # Correctly create the select statement using the select() function
        sql = select(table.c.request_url).where(table.c.pattern == pattern)
        with self.engine.connect() as connection:
            result = connection.execute(sql)
            return [row[0] for row in result]  # Return the list of matching request URLs
