import base64
import os
import tempfile
import subprocess

from .utils import get_record_metadata, get_property_value_as_dict, get_controlled_material_types
from .Constants.Constants import CHECKBOX, BLANK_CHECKBOX
from .docbook2pdf import docbook2pdf
from .hr_docbook import generate_personnel_records_xml
from .cm_docbook import generate_controlled_materials_list_xml


class Docbook:
    """ Docbook base class. """

    def __init__(self, config=None, pdf_path=["./"], log=None):
        self.config = config
        self.pdf_path = pdf_path
        self.log = log

    def _get_file_path(self, relative_path):
        return os.path.join(self.config["path"], relative_path)

    def generate_personnel_records_pdf(self, request):
        pdf_file = tempfile.NamedTemporaryFile(mode="r+b", suffix=".pdf", delete=False, dir=self.pdf_path["path"])
        # print("PDF PATH", self.pdf_path)
        # print("PDF FILE", pdf_file.name)
        xslt_file = self._get_file_path("stylesheets/fo/custom_personnel_records_docbook.xsl")
        xml = generate_personnel_records_xml(
            request,
            self._get_file_path("templates/personnel_records_list.xml")
        )

        # write to temporary file
        xml_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".xml")
        xml_file.write(xml)
        xml_file.flush()

        try:
            docbook2pdf(pdf_file.name,
                        docbook_xml_file=xml_file.name,
                        xslt_file=xslt_file,
                        log=self.log)
            pdf_file.close()
            head, tail = os.path.split(pdf_file.name)
            request.update({
                "data": {
                    "pdf": "/{}/{}".format(self.pdf_path["link"], tail),
                    "message": "",
                    "status": 0
                }
            })
            # data = open(pdf_file.name, "rb").read()
            # encoded = base64.b64encode(data)
            # request.update({
            #     "data": {
            #         "pdf": "data:application/pdf;base64,{}".format(encoded.decode()),
            #         "message": "",
            #         "status": 0
            #     }
            # })
        except subprocess.CalledProcessError as e:
            if self.log:
                self.log.error(e.stderr)
            request.update({
                   "data": {
                          "pdf": "",
                          "message": "{}".format(e),
                          "status": 1
                   }
            })
        except ValueError as e:
            if self.log:
                self.log.error(e)
            request.update({
                   "data": {
                          "pdf": "",
                          "message": "{}".format(e),
                          "status": 1
                   }
            })

    def generate_controlled_materials_list_pdf(self, request):
        access = request["access"] if "access" in request else "restricted"
        # get manufacturers
        manufacturers_dict = request["manufacturers"]
        # get storage locations
        storage_locations_dict = request["storage_locations"]
        # get surveillance frequency as dictionary from system properties
        surveillance_frequency_dict = get_property_value_as_dict(request["system_properties"], "nurims.surveillancefrequency", {})
        # get nuclides as dictionary from system properties
        nuclides_dict = get_property_value_as_dict(request["system_properties"], "nurims.material.nuclides", {})
        # get quantity units as dictionary from system properties
        quantity_units_dict = get_property_value_as_dict(request["system_properties"], "nurims.material.quantityunits", {})
        # get material types as dictionary from system properties
        material_types_dict = get_property_value_as_dict(request["system_properties"], "nurims.material.type", {})
        # get physical forms as dictionary from system properties
        physical_form_dict = get_property_value_as_dict(request["system_properties"], "nurims.material.physicalform", {})
        # get material classification as dictionary from system properties
        classification = get_property_value_as_dict(request["system_properties"], "nurims.material.classification", {})
        # get inventory status as dictionary from system properties
        inventory_status = get_property_value_as_dict(request["system_properties"], "nurims.material.inventorystatus", {})
        # get material types
        material_types = get_controlled_material_types(request, material_types_dict)
        # print("-----------")
        # print(material_types_dict)
        # print(material_types)
        # print(material_types)
        # print(manufacturers_dict)
        # print("-----------")
        pdf_file = tempfile.NamedTemporaryFile(mode="r+b", suffix=".pdf", delete=False, dir=self.pdf_path["path"])
        # print("PDF PATH", self.pdf_path)
        # print("PDF FILE", pdf_file.name)
        xslt_file = self._get_file_path("stylesheets/fo/custom_controlled_materials_docbook.xsl")
        # xml = generate_restricted_controlled_materials_list_xml(request, )
        xml = generate_controlled_materials_list_xml(
            request,
            self._get_file_path("templates/controlled_materials_list.xml"),
            access=access,
            material_types_dict=material_types_dict,
            physical_form_dict=physical_form_dict,
            classification_dict=classification,
            inventory_status_dict=inventory_status,
            material_types=material_types,
            manufacturers_dict=manufacturers_dict,
            storage_locations_dict=storage_locations_dict,
            surveillance_frequency_dict=surveillance_frequency_dict,
            nuclides_dict=nuclides_dict,
            quantity_units_dict=quantity_units_dict
        )

        # write to temporary file
        xml_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".xml")
        xml_file.write(xml)
        xml_file.flush()

        try:
            docbook2pdf(pdf_file.name,
                        docbook_xml_file=xml_file.name,
                        xslt_file=xslt_file,
                        log=self.log)
            pdf_file.close()
            head, tail = os.path.split(pdf_file.name)
            request.update({
                "data": {
                    "pdf": "/{}/{}".format(self.pdf_path["link"], tail),
                    "message": "",
                    "status": 0
                }
            })
            # data = open(pdf_file.name, "rb").read()
            # encoded = base64.b64encode(data)
            # request.update({
            #     "data": {
            #         "pdf": "data:application/pdf;base64,{}".format(encoded.decode()),
            #         "message": "",
            #         "status": 0
            #     }
            # })
        except subprocess.CalledProcessError as e:
            if self.log:
                self.log.error(e.stderr)
            request.update({
                   "data": {
                          "pdf": "",
                          "message": "{}".format(e),
                          "status": 1
                   }
            })
        except ValueError as e:
            if self.log:
                self.log.error(e)
            request.update({
                   "data": {
                          "pdf": "",
                          "message": "{}".format(e),
                          "status": 1
                   }
            })
