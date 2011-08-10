# PROJECTION = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
# PROJECTION = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs"
# PROJECTION = None
# PROJECTION = "+proj=utm +zone=32 +ellps=GRS80 +units=m +no_defs"


# three possibilities
## EPSG:900913 
# PROJECTION = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs"

## EPSG:3857: 
# PROJECTION = "+proj=merc +lon_0=0 +k=1 +x_0=0 +y_0=0 +a=6378137 +b=6378137 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs" 

## EPSG:4326 : 
# PROJECTION = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
 
 
PROJECTION = "+proj=utm +zone=32 +ellps=GRS80 +units=m +no_defs"

SAVE_AS_SHP = False

###### PostgreSQL setup

CREATE_TABLES = True
SAVE_INTO_POSTGRESQL = True
POSTGRESQL_CONNECTION_STRING = "postgresql://postgres:post2011gres@localhost/bikeability"
