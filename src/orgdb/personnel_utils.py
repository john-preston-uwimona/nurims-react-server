import sqlite3
import traceback
import sys
from .Constants import Constants
from datetime import datetime


def personnel_details_from_row_object(row):
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


def get_personnel_records(conn, log, request):
    cur = None
    try:
        cur = conn.cursor()
        log.trace("searching for personnel in items table")
        cur.execute("""SELECT * from item, item_topic_registry where
                       item.item_topic_id = item_topic_registry.item_topic_id and item_topic=? and type=?""",
                    (Constants.PERSONNEL_TOPIC, Constants.EMPLOYEE_RECORD_TYPE))
        row = cur.fetchone()
        data = []
        while row is not None:
            data.append({
                "item_id": row['item_id'],
                "nurims.title": row['title'],
                "nurims.withdrawn": row['withdrawn'],
            })
            row = cur.fetchone()

        log.trace("found {} records".format(len(data)))

        request.update({
            "response": {
                "personnel": data,
                "message": "",
                "status": 0
            }
        })

        cur.close()
    except (Exception, sqlite3.Error) as error:
        exc_type, exc_value, exc_tb = sys.exc_info()
        log.error(traceback.format_exception(exc_type, exc_value, exc_tb))
        request.update({
            "response": {
                "message": "{}".format(error),
                "status": 1
            }
        })
    finally:
        if cur is not None:
            cur.close()


def get_personnel_with_metadata(conn, log, request):
    cur = None
    try:
        cur = conn.cursor()
        log.trace("searching for personnel in items table")
        cur.execute("""SELECT * from item, item_topic_registry where
                       item.item_topic_id = item_topic_registry.item_topic_id and item_topic=? and type=?""",
                    (Constants.PERSONNEL_TOPIC, Constants.EMPLOYEE_RECORD_TYPE))
        row = cur.fetchone()
        data = []
        while row is not None:
            data.append({
                "item_id": row['item_id'],
                "nurims.title": row['title'],
                "nurims.withdrawn": row['withdrawn'],
            })
            row = cur.fetchone()

        log.trace("found {} records".format(len(data)))

        # Retrieve requested metadata
        for item in data:
            cur.execute("""SELECT * FROM metadata_value, metadata_field_registry where
                           metadata_value.metadata_field_id = metadata_field_registry.metadata_field_id and item_id=?""",
                        (item["item_id"],))
            row = cur.fetchone()
            metadata = []
            while row is not None:
                metadata.append({
                    row["metadata_field"]: row["text_value"]
                })
                row = cur.fetchone()
            item.update({"metadata": metadata})

        request.update({
            "response": {
                "personnel": data,
                "message": "",
                "status": 0
            }
        })

        cur.close()
    except (Exception, sqlite3.Error) as error:
        exc_type, exc_value, exc_tb = sys.exc_info()
        log.error(traceback.format_exception(exc_type, exc_value, exc_tb))
        request.update({
            "response": {
                "message": "{}".format(error),
                "status": 1
            }
        })
    finally:
        if cur is not None:
            cur.close()


def update_personnel_metadata(conn, log, request):
    cur = None
    if "item_id" not in request:
        request.update({
            "response": {
                "message": "request field: [item_id] not found",
                "status": 1
            }
        })
        return

    if "nurims.title" not in request:
        request.update({
            "response": {
                "message": "request field [nurims.title] not found",
                "status": 1
            }
        })
        return

    if "nurims.withdrawn" not in request:
        request.update({
            "response": {
                "message": "request field: [nurims.withdrawn] not found",
                "status": 1
            }
        })
        return

    if "metadata" not in request:
        request.update({
            "response": {
                "message": "request field: [metadata] not found",
                "status": 1
            }
        })
        return

    try:
        cur = conn.cursor()
        item_id = ""
        # if item_id = -1 then add new item record
        log.trace("searching for person in items table with item_id = {}".format(request["item_id"]))
        cur.execute("""SELECT COUNT(*) as n from item, item_topic_registry where
                       item.item_topic_id = item_topic_registry.item_topic_id and item_topic=? and
                       item_id=? and type=?""",
                    (Constants.PERSONNEL_TOPIC, request["item_id"], Constants.EMPLOYEE_RECORD_TYPE))
        row = cur.fetchone()
        rowcount = 0 if row is None else row["n"]
        log.trace("found {} records".format(rowcount))
        if rowcount == 0:
            request.update({
                "response": {
                    "message": "No personnel records with item_id = {} found".format(request["item_id"]),
                    "status": 1
                }
            })
            return
        elif rowcount > 1:
            request.update({
                "response": {
                    "message": "Multiple personnel records with item_id = {}".format(request["item_id"]),
                    "status": 1
                }
            })
            return

        # Update title and withdrawn metadata
        cur.execute("""UPDATE item set title=?, withdrawn=? where item_id=?""",
                    (request["nurims.title"], request["nurims.withdrawn"], request["item_id"],))

        # update item metadata using the keys specified in the metadata request field.
        # if no metadata field is specified in the request then update all the item[metadata]
        for m in request["metadata"]:
            for key in m:
                log.trace("updating metadata {}".format(key))
                cur.execute("""SELECT metadata_field_id from metadata_field_registry where metadata_field=?""", (key,))
                row = cur.fetchone()
                if row is not None:
                    metadata_field_id = row['metadata_field_id']
                    # if metadata field already exists then update it. Otherwise insert a new record
                    cur.execute("""SELECT COUNT(*) as N from metadata_value where item_id=? and metadata_field_id=?""",
                                (request["item_id"], metadata_field_id,))
                    row = cur.fetchone()
                    if row['N'] == 0:
                        cur.execute("""INSERT INTO metadata_value (item_id,metadata_field_id,text_value) values (?,?,?)""",
                                    (request["item_id"], metadata_field_id, m[key],))
                    else:
                        cur.execute("""UPDATE metadata_value set text_value=? where item_id=? and metadata_field_id=?""",
                                    (m[key], request["item_id"], metadata_field_id,))
                else:
                    log.trace("Unknown metadata {}".format(key))

        # commit changes to database
        cur.connection.commit()

        # return record
        cur.execute("""SELECT * from item, item_topic_registry where
                       item.item_topic_id = item_topic_registry.item_topic_id and item_topic=? and
                       item_id=? and type=?""",
                    (Constants.PERSONNEL_TOPIC, request["item_id"], Constants.EMPLOYEE_RECORD_TYPE))
        row = cur.fetchone()
        data = {
            "item_id": row['item_id'],
            "nurims.title": row['title'],
            "nurims.withdrawn": row['withdrawn'],
        }
        cur.execute("""SELECT * FROM metadata_value, metadata_field_registry where
                       metadata_value.metadata_field_id = metadata_field_registry.metadata_field_id and item_id=?""",
                    (data["item_id"],))
        row = cur.fetchone()
        metadata = []
        while row is not None:
            metadata.append({
                row["metadata_field"]: row["text_value"]
            })
            row = cur.fetchone()
        data.update({"metadata": metadata})

        request.update({
            "response": {
                "personnel": data,
                "message": "",
                "status": 0
            }
        })

        cur.close()
    except (Exception, sqlite3.Error) as error:
        exc_type, exc_value, exc_tb = sys.exc_info()
        log.error(traceback.format_exception(exc_type, exc_value, exc_tb))
        request.update({
            "response": {
                "message": "{}".format(error),
                "status": 1
            }
        })
    finally:
        if cur is not None:
            cur.close()


def get_personnel_metadata(conn, log, request):
    cur = None
    if "item_id" not in request:
        request.update({
            "response": {
                "message": "request field: [item_id] not found",
                "status": 1
            }
        })
        return

    try:
        cur = conn.cursor()
        log.trace("searching for person in items table with item_id = {}".format(request["item_id"]))
        cur.execute("""SELECT COUNT(*) as n from item, item_topic_registry where
                       item.item_topic_id = item_topic_registry.item_topic_id and item_topic=? and
                       item_id=? and type=?""",
                    (Constants.PERSONNEL_TOPIC, request["item_id"], Constants.EMPLOYEE_RECORD_TYPE))
        row = cur.fetchone()
        rowcount = 0 if row is None else row["n"]
        log.trace("found {} records".format(rowcount))
        if rowcount == 0:
            request.update({
                "response": {
                    "message": "No personnel records with item_id = {}".format(request["item_id"]),
                    "status": 1
                }
            })
            return
        elif rowcount > 1:
            request.update({
                "response": {
                    "message": "Multiple personnel records with item_id = {}".format(request["item_id"]),
                    "status": 1
                }
            })
            return
        else:
            cur.execute("""SELECT * from item, item_topic_registry where
                           item.item_topic_id = item_topic_registry.item_topic_id and item_topic=? and
                           item_id=? and type=?""",
                        (Constants.PERSONNEL_TOPIC, request["item_id"], Constants.EMPLOYEE_RECORD_TYPE))
            row = cur.fetchone()
            data = {
                "item_id": row['item_id'],
                "nurims.title": row['title'],
                "nurims.withdrawn": row['withdrawn'],
            }
            cur.execute("""SELECT * FROM metadata_value, metadata_field_registry where
                           metadata_value.metadata_field_id = metadata_field_registry.metadata_field_id and item_id=?""",
                        (data["item_id"],))
            row = cur.fetchone()
            metadata = []
            while row is not None:
                metadata.append({
                    row["metadata_field"]: row["text_value"]
                })
                row = cur.fetchone()
            data.update({"metadata": metadata})

        request.update({
            "response": {
                "personnel": data,
                "message": "",
                "status": 0
            }
        })

        cur.close()
    except (Exception, sqlite3.Error) as error:
        exc_type, exc_value, exc_tb = sys.exc_info()
        log.error(traceback.format_exception(exc_type, exc_value, exc_tb))
        request.update({
            "response": {
                "message": "{}".format(error),
                "status": 1
            }
        })
    finally:
        if cur is not None:
            cur.close()


def update_personnel_record(conn, log, request):
    cur = None
    if "item_id" not in request:
        request.update({
            "response": {
                "message": "request field: [item_id] not found",
                "status": 1
            }
        })
        return

    if "nurims.title" not in request:
        request.update({
            "response": {
                "message": "request field: [nurims.title] not found",
                "status": 1
            }
        })
        return

    if "nurims.withdrawn" not in request:
        request.update({
            "response": {
                "message": "request field: [nurims.withdrawn] not found",
                "status": 1
            }
        })
        return

    try:
        cur = conn.cursor()
        item_id = ""
        # if item_id = -1 then add new item record
        if request["item_id"] == -1:
            cur.execute("""SELECT item_topic_id from item_topic_registry where item_topic=?""",
                        (Constants.PERSONNEL_TOPIC,))
            row = cur.fetchone()
            if row is None:
                request.update({
                    "response": {
                        "message": "Cannot find person topic in item_topic_registry",
                        "status": 1
                    }
                })
                return
            item_topic_id = row['item_topic_id']
            ts = datetime.now().isoformat()
            cur.execute("""INSERT into item (item_topic_id,title,type,withdrawn,last_modified) VALUES (?,?,?,?,?)""",
                        (item_topic_id, request["nurims.title"], Constants.EMPLOYEE_RECORD_TYPE, request["nurims.withdrawn"], ts,))
            # update request item_id field
            cur.execute("""SELECT item_id from item where item_topic_id=? and title=? and withdrawn=? and last_modified=?""",
                        (item_topic_id, request["nurims.title"], request["nurims.withdrawn"], ts,))
            row = cur.fetchone()
            if row is None:
                request.update({
                    "response": {
                        "message": "Cannot find newly created personnel record",
                        "status": 1
                    }
                })
                return
            request["item_id"] = row['item_id']
        else:
            log.trace("searching for person in items table with item_id = {}".format(request["item_id"]))
            cur.execute("""SELECT COUNT(*) as n from item, item_topic_registry where
                           item.item_topic_id = item_topic_registry.item_topic_id and item_topic=? and
                           item_id=? and type=?""",
                        (Constants.PERSONNEL_TOPIC, request["item_id"], Constants.EMPLOYEE_RECORD_TYPE))
            row = cur.fetchone()
            rowcount = 0 if row is None else row["n"]
            log.trace("found {} records".format(rowcount))
            if rowcount == 0:
                request.update({
                    "response": {
                        "message": "No personnel records with item_id = {}".format(request["item_id"]),
                        "status": 1
                    }
                })
                return
            elif rowcount > 1:
                request.update({
                    "response": {
                        "message": "Multiple personnel records with item_id = {}".format(request["item_id"]),
                        "status": 1
                    }
                })
                return
            else:
                cur.execute("""UPDATE item SET title = ?, withdrawn = ? where item_id = ?""",
                            (request["nurims.title"], request["nurims.withdrawn"], request["item_id"], ))

        # update item metadata
        if "metadata" not in request:
            request.update({
                "response": {
                    "message": "request field: [metadata] not found",
                    "status": 1
                }
            })
            return

        for metadata in request["metadata"]:
            for key in metadata:
                log.trace("updating metadata {}".format(key))
                cur.execute("""SELECT metadata_field_id from metadata_field_registry where metadata_field=?""", (key,))
                row = cur.fetchone()
                if row is not None:
                    metadata_field_id = row['metadata_field_id']
                    # if metadata field already exists then update it. Otherwise insert a new record
                    cur.execute("""SELECT COUNT(*) as N from metadata_value where item_id=? and metadata_field_id=?""",
                                (request["item_id"], metadata_field_id,))
                    row = cur.fetchone()
                    if row['N'] == 0:
                        cur.execute("""INSERT INTO metadata_value (item_id,metadata_field_id,text_value) values (?,?,?)""",
                                    (request["item_id"], metadata_field_id, metadata[key],))
                    else:
                        cur.execute("""UPDATE metadata_value set text_value=? where item_id=? and metadata_field_id=?""",
                                    (metadata[key], request["item_id"], metadata_field_id,))
                else:
                    log.trace("Unknown metadata {}".format(key))

        # commit changes to database
        cur.connection.commit()

        # return record
        cur.execute("""SELECT * from item, item_topic_registry where
                       item.item_topic_id = item_topic_registry.item_topic_id and item_topic=? and
                       item_id=? and type=?""",
                    (Constants.PERSONNEL_TOPIC, request["item_id"], Constants.EMPLOYEE_RECORD_TYPE))
        row = cur.fetchone()
        data = {
            "item_id": row['item_id'],
            "nurims.title": row['title'],
            "nurims.withdrawn": row['withdrawn'],
        }
        cur.execute("""SELECT * FROM metadata_value, metadata_field_registry where
                       metadata_value.metadata_field_id = metadata_field_registry.metadata_field_id and item_id=?""",
                    (data["item_id"],))
        row = cur.fetchone()
        metadata = []
        while row is not None:
            metadata.append({
                row["metadata_field"]: row["text_value"]
            })
            row = cur.fetchone()
        data.update({"metadata": metadata})

        request.update({
            "response": {
                "personnel": data,
                "message": "",
                "status": 0
            }
        })

        cur.close()
    except (Exception, sqlite3.Error) as error:
        # print('SQLite error: %s' % (' '.join(error.args)))
        # print("Exception class is: ", error.__class__)
        # print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        # print("exc_type", exc_type)
        # print("exe_value", exc_value)
        # print("exe_tb", traceback.format_exception(exc_value, exc_tb))
        # print(traceback.format_exception(exc_type, exc_value, exc_tb))
        log.error(traceback.format_exception(exc_type, exc_value, exc_tb))
        request.update({
            "response": {
                "message": "{}".format(error),
                "status": 1
            }
        })
    finally:
        if cur is not None:
            cur.close()


def permanently_delete_person(pg, log, request):
    cur = None
    if "item_id" not in request:
        request.update({
            "response": {
                "message": "request field: [item_id] not found",
                "status": 1-1
            }
        })
        return

    if "nurims.withdrawn" not in request:
        request.update({
            "response": {
                "message": "request field: [nurims.withdrawn] not found",
                "status": 1
            }
        })
        return

    if request["nurims.withdrawn"] == 0:
        request.update({
            "response": {
                "message": "Personnel record cannot be deleted because it has NOT been disabled",
                "status": 1
            }
        })
        return

    try:
        cur = pg.cursor()
        log.trace("searching for metadata records with item_id: {}".format(request["item_id"]))
        cur.execute("SELECT COUNT(*) as N FROM metadata_value where item_id=?", (request["item_id"],))
        row = cur.fetchone()
        log.trace("found {} records".format(row["N"]))

        if row["N"] > 0:
            log.trace("Cannot delete personnel records with {} exiting metadata record(s)".format(row["N"]))
            request.update({
                "response": {
                    "message": "Cannot delete personnel records with {} exiting metadata record(s)".format(row["N"]),
                    "status": 1
                }
            })
            return

        log.trace("deleting item records with item_id: {}".format(request["item_id"]))
        cur.execute("DELETE FROM item where item_id=?", (request["item_id"],))

        request.update({
            "data": {
                "message": "",
                "status": 0
            }
        })

        cur.close()

    except (Exception, sqlite3.Error) as error:
        exc_type, exc_value, exc_tb = sys.exc_info()
        log.error(traceback.format_exception(exc_type, exc_value, exc_tb))
        request.update({
            "response": {
                "message": "{}".format(error),
                "status": 1
            }
        })
    finally:
        if cur is not None:
            cur.close()


def generate_personnel_records(pg, log, request):

    if True:
        return

#     cur = None
#     try:
#         cur = pg.cursor()
#         log.trace("updating client {} state to {}. (0 is offline, 1 is online)".format(client, state))
#         cur.execute("UPDATE clients SET online = %s WHERE client_id = %s", (state, client))
#         cur.close()
#     except (Exception, sqlite3.Error) as error:
#         log.error(error)
#     finally:
#         if cur is not None:
#             cur.close()
#
#
# def update_client_gps(pg, log, request):
#     cur = None
#     try:
#         cur = pg.cursor()
#         log.trace("searching for client {}".format(request["client"]))
#         cur.execute("SELECT client_id FROM clients where client_id = %s", (request["client"],))
#         log.trace("found {} clients".format(cur.rowcount))
#         row = cur.fetchone()
#
#         if row is None:
#             request.update({
#                 "data": {
#                     "message": "client {} NOT found".format(request["client"]),
#                     "status": 1
#                 }})
#         else:
#             log.trace("updating client {} record with {}".format(request["client"], request["reading"]))
#             cur.execute(
#                 "UPDATE clients SET easting = %s, northing = %s, altitude = %s, epsg = %s, cachedgps = %s WHERE client_id = %s",
#                 (request["reading"]["value"]["easting"], request["reading"]["value"]["northing"],
#                  request["reading"]["value"]["altitude"], request["reading"]["value"]["epsg"],
#                  request["reading"]["value"]["cachedgps"], request["client"]))
#
#         log.trace("fetching client {} record".format(request["client"]))
#         cur.execute("SELECT * FROM clients where client_id = %s", (request["client"],))
#         row = cur.fetchone()
#         details = {}
#         if row is not None:
#             details = client_details_from_row_object(row)
#         request.update({
#             "data": {
#                 "client": str(details),
#                 "message": "",
#                 "status": 0
#             }
#         })
#
#         cur.close()
#     except (Exception, sqlite3.Error) as error:
#         log.error(error)
#         request.update({
#             "data": {
#                 "message": "{}".format(error),
#                 "status": 1
#             }
#         })
#     finally:
#         if cur is not None:
#             cur.close()


def get_clients(pg, log, request):
    cur = None
    try:
        cur = pg.cursor()
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
    except (Exception, sqlite3.Error) as error:
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
        cur = pg.cursor()
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
    except (Exception, sqlite3.Error) as error:
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
        cur = pg.cursor()
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
    except (Exception, sqlite3.Error) as error:
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
        cur = pg.cursor()
        if "sensor_name" in request:
            log.trace(
                "searching for distinct client {} sensor {} data".format(request["client"], request["sensor_name"]))
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
    except (Exception, sqlite3.Error) as error:
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
        cur = pg.cursor()
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
            sql = "SELECT COUNT(data) as n FROM readings WHERE client_id IN ({}) AND name = '{}' AND reading_ts BETWEEN {}".format(
                ",".join(clients), name, ts_sql)
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
    except (Exception, sqlite3.Error) as error:
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
        cur = pg.cursor()
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
    except (Exception, sqlite3.Error) as error:
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
        cur = pg.cursor()
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
    except (Exception, sqlite3.Error) as error:
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
