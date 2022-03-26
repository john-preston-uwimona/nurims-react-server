import sqlite3
import os
import pathlib
import json
from . import personnel_utils, property_utils, manufacturer_utils, storage_utils, material_utils, glossary_utils, sensor_reading_utils, housekeeping_utils


def get_connection(name, config, log):
    dbpath = os.path.join(config["path"], name, '{}.db'.format(name))
    log.debug('connecting to database {}'.format(dbpath))
    # create pah to database file if not already exists
    pathlib.Path(os.path.dirname(dbpath)).mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect('file:{}'.format(dbpath), uri=True)
    log.debug('database connection successful.')
    log.debug('verifying database tables')

    # connection.autocommit = True
    connection.row_factory = sqlite3.Row

    cur = connection.cursor()

    # check if database is empty by getting count of tables with the name
    cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='metadata_field_registry' ''')

    # if the count is 1, then table exists
    if cur.fetchone()[0] == 0:
        # initialise database tables
        log.trace('initialising organisation database ...')
        with open(os.path.join(config["path"], config["init-sql"])) as reader:
            lines = reader.read().split(';')
            for line in lines:
                line = line.strip('\n')
                log.trace(line)
                if line:
                    cur.execute(line)
            connection.commit()
        log.trace('database initialised successfully')
    else:
        log.trace('database tables verified successfully.')

    # update system properties and glossary entries
    log.trace('updating system properties and glossary ...')
    with open(os.path.join(config["path"], config["default-property-values-sql"])) as reader:
        properties = json.load(reader)
        for entry in properties["entries"]:
            # log.trace("searching for system property in metadata_field_registry table")
            cur.execute("""SELECT metadata_field_id FROM metadata_field_registry where metadata_field=?""", (entry["entry"],))
            row = cur.fetchone()
            if row is None:
                log.warning("Unknown property {}. Skipping update".format(entry["entry"]))
            else:
                property_id = row['metadata_field_id']
                cur.execute("""SELECT pid FROM properties where property_id=?""", (property_id,))
                row = cur.fetchone()
                if row is None:
                    # Insert a new property value
                    log.warning("Inserting new property {}".format(entry["entry"]))
                    cur.execute("""INSERT INTO properties (property_id,value) VALUES (?,?)""",
                                (property_id, entry["value"],))
                else:
                    # Update property value
                    log.warning("Updating property {}".format(entry["entry"]))
                    cur.execute("""UPDATE properties set value=? where property_id=?""", (entry["value"], property_id,))

        connection.commit()

    with open(os.path.join(config["path"], config["default-glossary-values-sql"])) as reader:
        glossary = json.load(reader)
        for entry in glossary["entries"]:
            # log.trace("searching for glossary term in metadata_field_registry table")
            cur.execute("""SELECT metadata_field_id FROM metadata_field_registry where metadata_field=?""", (entry["entry"],))
            row = cur.fetchone()
            if row is None:
                log.warning("Unknown glossary term {}. Skipping update".format(entry["entry"]))
            else:
                glossary_id = row['metadata_field_id']
                cur.execute("""SELECT gid FROM glossary where glossary_id=?""", (glossary_id,))
                row = cur.fetchone()
                if row is None:
                    # Insert a new glossary value
                    log.warning("Inserting new glossary term {}".format(entry["entry"]))
                    cur.execute("""INSERT INTO glossary (glossary_id,value) VALUES (?,?)""",
                                (glossary_id, entry["value"],))
                else:
                    # Update glossary value
                    log.warning("Updating glossary term {}".format(entry["entry"]))
                    cur.execute("""UPDATE glossary set value=? where glossary_id=?""", (entry["value"], glossary_id,))

        connection.commit()

    return connection


class OrgDb:
    """ SensorManager base class. """

    def __init__(self, name=None, config=None, log=None):
        self._config = config
        self._log = log
        # verify database and get connection
        self._db = get_connection(name, config, log)

    def get_personnel_records(self, request):
        personnel_utils.get_personnel_records(self._db, self._log, request)

    def get_personnel_with_metadata(self, request):
        personnel_utils.get_personnel_with_metadata(self._db, self._log, request)

    def update_personnel_metadata(self, request):
        personnel_utils.update_personnel_metadata(self._db, self._log, request)

    def get_personnel_metadata(self, request):
        personnel_utils.get_personnel_metadata(self._db, self._log, request)

    def update_personnel_record(self, request):
        personnel_utils.update_personnel_record(self._db, self._log, request)

    def permanently_delete_person(self, request):
        personnel_utils.permanently_delete_person(self._db, self._log, request)

    def get_system_properties(self, request):
        property_utils.get_system_properties(self._db, self._log, request)

    def set_system_property(self, request):
        property_utils.set_system_property(self._db, self._log, request)

    def get_manufacturer_records(self, request):
        manufacturer_utils.get_manufacturer_records(self._db, self._log, request)

    def save_manufacturer_record(self, request):
        manufacturer_utils.save_manufacturer_record(self._db, self._log, request)

    def get_storage_records(self, request):
        storage_utils.get_storage_records(self._db, self._log, request)

    def save_storage_record(self, request):
        storage_utils.save_storage_record(self._db, self._log, request)

    def get_material_records(self, request):
        material_utils.get_material_records(self._db, self._log, request)

    def save_material_record(self, request):
        material_utils.save_material_record(self._db, self._log, request)

    def get_glossary_terms(self, request):
        glossary_utils.get_glossary_terms(self._db, self._log, request)

    def generate_personnel_records_pdf(self, request):
        personnel_utils.get_personnel_with_metadata(self._db, self._log, request)

    def generate_controlled_materials_list_pdf(self, request):
        material_utils.get_material_records(self._db, self._log, request)

    def close(self):
        self._db.close()

    @staticmethod
    def set_log_level(self, level):
        self._log.setLevel(level)
