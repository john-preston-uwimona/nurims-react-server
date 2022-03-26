import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime


def put_sensor_reading(pg, log, request):
    if request["reading"]["value"] == "None":
        request.update({
            "data": {
                "message": "cannot store reading value of None",
                "status": 1
            }
        })
        return

    cur = None
    try:
        cur = pg.cursor(cursor_factory=DictCursor)
        log.trace("searching for client {}".format(request["client"]))
        cur.execute("SELECT * FROM clients where client_id = %s", (request["client"],))
        log.trace("found {} clients".format(cur.rowcount))
        row = cur.fetchone()

        if row is None:
            request.update({
                "data": {
                    "message": "client {} NOT found".format(request["client"]),
                    "status": 1
                }})
        else:
            cid = row['cid']
            client_id = row['client_id']
            log.trace("adding reading {}: {}".format(request["sensor"], request["reading"]))
            data = request["reading"]["value"]
            units = request["reading"]["units"]
            easting = request["reading"]["easting"]
            northing = request["reading"]["northing"]
            altitude = request["reading"]["altitude"]
            epsg = request["reading"]["epsg"]
            cachedgps = request["reading"]["cachedgps"]
            if isinstance(data, (float, int)):
                cur.execute(
                    """INSERT INTO readings
                       (client_id,name,reading_ts,data,units,easting,northing,altitude,epsg,cachedgps) VALUES
                        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (client_id, request["sensor"], request["reading"]["timestamp"], data, units, easting, northing,
                     altitude, epsg, cachedgps))

        request.update({
            "data": {
                "message": "",
                "status": 0
            }
        })

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        log.error(error)
        request.update({
            "data": {
                "message": "{}".format(error),
                "status": 1
            }
        })
    finally:
        if cur is not None:
            cur.close()
