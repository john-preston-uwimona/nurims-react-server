
def get_record_metadata(record, field, missing):
    if "metadata" in record:
        for m in record["metadata"]:
            if field in m:
                return m[field]
    return missing


def _append_list(_list, elem):
    if elem in _list:
        return
    _list.append(elem)


def get_property_value_as_dict(properties, name, missing={}):
    nv = {"unknown": "Unknown"}
    for p in properties:
        if p["name"] == name:
            values = p["value"].split("|")
            for v in values:
                kv = v.split(",")
                nv[kv[0]] = kv[1]
            return nv

    return missing


def get_controlled_material_types(request, properties_dict={}):
    material_types = []
    if "response" in request and "materials" in request["response"]:
        for material in request["response"]["materials"]:
            if "metadata" in material:
                metadata = material["metadata"]
                found = False
                for m in metadata:
                    if "nurims.material.type" in m:
                        _append_list(material_types, m["nurims.material.type"])
                        found = True
                if not found:
                    _append_list(material_types, "unknown")
            else:
                _append_list(material_types, "unknown")

    return material_types
