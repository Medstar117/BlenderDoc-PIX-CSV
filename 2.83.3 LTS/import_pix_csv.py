# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import bpy
import csv
import mathutils
from collections import OrderedDict
from bpy_extras.io_utils import axis_conversion
from bpy.props import BoolProperty, StringProperty, EnumProperty

bl_info = {
           "name": "BlenderDoc PIX CSV",
           "author": "Medstar, Stanislav Bobovych",
           "version": (1, 0, 2),
           "blender": (2, 80, 0),
           "location": "File > Import-Export",
           "description": "Import PIX CSV data from RenderDoc. Imports meshes, normals, UV's.",
           "category": "Import",
           }

class PIX_CSV_Operator(bpy.types.Operator):

    # Plugin definitions, such as ID, name, and file extension filters
    bl_idname = "object.pix_csv_importer"
    bl_label = "Import PIX CSV"
    filepath = StringProperty(subtype = "FILE_PATH")
    filter_glob = StringProperty(default = "*.csv", options = {"HIDDEN"})

    # Options for generation of vertices
    mirror_x = BoolProperty(
                            name = "Mirror X",
                            description = "Mirror all the vertices across X axis",
                            default = False,
                            )

    vertex_order = BoolProperty(
                                name = "Change vertex order",
                                description = "Reorder vertices in counter-clockwise order",
                                default = False,
                                )

    # Options for axis alignment
    axis_forward = EnumProperty(
                                name = "Forward",
                                items = (
                                         ('X', "X Forward", ""),
                                         ('Y', "Y Forward", ""),
                                         ('Z', "Z Forward", ""),
                                         ('-X', "-X Forward", ""),
                                         ('-Y', "-Y Forward", ""),
                                         ('-Z', "-Z Forward", ""),
                                         ),
                                default = 'Z',
                                )

    axis_up = EnumProperty(
                           name = "Up",
                           items = (
                                    ('X', "X Up", ""),
                                    ('Y', "Y Up", ""),
                                    ('Z', "Z Up", ""),
                                    ('-X', "-X Up", ""),
                                    ('-Y', "-Y Up", ""),
                                    ('-Z', "-Z Up", ""),
                                    ),
                           default = 'Y',
                           )


# ~~~~~~~~~~~~~~~~~~~~Operator Functions~~~~~~~~~~~~~~~~~~~~
    def execute(self, context):
        keywords = self.as_keywords(ignore = ("axis_forward", "axis_up", "filter_glob"))
        global_matrix = axis_conversion(from_forward = self.axis_forward, from_up = self.axis_up).to_4x4()

        keywords["global_matrix"] = global_matrix
        importCSV(**keywords)

        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text = "Import Options")

        row = col.row()
        row.prop(self, "mirror_x")
        row = col.row()
        row.prop(self, "vertex_order")
        layout.prop(self, "axis_forward")
        layout.prop(self, "axis_up")


# ~~~~~~~~~~~~~~~~~~~~Mesh-Related Functions~~~~~~~~~~~~~~~~~~~~
def make_mesh(vertices, faces, normals, uvs, global_matrix):

    # Create a new mesh from the vertices and faces
    mesh = bpy.data.meshes.new("Imported Mesh")
    mesh.from_pydata(vertices, [], faces)

    # Generate normals
    index = 0
    for vertex in mesh.vertices:
        vertex.normal = normals[index]
        index += 1

    # Generate UV data
    uv_layer = mesh.uv_layers.new(name = "UVMap")
    for face, uv in enumerate(uv_layer.data): uv.uv = uvs[face]

    mesh.update(calc_edges = False)

    obj = bpy.data.objects.new("Imported Mesh", mesh)    # Create the mesh object for the imported mesh
    obj.matrix_world = global_matrix                     # Apply transformation matrix
    bpy.context.collection.objects.link(obj)             # Link object to scene


def importCSV(filepath = None, mirror_x = False, vertex_order = True, global_matrix = None):

    # Translates coordinates of things to the global space by ensuring that there's a global matrix to use
    if global_matrix is None: global_matrix = mathutils.Matrix()

    # Check if a valid filepath was given; if nothing was given, cancel the import
    if filepath == None: return

    # Dictionaries
    vertex_dict = {}
    normal_dict = {}

    # Arrays/Lists
    vertices = []
    faces = []
    normals = []
    uvs = []

    with open(filepath) as f:

        # Create the CSV reader and set which column is what data
        reader = csv.reader(f)              # Initialize the reader
        csv_header = next(reader)           # Get the header of the CSV file
        header_dict = {"VTX": 0, "IDX": 1}  # These two values will always appear at these positions in a row list

        # Dynamically assign which column index is for what component; also strips any spaces in the header
        for index in range(2, len(csv_header)):
            header = csv_header[index].split(" ")
            header_dict.update({header[1]: index})

        # Check if user wants vertices to be mirrored on the X-axis
        if mirror_x: x_mod = -1
        else: x_mod = 1

        # For-Loop variables
        i = 0
        current_face = []

        for row in reader: # TODO: Make dynamic searching for different vertex sections
            vertex_index = int(row[header_dict["VTX"]])

            # X, Y, Z coordinates of vertices
            vertex_dict[vertex_index] = (
                                         x_mod * float(row[header_dict["a_Position0.x"]]),
                                                 float(row[header_dict["a_Position0.y"]]),
                                                 float(row[header_dict["a_Position0.z"]]),
                                         )

            # TODO: How are axises really ligned up?
            normal_dict[vertex_index] = (
                                         float(row[header_dict["a_Normal0.x"]]),
                                         float(row[header_dict["a_Normal0.y"]]),
                                         float(row[header_dict["a_Normal0.z"]]),
                                         )

            # TODO: Add support for changing the origin of UV coords
            uv = (
                  float(row[header_dict["a_TexCoord0.x"]]),
                  float(row[header_dict["a_TexCoord0.y"]]),
                  )

            if i < 2:
                # Append "current" data to list/array until a 3-vertex face is formed
                current_face.append(vertex_index)
                uvs.append(uv)
                i += 1
            else:
                # Append face and UV data to appropriate dictionary/array/list
                current_face.append(vertex_index)
                # TODO: add option to change order of marching vertices
                if vertex_order: faces.append((current_face[2], current_face[1], current_face[0]))
                else: faces.append(current_face)
                uvs.append(uv)

                # Clear For-Loop variables for next iteration
                current_face = []
                i = 0

        # Zero out any missing vertices/normals
        for i in range(len(vertex_dict)):
            if i in vertex_dict:
                pass
            else:
                vertex_dict[i] = (0, 0, 0)
                normal_dict[i] = (0, 0, 0)

        # Dictionary sorted by key
        vertex_dict = OrderedDict(sorted(vertex_dict.items(), key = lambda t: t[0]))
        normal_dict = OrderedDict(sorted(normal_dict.items(), key = lambda t: t[0]))

        for key in vertex_dict: vertices.append(list(vertex_dict[key]))
        for key in normal_dict: normals.append(list(normal_dict[key]))

        make_mesh(vertices, faces, normals, uvs, global_matrix)


# ~~~~~~~~~~~~~~~~~~~~Registration Functions~~~~~~~~~~~~~~~~~~~~
classes = (PIX_CSV_Operator,)

def menu_func_import(self, context):
    self.layout.operator(PIX_CSV_Operator.bl_idname, text = "RenderDoc PIX CSV (.csv)")

def register():
    for cls in classes: bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    for cls in reversed(classes): bpy.utils.unregister_class(cls)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


# ~~~~~~~~~~~~~~~~~~~~MAIN Block~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
    #register()                                             # Uncomment this to run as a plugin
    #These run the script from "Run script" button
    bpy.utils.register_class(PIX_CSV_Operator)              # Comment this to run as a plugin
    bpy.ops.object.pix_csv_importer('INVOKE_DEFAULT')       # Comment this to run as a plugin
