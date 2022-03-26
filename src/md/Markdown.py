from .utils import get_record_metadata, get_property_value_as_dict, get_controlled_material_types
from .Constants.Constants import CHECKBOX, BLANK_CHECKBOX
from .md2pdf import md2pdf
from .hr_markdown import generate_personnel_records_md
from .cm_markdown import generate_restricted_controlled_materials_list_md, generate_unrestricted_controlled_materials_list_md

import base64
import os
import tempfile


class Markdown:
    """ Markdown base class. """

    def __init__(self, config=None, log=None):
        self._config = config
        self._log = log

    def generate_personnel_records_pdf(self, request):
        md_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".md")
        pdf_file = tempfile.NamedTemporaryFile(mode="r+b", suffix=".pdf")
        generate_personnel_records_md(request, md_file)
        md2pdf(pdf_file.name,
               md_file_path=md_file.name,
               css_file_path=os.path.join(os.path.join(self._config["path"]), "input.css"),
               base_url=None)
        data = open(pdf_file.name, "rb").read()
        encoded = base64.b64encode(data)
        # print(encoded)

        request.update({
               "data": {
                      "pdf": "data:application/pdf;base64,{}".format(encoded.decode()),
                      "message": "",
                      "status": 0
               }
        })

    def generate_controlled_materials_list_pdf(self, request):
        print("==================")
        # print(self._config)
        # print(self._config["path"])
        # print(os.path.join(self._config["path"], "input.md"))
        print(request)
        print("==================")
        access = request["access"] if "access" in request else "restricted"
        # create temporary markdown file
        html_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".html")
        pdf_file = tempfile.NamedTemporaryFile(mode="r+b", suffix=".pdf")
        print("PDF FILE: {}".format(pdf_file.name))
        # get material types as dictionary from system properties
        material_types_dict = get_property_value_as_dict(request["system_properties"], "nurims.material.type", {})
        # get material types
        material_types = get_controlled_material_types(request, material_types_dict)
        print("-----------")
        print(material_types_dict)
        print(material_types)
        if access == "restricted":
            generate_restricted_controlled_materials_list_md(request, html_file, material_types_dict=material_types_dict, material_types=material_types)
        # else:
        #     _generate_unrestricted_controlled_materials_list_md(request, md_file)
        md2pdf(pdf_file.name,
               # md_content='./input.md',
               # md_file_path=md_file.name,
               # md_file_path=os.path.join(os.path.join(self._config["path"]), "toc.html"),
               html_file_path=os.path.join(os.path.join(self._config["path"]), "toc.html"),
               css_file_path=os.path.join(os.path.join(self._config["path"]), "toc.css"),
               base_url=None)
        data = open(pdf_file.name, "rb").read()
        encoded = base64.b64encode(data)
        # print(encoded)

        request.update({
               "data": {
                      "pdf": "data:application/pdf;base64,{}".format(encoded.decode()),
                      "message": "",
                      "status": 0
               }
        })
