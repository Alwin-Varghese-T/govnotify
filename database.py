from sqlalchemy import create_engine, text

db_connect_string = "mysql+pymysql://cc368utl7dt898dkdz23:pscale_pw_rHmdaRZZR219HzQ8IFSutYoOqt5HrlUXdn7SX9go8oC@ap-south.connect.psdb.cloud/govnotify?charset=utf8mb4"

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
