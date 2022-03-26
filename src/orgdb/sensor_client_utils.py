import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime


def client_details_from_row_object(row):
    return {
        "client_id": row['client_id'],
        "client_name": row['client_name'],
        "client_description": row['client_description'],
        "reg_ts": row['reg_ts'].isoformat(),
        "last_conn_established": row['last_conn_established'].isoformat(),
        "easting": float(row['easting']),
        "northing": float(row['northing']),
        "altitude": float(row['altitude']),
        "epsg": row['epsg'],
        "cachedgps": row['cachedgps'],
        "os": row['os'],
        "online": row['online']
    }


def reading_details_from_row_object(row):
    return {
        "rid": row['rid'],
        "client_id": row['client_id'],
        "sensor_name": row['name'],
        "reading_ts": row['reading_ts'].isoformat(),
        "data": float(row['data']),
        "units": row['units'],
        "maxdata": float(row['maxdata']),
        "mindata": float(row['mindata']),
        "avgdata": float(row['avgdata']),
        "first_reading_ts": row['mindate'].isoformat(),
        "easting": float(row['easting']),
        "northing": float(row['northing']),
        "altitude": float(row['altitude']),
        "epsg": row['epsg'],
        "cachedgps": row['cachedgps'],
    }


def register_client(pg, log, request):
    cur = None
    try:
        cur = pg.cursor(cursor_factory=DictCursor)
        log.trace("searching for client {}".format(request["uuid"]))
        cur.execute("SELECT client_id FROM clients where client_id = %s", (request["uuid"],))
        log.trace("found {} clients".format(cur.rowcount))
        row = cur.fetchone()

        if row is None:
            log.trace("adding client {} record".format(request["uuid"]))
            cur.execute(
                """INSERT INTO clients(client_id,client_name,client_description,reg_ts,
                   last_conn_established,os,online,easting,northing,altitude,epsg,cachedgps)
                   values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (request["uuid"], request["name"], request["description"], request["reg_ts"],
                 datetime.now(), request["os"], 1, request["easting"], request["northing"], request["altitude"],
                 request["epsg"], 0))
        else:
            log.trace("updating client {} record".format(request["uuid"]))
            cur.execute(
                """UPDATE clients SET last_conn_established = %s, os = %s, online = %s, easting = %s, northing = %s,
                   altitude = %s, epsg = %s WHERE client_id = %s""",
                (datetime.now(), request["os"], 1, request["easting"], request["northing"], request["altitude"],
                 request["epsg"], request["uuid"], ))

        log.trace("fetching client {} record".format(request["uuid"]))
        cur.execute("SELECT * FROM clients where client_id = %s", (request["uuid"],))
        row = cur.fetchone()
        details = {}
        if row is not None:
            details = client_details_from_row_object(row)
        request.update({
            "data": {
                "client": details,
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


def update_client_name_description(pg, log, request):
    cur = None
    try:
        cur = pg.cursor(cursor_factory=DictCursor)
        log.trace("searching for client {}".format(request["uuid"]))
        cur.execute("SELECT client_id FROM clients where client_id = %s", (request["uuid"],))
        log.trace("found {} clients".format(cur.rowcount))
        row = cur.fetchone()

        if row is not None:
            log.trace("updating client {} record".format(request["uuid"]))
            cur.execute("UPDATE clients SET client_name = %s, client_description = %s WHERE client_id = %s",
                        (request["name"], request["description"], request["uuid"],))

        log.trace("fetching client {} record".format(request["uuid"]))
        cur.execute("SELECT * FROM clients where client_id = %s", (request["uuid"],))
        row = cur.fetchone()
        details = {}
        if row is not None:
            details = client_details_from_row_object(row)
        request.update({
            "data": {
                "client": str(details),
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


def set_client_online_state(pg, log, client, state):
    if client is None:
        return

    cur = None
    try:
        cur = pg.cursor()
        log.trace("updating client {} state to {}. (0 is offline, 1 is online)".format(client, state))
        cur.execute("UPDATE clients SET online = %s WHERE client_id = %s", (state, client))
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        log.error(error)
    finally:
        if cur is not None:
            cur.close()


def update_client_gps(pg, log, request):
    cur = None
    try:
        cur = pg.cursor(cursor_factory=DictCursor)
        log.trace("searching for client {}".format(request["client"]))
        cur.execute("SELECT client_id FROM clients where client_id = %s", (request["client"],))
        log.trace("found {} clients".format(cur.rowcount))
        row = cur.fetchone()

        if row is None:
            request.update({
                "data": {
                    "message": "client {} NOT found".format(request["client"]),
                    "status": 1
                }})
        else:
            log.trace("updating client {} record with {}".format(request["client"], request["reading"]))
            cur.execute(
                "UPDATE clients SET easting = %s, northing = %s, altitude = %s, epsg = %s, cachedgps = %s WHERE client_id = %s",
                (request["reading"]["value"]["easting"], request["reading"]["value"]["northing"],
                 request["reading"]["value"]["altitude"], request["reading"]["value"]["epsg"],
                 request["reading"]["value"]["cachedgps"], request["client"]))

        log.trace("fetching client {} record".format(request["client"]))
        cur.execute("SELECT * FROM clients where client_id = %s", (request["client"],))
        row = cur.fetchone()
        details = {}
        if row is not None:
            details = client_details_from_row_object(row)
        request.update({
            "data": {
                "client": str(details),
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


def get_clients(pg, log, request):
    cur = None
    try:
        cur = pg.cursor(cursor_factory=DictCursor)
        log.trace("searching for clients")
        cur.execute("SELECT * FROM clients ORDER BY client_id")
        row = cur.fetchone()
        clients = []
        while row is not None:
            clients.append(client_details_from_row_object(row))
            row = cur.fetchone()

        for c in clients:
            log.trace("searching for distinct most recent client sensor data")
            cur.execute(
                """SELECT * FROM readings a JOIN (SELECT client_id, max(reading_ts) maxDate, min(reading_ts) minDate,
                   max(data) maxData, min(data) minData, avg(data) avgData FROM readings
                   GROUP BY client_id, name) b ON a.client_id = b.client_id AND a.reading_ts = b.maxDate and
                   a.client_id = %s""",
                (c["client_id"],))
            row = cur.fetchone()
            sensors = []
            while row is not None:
                sensors.append(reading_details_from_row_object(row))
                row = cur.fetchone()
            c.update({"sensors": sensors})

        request.update({
            "data": {
                "clients": clients,
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


def get_clients_list(pg, log, request):
    cur = None
    try:
        cur = pg.cursor(cursor_factory=DictCursor)
        log.trace("searching for clients")
        cur.execute("SELECT * FROM clients ORDER BY client_id")
        row = cur.fetchone()
        clients = []
        while row is not None:
            clients.append(client_details_from_row_object(row))
            row = cur.fetchone()

        request.update({
            "data": {
                "clients": clients,
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


def get_latest_client_sensor_data(pg, log, request):
    cur = None
    try:
        cur = pg.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT * FROM clients where client_id = %s", (request["client"],))
        row = cur.fetchone()
        online = 0
        if row is not None:
            online = row['online']
        log.trace("searching for distinct most recent client {} sensor data".format(request["client"]))
        cur.execute(
            """SELECT * FROM readings a JOIN (SELECT client_id, max(reading_ts) maxDate, min(reading_ts) minDate,
               max(data) maxData, min(data) minData, avg(data) avgData FROM readings
               GROUP BY client_id, name) b ON a.client_id = b.client_id AND a.reading_ts = b.maxDate and
               a.client_id = %s ORDER BY a.name""",
            (request["client"],))
        row = cur.fetchone()
        sensors = []
        while row is not None:
            sensors.append({
                "rid": row['rid'],
                "client_id": row['client_id'],
                "sensor_name": row['name'],
                "reading_ts": row['reading_ts'].isoformat(),
                "data": float(row['data']),
                "units": row['units'],
                "maxdata": float(row['maxdata']),
                "mindata": float(row['mindata']),
                "avgdata": float(row['avgdata']),
                "first_reading_ts": row['mindate'].isoformat(),
                "easting": float(row['easting']),
                "northing": float(row['northing']),
                "altitude": float(row['altitude']),
                "epsg": row['epsg'],
                "cachedgps": row['cachedgps'],
                "online": online
            })
            row = cur.fetchone()

        request.update({
            "data": {
                "sensor_data": sensors,
                "message": "",
                "status": 0
            }
        })

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
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


def get_client_sensor_data(pg, log, request):
    cur = None
    try:
        sensor_data = {}
        cur = pg.cursor(cursor_factory=DictCursor)
        if "sensor_name" in request:
            log.trace("searching for distinct client {} sensor {} data".format(request["client"], request["sensor_name"]))
            cur.execute("SELECT * FROM readings WHERE client_id = %s AND name = %s ORDER by reading_ts DESC LIMIT %s",
                        (request["client"], request["sensor_name"], request["limit"] if "limit" in request else 10,))
            row = cur.fetchone()
            sensors = []
            while row is not None:
                sensors.append({
                    "client_id": row['client_id'],
                    "sensor_name": str(row['name']),
                    "reading_ts": row['reading_ts'].isoformat(),
                    "data": float(row['data']),
                    "units": row['units'],
                })
                row = cur.fetchone()
            sensor_data[request["sensor_name"]] = sensors
        else:
            log.trace("searching for distinct client {} sensor names".format(request["client"]))
            cur.execute("SELECT DISTINCT name FROM readings WHERE client_id = %s ORDER BY name", (request["client"],))
            row = cur.fetchone()
            sensor_names = []
            while row is not None:
                sensor_names.append(row['name'])
                row = cur.fetchone()
            for name in sensor_names:
                log.trace("searching for distinct client {} sensor {} data".format(request["client"], name))
                cur.execute(
                    "SELECT * FROM readings WHERE client_id = %s AND name = %s ORDER by reading_ts DESC LIMIT %s",
                    (request["client"], name, request["limit"] if "limit" in request else 10,))
                row = cur.fetchone()
                data = []
                while row is not None:
                    data.append({
                        "client_id": row['client_id'],
                        "sensor_name": str(row['name']),
                        "reading_ts": row['reading_ts'].isoformat(),
                        "data": float(row['data']),
                        "units": row['units'],
                    })
                    row = cur.fetchone()
                sensor_data[name] = data

        request.update({
            "data": {
                "sensor_data": sensor_data,
                "message": "",
                "status": 0
            }
        })

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
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


def search_sensor_data(pg, log, request):
    cur = None

    try:
        sensor_data = {}
        cur = pg.cursor(cursor_factory=DictCursor)
        if "site" in request and request["site"]:
            # get list of clients
            csql = "SELECT * FROM clients where lower(client_name) SIMILAR TO lower('%(("
            if "," in request["site"]:
                for site in request["site"].split(","):
                    csql += site + "|"
            else:
                csql += request["site"]
            csql += "))%');"
            cur.execute(csql)
        else:
            cur.execute("SELECT * FROM clients")
        row = cur.fetchone()
        clients = []
        while row is not None:
            clients.append("'{}'".format(row['client_id']))
            row = cur.fetchone()
        print("----------------------")
        print(clients)
        print("----------------------")
        log.trace("searching for sensor data for clients {}".format(clients))

        sensor_count = {}
        sensor_names = []
        if "name" in request and request["name"]:
            for sensor in request["name"]:
                sensor_names.append(sensor)
        else:
            log.trace("searching for distinct sensor names")
            cur.execute("SELECT DISTINCT (name) FROM readings WHERE client_id IN ({})".format(",".join(clients)))
            row = cur.fetchone()
            while row is not None:
                sensor_names.append(str(row['name']))
                row = cur.fetchone()

        # data timestamp range
        ts_sql = "'{}' and '{}'".format(
            request["start_time"].replace('T', ' ')[:19] if "start_time" in request else "2022-01-17 00:00:00",
            request["end_time"].replace('T', ' ')[:19] if "end_time" in request else "2022-01-17 00:01:00",
        )

        for name in sensor_names:
            log.trace("counting sensor data for {}".format(name))
            sql = "SELECT COUNT(data) as n FROM readings WHERE client_id IN ({}) AND name = '{}' AND reading_ts BETWEEN {}".format(",".join(clients), name, ts_sql)
            print("%%%%%%%")
            print(sql)
            print("%%%%%%%")
            cur.execute(sql)
            row = cur.fetchone()
            while row is not None:
                sensor_count.update({
                    name: row["n"]
                })
                row = cur.fetchone()

        request.update({
            "data": {
                "sensor_data": {
                    "count": sensor_count
                },
                "message": "",
                "status": 0
            }
        })

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
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


def get_sensor_list(pg, log, request):
    cur = None
    try:
        cur = pg.cursor(cursor_factory=DictCursor)
        log.trace("searching for sensor names from readings database")
        cur.execute("SELECT DISTINCT(name) as name FROM readings")
        row = cur.fetchone()
        sensors = []
        while row is not None:
            sensors.append(row['name'])
            row = cur.fetchone()

        request.update({
            "data": {
                "sensors": sensors,
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


def get_sensor_data_range(pg, log, request):
    cur = None
    try:
        cur = pg.cursor(cursor_factory=DictCursor)
        # log.trace("searching for sensor names from readings database")
        cur.execute("SELECT MIN(reading_ts) as mn, MAX(reading_ts) as mx FROM readings")
        row = cur.fetchone()
        range = []
        while row is not None:
            range.append({
                "min": row['mn'],
                "max": row['mx']
            })
            row = cur.fetchone()

        request.update({
            "data": {
                "sensors": range,
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