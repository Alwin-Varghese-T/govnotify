from sqlalchemy import create_engine, text
import os

db_connect_string = os.environ['db_connect_string']

engine = create_engine(db_connect_string,
                       connect_args={"ssl": {
                         "ssl_ca": "/etc/ssl/cert.pem"
                       }})
def load_links():
  with engine.connect() as conn:
    result = conn.execute(text("select * from sample"))
    items = []
    for row in result:
      items.append(row._asdict())
    return items  
