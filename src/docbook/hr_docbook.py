import io
import datetime

from .utils import get_record_metadata, get_record_metadata_as_dict
from .Constants.Constants import CHECKBOX, BLANK_CHECKBOX, HIGHLIGHT_BGCOLOR


def generate_personnel_records_xml(request, xml_template_file):
    xml = io.StringIO()
    if "response" in request and "personnel" in request["response"]:
        for person in request["response"]["personnel"]:
            name = person["nurims.title"]
            withdrawn = person["nurims.withdrawn"]
            gender = get_record_metadata(person, "nurims.entity.sex", "&nbsp;")
            iswholebodymonitored = True if get_record_metadata(person, "nurims.entity.iswholebodymonitored", "false") == "true" else False
            isextremitymonitored = True if get_record_metadata(person, "nurims.entity.isextremitymonitored", "false") == "true" else False
            iswristmonitored = True if get_record_metadata(person, "nurims.entity.iswristmonitored", "false") == "true" else False
            dob = get_record_metadata(person, "nurims.entity.dob", "&nbsp;")
            nid = get_record_metadata(person, "nurims.entity.nid", "&nbsp;")
            work_details = get_record_metadata(person, "nurims.entity.workdetails", "&nbsp;")
            contact = get_record_metadata(person, "nurims.entity.contact", "&nbsp;")
            address = get_record_metadata(person, "nurims.entity.address", "&nbsp;")
            avatar = get_record_metadata(person, "nurims.entity.avatar", "&nbsp;")

            xml.write("<?hard-pagebreak?>")
            xml.write("<section><title>{}</title>".format(name))
            xml.write("<informaltable frame='all'>")
            xml.write("<tgroup cols='5' align='left' colsep='0' rowsep='0'>")
            xml.write("<colspec colname='c1' align='right' colwidth='2*' />")
            xml.write("<colspec colname='c2' align='left' colwidth='5*' />")
            xml.write("<colspec colname='c3' align='center' colwidth='1*' />")
            xml.write("<colspec colname='c4' align='center' colwidth='1*' />")
            xml.write("<colspec colname='c5' align='center' colwidth='1*' />")
            xml.write("<tbody>")
            xml.write("<row><entry align='center' namest='c1' nameend='c5'>{}<emphasis role='strong'>Details</emphasis></entry></row>".format(HIGHLIGHT_BGCOLOR))
            xml.write("<row>")
            xml.write("<entry> &nbsp; </entry>")
            xml.write("<entry> &nbsp; </entry>")
            xml.write("<entry>Whole Body <?linebreak?> Monitoring</entry>")
            xml.write("<entry>Ring <?linebreak?> Monitoring</entry>")
            xml.write("<entry>Wrist <?linebreak?> Monitoring</entry>")
            xml.write("</row>")
            xml.write("<row>")
            xml.write("<entry>Name: </entry>")
            xml.write("<entry>{}</entry>".format(name))
            xml.write("<entry>{}</entry>".format(CHECKBOX if iswholebodymonitored else BLANK_CHECKBOX))
            xml.write("<entry>{}</entry>".format(CHECKBOX if isextremitymonitored else BLANK_CHECKBOX))
            xml.write("<entry>{}</entry>".format(CHECKBOX if iswristmonitored else BLANK_CHECKBOX))
            xml.write("</row>")
            xml.write("<row>")
            xml.write("<entry>Status: </entry>")
            xml.write("<entry namest='c2' nameend='c5'>{}</entry>".format("INACTIVE" if withdrawn == 1 else "ACTIVE"))
            xml.write("</row>")
            xml.write("<row>")
            xml.write("<entry>Gender: </entry>")
            xml.write("<entry namest='c2' nameend='c5'>{}</entry>".format("Male" if gender == "m" else "Female" if gender == "f" else gender))
            xml.write("</row>")
            xml.write("<row>")
            xml.write("<entry>Date Of Birth: </entry>")
            xml.write("<entry namest='c2' nameend='c5'>{}</entry>".format(dob))
            xml.write("</row>")
            xml.write("<row>")
            xml.write("<entry>National ID: </entry>")
            xml.write("<entry namest='c2' nameend='c5'>{}</entry>".format(nid))
            xml.write("</row>")
            xml.write("<row>")
            xml.write("<entry>Address: </entry>")
            xml.write("<entry namest='c2' nameend='c5'>{}</entry>".format(address))
            xml.write("</row>")
            xml.write("<row>")
            xml.write("<entry>Work: </entry>")
            xml.write("<entry namest='c2' nameend='c5'>{}</entry>".format(work_details))
            xml.write("</row>")
            xml.write("<row>")
            xml.write("<entry>Contact: </entry>")
            xml.write("<entry namest='c2' nameend='c5'>{}</entry>".format(contact))
            xml.write("</row>")
            xml.write("<row>")
            xml.write("<entry>Avatar: </entry>")
            xml.write("<entry namest='c2' nameend='c5'>")
            xml.write("<imagedata width='2.5in' scalefit='1' contentdepth='100%' fileref='{}'></imagedata>".format(avatar))
            xml.write("</entry>")
            xml.write("</row>")
            xml.write("<row><entry align='center' namest='c1' nameend='c5'> <?linebreak?> </entry></row>")
            xml.write("<row><entry align='center' namest='c1' nameend='c5'>{}<emphasis role='strong'>Roles</emphasis></entry></row>".format(HIGHLIGHT_BGCOLOR))
            xml.write("<row><entry align='center' namest='c1' nameend='c5'> <?linebreak?> </entry></row>")
            xml.write("<row><entry align='center' namest='c1' nameend='c5'>{}<emphasis role='strong'>Training Programmes</emphasis></entry></row>".format(HIGHLIGHT_BGCOLOR))
            xml.write("<row><entry align='center' namest='c1' nameend='c5'> <?linebreak?> </entry></row>")
            xml.write("</tbody>")
            xml.write("</tgroup>")
            xml.write("</informaltable>")
            xml.write("</section>")

    xml_template = ''
    with open(xml_template_file) as f:
        xml_template = f.read()

    xml_template = xml_template.replace('__PERSONNEL_TABLES__', xml.getvalue())
    xml_template = xml_template.replace('__REPORT_DATE__', datetime.datetime.now().isoformat().replace("T", " ")[0:10])
    xml_template = xml_template.replace('__PUBLISHER__', "ICENS")
    xml_template = xml_template.replace('__ADDRESS__', " ")
    xml_template = xml_template.replace('__ADDRESS1__', " ")

    xml.close()

    return xml_template


