import sqlite3
import traceback
import sys
import json
from .Constants import Constants
from datetime import datetime


def get_system_properties(conn, log, request):
    cur = None
    try:
        cur = conn.cursor()
        log.trace("searching for system properties properties table")
        cur.execute("""SELECT properties.pid, properties.property_id, metadata_field_registry.metadata_field,
                       properties.value FROM properties, metadata_field_registry where
                       properties.property_id = metadata_field_registry.metadata_field_id""")
        row = cur.fetchone()
        data = []
        while row is not None:
            data.append(properties_from_row_object(row))
            row = cur.fetchone()

        log.trace("found {} records".format(len(data)))

        request.update({
            "response": {
                "properties": data,
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


def set_system_property(conn, log, request):
    cur = None
    if "property" not in request:
        request.update({
            "response": {
                "message": "request field: [property] not found",
                "status": 1
            }
        })
        return

    if "value" not in request:
        request.update({
            "response": {
                "message": "request field [value] not found",
                "status": 1
            }
        })
        return

    try:
        cur = conn.cursor()
        log.trace("searching for system property in metadata_field_registry table")
        cur.execute("""SELECT * FROM metadata_field_registry where metadata_field=?""", (request["property"],))
        row = cur.fetchone()
        property_id = 0
        if row is None:
            request.update({
                "response": {
                    "message": "Unknown property {}".format(request["property"]),
                    "status": 1
                }
            })
            return
        else:
            property_id = row['metadata_field_id']

        # Update property value
        cur.execute("""UPDATE properties set value=? where property_id=?""", (request["value"], property_id,))
        # commit changes to database
        cur.connection.commit()

        # return existing property value
        cur.execute("""SELECT properties.pid, properties.property_id, metadata_field_registry.metadata_field,
                       properties.value FROM properties, metadata_field_registry where
                       properties.property_id = metadata_field_registry.metadata_field_id and
                       properties.property_id=?""", (property_id,))
        row = cur.fetchone()
        if row is None:
            request.update({
                "response": {
                    "message": "Empty property record for {}".format(request["property"]),
                    "status": 1
                }
            })
            return

        request.update({
            "response": {
                "property": properties_from_row_object(row),
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


# ======================================================================================================================
#                                             L O C A L    F U N C T I O N S
# ======================================================================================================================
def properties_from_row_object(row):
    return {
        "pid": row['pid'],
        "property_id": row['property_id'],
        "name": row['metadata_field'],
        "value": row['value'],
    }
