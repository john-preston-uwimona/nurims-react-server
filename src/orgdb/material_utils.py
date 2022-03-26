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


def get_material_records(conn, log, request):
    cur = None
    try:
        cur = conn.cursor()

        data = []
        if "item_id" in request:
            log.trace("searching for material records in items table with item_id={}".format(request["item_id"]))
            cur.execute("""SELECT * from item, item_topic_registry where
                           item.item_topic_id = item_topic_registry.item_topic_id and 
                           item_topic=? and type=? and item_id=?""",
                        (Constants.MATERIAL_TOPIC, Constants.MATERIAL_RECORD_TYPE, request["item_id"],))
            row = cur.fetchone()
            if row is not None:
                data.append({
                    "item_id": row['item_id'],
                    "nurims.title": row['title'],
                    "nurims.withdrawn": row['withdrawn'],
                })
        else:
            log.trace("searching for material records in items table")
            cur.execute("""SELECT * from item, item_topic_registry where
                           item.item_topic_id = item_topic_registry.item_topic_id and item_topic=? and type=?""",
                        (Constants.MATERIAL_TOPIC, Constants.MATERIAL_RECORD_TYPE))
            row = cur.fetchone()
            while row is not None:
                data.append({
                    "item_id": row['item_id'],
                    "nurims.title": row['title'],
                    "nurims.withdrawn": row['withdrawn'],
                })
                row = cur.fetchone()

        # Get any metadata
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

        log.trace("found {} records".format(len(data)))

        request.update({
            "response": {
                "materials": data,
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


def save_material_record(conn, log, request):
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

    try:
        cur = conn.cursor()
        # if item_id = -1 then add new item record
        if request["item_id"] == -1:
            cur.execute("""SELECT item_topic_id from item_topic_registry where item_topic=?""",
                        (Constants.MATERIAL_TOPIC,))
            row = cur.fetchone()
            if row is None:
                request.update({
                    "response": {
                        "message": "Cannot find material topic in item_topic_registry",
                        "status": 1
                    }
                })
                return
            log.trace("inserting a new material record")
            item_topic_id = row['item_topic_id']
            ts = datetime.now().isoformat()
            cur.execute("""INSERT into item (item_topic_id,title,type,withdrawn,last_modified) VALUES (?,?,?,?,?)""",
                        (item_topic_id, request["nurims.title"], Constants.MATERIAL_RECORD_TYPE, request["nurims.withdrawn"], ts,))
            # retrieve item_id for new record
            cur.execute("""SELECT item_id from item where item_topic_id=? and title=? and withdrawn=? and last_modified=?""",
                        (item_topic_id, request["nurims.title"], request["nurims.withdrawn"], ts,))
            row = cur.fetchone()
            if row is None:
                request.update({
                    "response": {
                        "message": "Cannot find newly created material record",
                        "status": 1
                    }
                })
                return
            request["item_id"] = row['item_id']
        else:
            log.trace("searching for material in items table with item_id = {}".format(request["item_id"]))
            cur.execute("""SELECT COUNT(*) as n from item, item_topic_registry where
                           item.item_topic_id = item_topic_registry.item_topic_id and item_topic=? and
                           item_id=? and type=?""",
                        (Constants.MATERIAL_TOPIC, request["item_id"], Constants.MATERIAL_RECORD_TYPE))
            row = cur.fetchone()
            rowcount = 0 if row is None else row["n"]
            log.trace("found {} records".format(rowcount))
            if rowcount == 0:
                request.update({
                    "response": {
                        "message": "No material records with item_id = {}".format(request["item_id"]),
                        "status": 1
                    }
                })
                return
            elif rowcount > 1:
                request.update({
                    "response": {
                        "message": "Multiple material records with item_id = {}".format(request["item_id"]),
                        "status": 1
                    }
                })
                return
            else:
                cur.execute("""UPDATE item SET title = ?, withdrawn = ? where item_id = ?""",
                            (request["nurims.title"], request["nurims.withdrawn"], request["item_id"], ))

        # update item metadata
        if "metadata" in request:
            for metadata in request["metadata"]:
                for key in metadata:
                    cur.execute("""SELECT metadata_field_id from metadata_field_registry where metadata_field=?""",
                                (key,))
                    row = cur.fetchone()
                    if row is not None:
                        metadata_field_id = row['metadata_field_id']
                        # if metadata field already exists then update it. Otherwise insert a new record
                        cur.execute(
                            """SELECT COUNT(*) as N from metadata_value where item_id=? and metadata_field_id=?""",
                            (request["item_id"], metadata_field_id,))
                        row = cur.fetchone()
                        if row['N'] == 0:
                            log.trace("inserting metadata {}".format(key))
                            cur.execute(
                                """INSERT INTO metadata_value (item_id,metadata_field_id,text_value) values (?,?,?)""",
                                (request["item_id"], metadata_field_id, metadata[key],))
                        else:
                            log.trace("updating metadata {}".format(key))
                            cur.execute(
                                """UPDATE metadata_value set text_value=? where item_id=? and metadata_field_id=?""",
                                (metadata[key], request["item_id"], metadata_field_id,))
                    else:
                        log.trace("Unknown metadata {}".format(key))

        # commit changes to database
        cur.connection.commit()

        # return record
        cur.execute("""SELECT * from item, item_topic_registry where
                       item.item_topic_id = item_topic_registry.item_topic_id and item_topic=? and
                       item_id=? and type=?""",
                    (Constants.MATERIAL_TOPIC, request["item_id"], Constants.MATERIAL_RECORD_TYPE))
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
                Constants.MATERIAL_TOPIC: data,
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

