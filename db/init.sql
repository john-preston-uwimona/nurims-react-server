DROP TABLE IF EXISTS "metadata_field_registry";
DROP INDEX IF EXISTS metadata_field_registry_field_id_index;
CREATE TABLE metadata_field_registry
(
    metadata_field_id INTEGER PRIMARY KEY AUTOINCREMENT,
    metadata_field    TEXT,
    scope_note        TEXT
);
CREATE UNIQUE INDEX metadata_field_registry_field_index ON metadata_field_registry (metadata_field);
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.identifier','An unambiguous reference to the resource');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.relateditemid','The item id of a related resource');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.withdrawn','Boolean value indicating if the resource has been withdrawn and is not available');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.publisher','An entity responsible for making the resource available');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.source','A related resource from which the described resource is derived');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.title','A name given to the resource');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.description','An account of the resource');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.description.provenance','A statement of any changes in ownership and custody of the resource since its creation that are significant for its authenticity, integrity, and interpretation. The statement may include a description of any changes successive custodians made to the resource');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.available','Date that the resource became or will become available in the format yyyy-mm-dd hh:mm:ss');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.surveillancefrequency','Surveillance frequency');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.inventorysurveillancefrequency','Inventory surveillance frequency');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.leaktestsurveillancefrequency','Leak test surveillance frequency');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.activitysurveillancefrequency','Activity surveillance frequency');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.entity.name','Name of the resource entity');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.entity.avatar','Blob of resource entity avatar');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.entity.address','Address of the resource entity');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.entity.contact','Contact details to correspond with the resource entity');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.entity.dob','Date Of Birth');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.entity.nid','National ID');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.entity.sex','Sex, i.e. m=male or f=female');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.entity.doseproviderid','Identifier assigned to resource entity by the dose provider. i.e. icens|34213');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.entity.workdetails','Brief text describing type and location of work carried out by the entity');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.entity.isbeingmonitored','If present and true it indicates that the entity is currently being monitored');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.entity.iswholebodymonitored','If present and true it indicates that the entity is currently being monitored for radiation exposure to the body with a whole body dosimeter');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.entity.iswristmonitored','If present and true it indicated that the entity is currently being monitored for radiation exposure to the wrist with a wrist dosimeter');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.entity.isextremitymonitored','If present and true it indicated that the entity is currently being monitored for radiation exposure to the fingers with a ring dosimeter');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.entity.assignedrole','A comma seperated list of assigned role(s) for a staff member.');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.coverage.location','Location of the resource');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.coverage.spatial','Spatial coverage of the resource');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.coverage.temporal','Temporal coverage of the resource');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.instrument','Instrument used for measurement');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.instrument.model','Model of instrument used for measurement');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.instrument.serialno','Serial number of instrument used for measurement');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.instrument.lastcalibration','Timestamp of last instrument calibration');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.dosimeter.monitorperiod','Start and ending date of dose evaluation period in ISO date format. i.e. YYYY-MM-DD|YYYY-MM-DD');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.dosimeter.id','An alphanumeric text used to uniquely identify the dosimeter');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.dosimeter.type','The type of dosimeter used for monitoring. i.e. WholeBody, Extremity, Wrist, Eye, etc');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.dosimeter.timestamp','Date and time when the dosimeter card was read. YYYY-MM-DDTHH:MM:SSZ');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.dosimeter.batchid','An alphanumeric identifier assigned by to the batch of dose monitor measurements');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.dosimeter.shallowdose','An alphanumeric identifier assigned by to the batch of dose monitor measurements');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.dosimeter.deepdose','An alphanumeric identifier assigned by to the batch of dose monitor measurements');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.dosimeter.extremitydose','An alphanumeric identifier assigned by to the batch of dose monitor measurements');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.dosimeter.wristdose','An alphanumeric identifier assigned by to the batch of dose monitor measurements');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.dosimeter.internaldose','An alphanumeric identifier assigned by to the batch of dose monitor measurements');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.dosimeter.units','Dose units');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.material.id','A unique identifier of maximum length 16 characters for the controlled material.');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.material.type','The type of a controlled material such as controlled nuclear item, irradiated samples, sealed radioactive source, unsealed radioactive source, nuclear material');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.material.registrationdate','The date when the controlled material was commissioned into service i.e. 2008-03-01');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.material.classification','Materials are classified in terms of their potential to cause deterministic health effects. Category 1 materials are considered to be the most ‘dangerous’ because they can pose a very high risk to human health if not managed safely and securely. An exposure of only a few minutes to an unshielded Category 1 source may be fatal. At the lower end of the categorization system, sources in Category 5 are the least dangerous; however, even these sources could give rise to doses in excess of the dose limits if not properly controlled, and therefore need to be kept under appropriate regulatory control.');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.material.manufacturer','Manufacturer of the controlled material');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.material.inventorystatus','Inventory status of material i.e. In-use, Dis-used, Waste, Disposal');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.material.physicalform','Controlled material physical form.');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.material.storagelocation','Controlled material storage location');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.material.nuclides','Nuclides contained in controlled material');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.material.quantityunits','Units of quantities for controlled materials');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.material.image','Image of the controlled material');
INSERT INTO metadata_field_registry (metadata_field, scope_note) VALUES('nurims.material.documents','Documents related to the controlled material');

DROP TABLE IF EXISTS "item_topic_registry";
DROP INDEX IF EXISTS item_topic_id_index;
CREATE TABLE item_topic_registry
(
    item_topic_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    item_topic        TEXT,
    scope_note        TEXT
);
CREATE UNIQUE INDEX item_topic_id_index ON item_topic_registry (item_topic_id, item_topic);
INSERT INTO item_topic_registry (item_topic, scope_note)VALUES ('person', 'Personnel details record');
INSERT INTO item_topic_registry (item_topic, scope_note)VALUES ('monitor', 'Area, Contamination and Waste monitor records');
INSERT INTO item_topic_registry (item_topic, scope_note)VALUES ('organisation', 'Organisation details record');
INSERT INTO item_topic_registry (item_topic, scope_note)VALUES ('measurement', 'Measurement values records');
INSERT INTO item_topic_registry (item_topic, scope_note)VALUES ('history', 'History details records');
INSERT INTO item_topic_registry (item_topic, scope_note)VALUES ('instrument', 'Instrument records');
INSERT INTO item_topic_registry (item_topic, scope_note)VALUES ('material', 'Controlled material records');
INSERT INTO item_topic_registry (item_topic, scope_note)VALUES ('manufacturer', 'Controlled material manufacturer records');
INSERT INTO item_topic_registry (item_topic, scope_note)VALUES ('document', 'Document records');
INSERT INTO item_topic_registry (item_topic, scope_note)VALUES ('storage_location', 'Controlled material storage location records');

DROP TABLE IF EXISTS "item";
CREATE TABLE item
(
    item_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    item_topic_id INTEGER REFERENCES item_topic_registry (item_topic_id),
    title         TEXT NOT NULL,
    type          TEXT NOT NULL,
    withdrawn     BOOL NOT NULL,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS "metadata_value";
CREATE TABLE metadata_value
(
    metadata_value_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id           INTEGER REFERENCES item (item_id),
    metadata_field_id INTEGER REFERENCES metadata_field_registry (metadata_field_id),
    text_value        TEXT
);

DROP TABLE IF EXISTS "provenance";
DROP INDEX IF EXISTS item_provenance_index;
DROP INDEX IF EXISTS item_provenance_value_index;
CREATE TABLE provenance
(
    provenance_value_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id             INTEGER REFERENCES item (item_id),
    metadata_field_id   INTEGER REFERENCES metadata_field_registry (metadata_field_id),
    text_value          TEXT,
    created             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX item_provenance_index ON provenance (item_id, metadata_field_id);
CREATE INDEX item_provenance_value_index ON provenance (text_value);


DROP TABLE IF EXISTS "properties";
CREATE TABLE properties
(
    pid           INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id   INTEGER REFERENCES metadata_field_registry (metadata_field_id),
    value         TEXT NOT NULL
);
CREATE UNIQUE INDEX property_index ON properties (pid, property_id);


DROP TABLE IF EXISTS "glosarry";
CREATE TABLE glossary
(
    gid           INTEGER PRIMARY KEY AUTOINCREMENT,
    glossary_id   INTEGER REFERENCES metadata_field_registry (metadata_field_id),
    value         TEXT NOT NULL
);
CREATE UNIQUE INDEX glossary_index ON glossary (gid, glossary_id);
