import io
import datetime

from .utils import get_record_metadata, get_record_metadata_as_dict, get_item_record
from .Constants.Constants import CHECKBOX, BLANK_CHECKBOX, HIGHLIGHT_BGCOLOR


def generate_controlled_materials_list_xml(request, xml_template_file, access="restricted",
                                           material_types_dict=None, material_types=None,
                                           manufacturers_dict=None, physical_form_dict=None,
                                           classification_dict=None, inventory_status_dict=None,
                                           storage_locations_dict=None, surveillance_frequency_dict=None,
                                           nuclides_dict=None, quantity_units_dict=None):
    xml = io.StringIO()
    if "response" in request and "materials" in request["response"]:

        for material_type in material_types:
            xml.write("<?hard-pagebreak?>")
            xml.write("<section><title>{}</title>".format(material_types_dict[material_type]))
            for material in request["response"]["materials"]:
                record_material_type = get_record_metadata(material, "nurims.material.type", "unknown")
                if record_material_type == material_type:
                    name = material["nurims.title"]
                    id = get_record_metadata(material, "nurims.material.id", "")
                    description = get_record_metadata(material, "nurims.description", "")
                    manufacturer_name, manufacturer_address, manufacturers_contact =\
                        get_item_record(manufacturers_dict, get_record_metadata(material, "nurims.material.manufacturer", 0))
                    storage_name, storage_address, storage_contact =\
                        get_item_record(storage_locations_dict, get_record_metadata(material, "nurims.material.storagelocation", 0))
                    registration_date = get_record_metadata(material, "nurims.material.registrationdate", "1970-01-01")
                    physical_form = get_record_metadata(material, "nurims.material.physicalform", "unknown")
                    classification = get_record_metadata(material, "nurims.material.classification", "unknown")
                    inventory_status = get_record_metadata(material, "nurims.material.inventorystatus", "unknown")
                    inventory_surveillance_frequency = get_record_metadata(material, "nurims.inventorysurveillancefrequency", "unknown")
                    activity_surveillance_frequency = get_record_metadata(material, "nurims.activitysurveillancefrequency", "unknown")
                    leaktest_surveillance_frequency = get_record_metadata(material, "nurims.leaktestsurveillancefrequency", "unknown")
                    avatar = get_record_metadata_as_dict(material, "nurims.material.image", {})
                    nuclides = get_record_metadata_as_dict(material, "nurims.material.nuclides", [])

                    xml.write("<section><title>{} : {}</title>".format(id, name))
                    xml.write("<informaltable frame='all'>")
                    xml.write("<tgroup cols='4' align='center'>")
                    xml.write("<colspec colname='c1' align='right' />")
                    xml.write("<colspec colname='c2' />")
                    xml.write("<colspec colname='c3' />")
                    xml.write("<colspec colname='c4' />")
                    xml.write("<tbody>")
                    xml.write("<row>")
                    xml.write("<entry>Name :</entry>")
                    xml.write("<entry align='left' namest='c2' nameend='c3'>{}</entry>".format(name))
                    xml.write("<entry align='center' morerows='9'><imagedata width='100%' scalefit='1' contentdepth='100%' fileref='{}'></imagedata></entry>".format(
                        avatar["url"] if "url" in avatar else "&nbsp;"))
                    xml.write("</row>")
                    xml.write("<row>")
                    xml.write("<entry>ID :</entry>")
                    xml.write("<entry align='left' namest='c2' nameend='c3'>{}</entry>".format(id))
                    xml.write("</row>")
                    xml.write("<row>")
                    xml.write("<entry>Description :</entry>")
                    xml.write("<entry align='left' namest='c2' nameend='c3'>{}</entry>".format(description))
                    xml.write("</row>")
                    xml.write("<row>")
                    xml.write("<entry>Manufacturer :</entry>")
                    xml.write("<entry align='left' namest='c2' nameend='c3'>{}<?linebreak?>{}<?linebreak?>{}<?linebreak?></entry>".format(
                        manufacturer_name, manufacturer_address, manufacturers_contact))
                    xml.write("</row>")
                    xml.write("<row>")
                    xml.write("<entry>Registration Date :</entry>")
                    xml.write("<entry align='left' namest='c2' nameend='c3'>{}</entry>".format(registration_date))
                    xml.write("</row>")
                    xml.write("<row>")
                    xml.write("<entry>Physical Form :</entry>")
                    xml.write("<entry align='left' namest='c2' nameend='c3'>{}</entry>".format(physical_form_dict[physical_form]))
                    xml.write("</row>")
                    xml.write("<row>")
                    xml.write("<entry>Classification :</entry>")
                    xml.write("<entry align='left' namest='c2' nameend='c3'>{}</entry>".format(classification_dict[classification]))
                    xml.write("</row>")
                    xml.write("<row>")
                    xml.write("<entry>Inventory Status :</entry>")
                    xml.write("<entry align='left' namest='c2' nameend='c3'>{}</entry>".format(inventory_status_dict[inventory_status]))
                    xml.write("</row>")
                    xml.write("<row>")
                    xml.write("<entry>Storage Location :</entry>")
                    xml.write("<entry align='left' namest='c2' nameend='c3'>{}</entry>".format(storage_name if access == "restricted" else "-"))
                    xml.write("</row>")
                    xml.write("<row>")
                    xml.write("<entry>Surveillance :</entry>")
                    xml.write("<entry align='left' namest='c2' nameend='c3'>Inventory: {}<?linebreak?>Leak Testing: {}<?linebreak?>Activity Testing: {}</entry>".format(
                        surveillance_frequency_dict[inventory_surveillance_frequency],
                        surveillance_frequency_dict[leaktest_surveillance_frequency],
                        surveillance_frequency_dict[activity_surveillance_frequency]))
                    xml.write("</row>")
                    if material_type != "controlled_item":
                        xml.write("<row>")
                        xml.write("<entry morerows='{}'>Nuclides :</entry>".format(len(nuclides)))
                        xml.write("<entry align='center'>{}Nuclide</entry>".format(HIGHLIGHT_BGCOLOR))
                        xml.write("<entry align='center'>{}Activity/Quantity</entry>".format(HIGHLIGHT_BGCOLOR))
                        xml.write("<entry align='center'>{}Ref. Date</entry>".format(HIGHLIGHT_BGCOLOR))
                        xml.write("</row>")
                        for n in nuclides:
                            xml.write("<row>")
                            xml.write("<entry align='center'>{}</entry>".format(
                                nuclides_dict[n["nuclide"]] if access == "restricted" else "-"))
                            xml.write("<entry align='center'>{}</entry>".format(
                                "{} {}".format(n["quantity"], quantity_units_dict[n["units"]]) if access == "restricted" else "-"))
                            xml.write("<entry align='center'>{}</entry>".format(
                                n["date"] if access == "restricted" else "-"))
                            xml.write("</row>")
                    xml.write("</tbody>")
                    xml.write("</tgroup>")
                    xml.write("</informaltable>")
                    xml.write("</section>")
                    xml.write("<?hard-pagebreak?>")
            xml.write("</section>")

        # storage location section if restricted access
        if access == "restricted":
            xml.write("<section><title>Storage Locations</title>")
            for location in storage_locations_dict:
                location_name = location["nurims.title"]
                location_description = get_record_metadata(location, "nurims.description", "&nbsp;")
                xml.write("<section><title>{}</title>".format(location_name))
                xml.write("<para>{}</para>".format(location_description))
                xml.write("</section>")
                xml.write("<?hard-pagebreak?>")
            xml.write("</section>")

    xml_template = ''
    with open(xml_template_file) as f:
        xml_template = f.read()

    xml_template = xml_template.replace('__CONTROLLED_MATERIAL_TABLES__', xml.getvalue())
    xml_template = xml_template.replace('__REPORT_DATE__', datetime.datetime.now().isoformat().replace("T", " ")[0:10])
    xml_template = xml_template.replace('__PUBLISHER__', "ICENS")
    xml_template = xml_template.replace('__ADDRESS__', " ")
    xml_template = xml_template.replace('__ADDRESS1__', " ")

    xml.close()

    return xml_template


