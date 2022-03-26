import os
import math
import shared_objects

from authentication import generate_keys, verify_password
from expiringdict import ExpiringDict

tasks = {}
task = lambda f: tasks.setdefault(f.__name__, f)

keys = ExpiringDict(max_len=100, max_age_seconds=10000)


def run(request, db=None, md=None, docbook=None, msg_queue=None):
    try:
        if db is None:
            request.update({
                "response": {
                    "message": "Organisation database NOT defined",
                    "status": 1
                }
            })
        else:
            for t in tasks:
                if t == request["cmd"].replace("-", "_"):
                    tasks[t](request, db, md, docbook, msg_queue)
                    return
            request.update({
                "response": {
                    "message": "Unknown server request command: {}".format(request["cmd"]),
                    "status": 1
                }
            })
    except KeyError as e:
        request.update({
            "response": {
                "message": "{}".format(e),
                "status": 1
            }
        })
    msg_queue.put(request)


@task
def set_logging_level(request, db=None, md=None, docbook=None, msg_queue=None):
    shared_objects.log.setLevel(shared_objects.get_level_number(request["level"]))
    message = "setting logging level to '{}'".format(shared_objects.get_level_name(shared_objects.log.level))
    shared_objects.log.info(message)
    request.update({
        "status": 0,
        "message": message
    })
    msg_queue.put(request)


@task
def get_public_key(request, db=None, md=None, docbook=None, msg_queue=None):
    pr_key_pem, pu_key_pem = generate_keys()
    keys[request["uuid"]] = pr_key_pem
    request["data"] = {}
    # request["data"]["public"] = public_key_pem(public_key).decode('utf8').replace("'", '"')
    request["data"]["public"] = pu_key_pem.decode('utf8').replace("'", '"')
    request["data"]["message"] = ""
    request["data"]["status"] = 0
    request.update({
        "response": {
            "public": pu_key_pem.decode('utf8').replace("'", '"'),
            "message": "",
            "status": 0
        }
    })
    msg_queue.put(request)


@task
def get_config_properties(request, db=None,md=None, msg_queue=None):
    request.update({
        "data": {
            "properties": shared_objects.config,
            "message": "",
            "status": 0
        }
    })
    msg_queue.put(request)


@task
def verify_user_password(request, onaa=None, md=None, docbook=None, msg_queue=None):
    if request["uuid"] in keys:
        request.update({
            "data": verify_password(keys[request["uuid"]], request["username"], request["password"])
        })
    else:
        request.update({
            "data": {
                "status": 1,
                "message":
                    "Session Expired!"
            }
        })
    msg_queue.put(request)


@task
def get_personnel_records(request, db=None, md=None, docbook=None, msg_queue=None):
    db.get_personnel_records(request)
    msg_queue.put(request)


@task
def get_personnel_with_metadata(request, db=None, md=None, docbook=None, msg_queue=None):
    db.get_personnel_with_metadata(request)
    msg_queue.put(request)


@task
def update_personnel_metadata(request, db=None, md=None, docbook=None, msg_queue=None):
    db.update_personnel_metadata(request)
    msg_queue.put(request)


@task
def get_personnel_metadata(request, db=None, md=None, docbook=None, msg_queue=None):
    db.get_personnel_metadata(request)
    msg_queue.put(request)


@task
def update_personnel_record(request, db=None, md=None, docbook=None, msg_queue=None):
    db.update_personnel_record(request)
    msg_queue.put(request)


@task
def permanently_delete_person(request, db=None, md=None, docbook=None, msg_queue=None):
    db.permanently_delete_person(request)
    msg_queue.put(request)


@task
def get_system_properties(request, db=None, md=None, docbook=None, msg_queue=None):
    db.get_system_properties(request)
    msg_queue.put(request)


@task
def set_system_property(request, db=None, md=None, docbook=None, msg_queue=None):
    db.set_system_property(request)
    msg_queue.put(request)


@task
def get_manufacturer_records(request, db=None, md=None, docbook=None, msg_queue=None):
    db.get_manufacturer_records(request)
    msg_queue.put(request)


@task
def save_manufacturer_record(request, db=None, md=None, docbook=None, msg_queue=None):
    db.save_manufacturer_record(request)
    msg_queue.put(request)


@task
def get_storage_records(request, db=None, md=None, docbook=None, msg_queue=None):
    db.get_storage_records(request)
    msg_queue.put(request)


@task
def save_storage_record(request, db=None, md=None, docbook=None, msg_queue=None):
    db.save_storage_record(request)
    msg_queue.put(request)


@task
def get_material_records(request, db=None, md=None, docbook=None, msg_queue=None):
    db.get_material_records(request)
    msg_queue.put(request)


@task
def save_material_record(request, db=None, md=None, docbook=None, msg_queue=None):
    db.save_material_record(request)
    msg_queue.put(request)


@task
def get_glossary_terms(request, db=None, md=None, docbook=None, msg_queue=None):
    db.get_glossary_terms(request)
    msg_queue.put(request)


@task
def generate_personnel_records_pdf(request, db=None, md=None, docbook=None, msg_queue=None):
    db.generate_personnel_records_pdf(request)
    docbook.generate_personnel_records_pdf(request)
    msg_queue.put(request)


@task
def generate_controlled_materials_list_pdf(request, db=None, md=None, docbook=None, msg_queue=None):
    db.generate_controlled_materials_list_pdf(request)
    _request = {}
    db.get_system_properties(_request)
    request.update({
        "system_properties": _request["response"]["properties"]
    })
    _request = {}
    db.get_manufacturer_records(_request)
    request.update({
        "manufacturers": _request["response"]["manufacturers"]
    })
    _request = {}
    db.get_storage_records(_request)
    request.update({
        "storage_locations": _request["response"]["storage_locations"]
    })
    docbook.generate_controlled_materials_list_pdf(request)
    msg_queue.put(request)


@task
def test_client(request, db=None, msg_queue=None):
    request.update({
        "data": {
            "ok": "yes",
            "message": "",
            "status": 0
        }
    })
    msg_queue.put(request)


@task
def broadcast_response(request, onaa=None, msg_queue=None):
    print("BROADCAST RESPONSE", request)
    if "recipient" in request:
        # forward request to recipient
        msg_queue.put(request)
