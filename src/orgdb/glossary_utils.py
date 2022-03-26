import sqlite3
import traceback
import sys
import json
from .Constants import Constants
from datetime import datetime


def get_glossary_terms(conn, log, request):
    cur = None
    try:
        cur = conn.cursor()
        log.trace("searching for glossary terms in the glossary table")
        cur.execute("""SELECT glossary.gid,glossary.glossary_id,metadata_field_registry.metadata_field,
                       glossary.value FROM glossary, metadata_field_registry where
                       glossary.glossary_id=metadata_field_registry.metadata_field_id""")
        row = cur.fetchone()
        data = []
        while row is not None:
            data.append(terms_from_row_object(row))
            row = cur.fetchone()

        log.trace("found {} records".format(len(data)))

        request.update({
            "response": {
                "terms": data,
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
def terms_from_row_object(row):
    return {
        "gid": row['gid'],
        "glossary_id": row['glossary_id'],
        "name": row['metadata_field'],
        "value": row['value'],
    }
