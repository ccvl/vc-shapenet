#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
This is modified from
RenderForCNN/render_pipeline/render_model_views.py by Weichao
to enable explictly control of lighting, to see the modification
use git diff.
'''

'''
RENDER_MODEL_VIEWS.py
brief:
    render projections of a 3D model from viewpoints specified by an input parameter file
usage:
	blender blank.blend --background --python render_model_views.py -- <shape_obj_filename> <shape_category_synset> <shape_model_md5> <shape_view_param_file> <syn_img_output_folder>

inputs:
       <shape_obj_filename>: .obj file of the 3D shape model
       <shape_category_synset>: synset string like '03001627' (chairs)
       <shape_model_md5>: md5 (as an ID) of the 3D shape model
       <shape_view_params_file>: txt file - each line is '<azimith angle> <elevation angle> <in-plane rotation angle> <distance>'
       <syn_img_output_folder>: output folder path for rendered images of this model

author: hao su, charles r. qi, yangyan li
'''
#import sys
#sys.path.append('.')
#from share.py import color
import pickle
#color = pickle.load( open( "color_map.p", "rb"))
import os
import bpy
import sys
import math
import random
import numpy as np
import mathutils
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix
from mathutils import Vector
division = 5 # 5*5*5


#bpy.context.user_preferences.system.compute_device_type = 'CUDA'
#bpy.context.user_preferences.system.compute_device = 'CUDA_1'

# Load rendering light parameters
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dep_paths = [
	BASE_DIR,
	os.path.join(BASE_DIR, 'rendercnn')
]
for p in dep_paths:
	sys.path.append(p)
sys.stdout.flush()
from global_variables import *
import render_opt as opt

def setObjectPaintMode(obj):
    def setMaterialPaintMode(material):
        if material:
            material.use_shadeless = True
            material.use_vertex_color_paint = True
            material.use_transparency = False
            for i in range(len(material.use_textures)):
                material.use_textures[i] = False
        else:
            print('Material not available')
    #----
    if obj:
        if len(obj.material_slots.items()) == 0:
            print('No material is defined for object: %s' % obj.name)
        for slot in obj.material_slots:
            setMaterialPaintMode(slot.material)
    else:
        print('Enable paint mode: Object not exist')
def find_connected_verts(obj, found_index):
    edges = obj.data.edges
    # connecting_edges = []
    # for edge in edges:
    #     #print('vertices',found_index, edge.vertices)
    #     for vert in edge.vertices:
    #         if vert == found_index:
    #             connecting_edges.append(edge)
    #             continue
    connecting_edges = [i for i in edges if found_index in i.vertices[:]]
    if len(connecting_edges) < 2:
        return None
    else:
        connected_verts = []
        for edge in connecting_edges:
            cvert = set(edge.vertices[:])
            cvert.remove(found_index)
            connected_verts.append(cvert.pop())

        return connected_verts

def color_vertex(obj, vert, color):
    """Paints a single vertex where vert is the index of the vertex
    and color is a tuple with the RGB values."""
    mesh = obj.data
    scn = bpy.context.scene
    #check if our mesh already has Vertex Colors, and if not add some... (first we need to make sure it's the active object)
    scn.objects.active = obj
    obj.select = True
    if mesh.vertex_colors:
        vcol_layer = mesh.vertex_colors.active
    else:
        vcol_layer = mesh.vertex_colors.new()
    for poly in mesh.polygons:
        for loop_index in poly.loop_indices:
            loop_vert_index = mesh.loops[loop_index].vertex_index
            if vert == loop_vert_index:
                vcol_layer.data[loop_index].color = color
#example usage
def makeMaterial(name, diffuse, specular, alpha):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = diffuse
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = specular
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 0.5
    mat.alpha = alpha
    mat.ambient = 1
    return mat
def setMaterial(ob, mat):
    me = ob.data
    me.materials.append(mat)

red = makeMaterial('Red',(1.0,0,1.0),(0,0,0),1)
def paint(obj,color):
    for i in range(len(obj.data.vertices)):
        color_vertex(obj, i, color)
    setObjectPaintMode(obj)

def label_vertex(loc, color):

    bpy.ops.mesh.primitive_uv_sphere_add(location=loc)
    obj = bpy.context.object
    obj.dimensions = [0.0025,0.0025,0.0025]
    setMaterial(obj, red)
    paint(obj, color)
def applyRemesh (target):
    # remesh = target.modifiers.new('RemeshToBlocks', 'BOOLEAN')
    scn = bpy.context.scene
    scn.objects.active = target
    # No empty line
    bpy.ops.object.modifier_add(type='REMESH')
    remesh = target.modifiers['Remesh'] # This is the default name, might cause problem if Remesh already exist
    if target.name == 'mesh15.002_mesh15-geometry':
        remesh.octree_depth = 6
    else:
        remesh.octree_depth = 7
    remesh.mode = 'SMOOTH'
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Remesh")

def build_kdtrees():
    kdtrees = []
    mat_worlds = []
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            mesh = obj.data
            size = len(mesh.vertices)
            kd = mathutils.kdtree.KDTree(size)
            for i, v in enumerate(mesh.vertices):
                #if obj.name == 'mesh61.003_mesh61-geometry':
                    #label_vertex(v.co, [1.0,0,1.0])
                kd.insert(v.co, i)
            kd.balance()
            kdtrees.append(kd)
            mat_world = obj.matrix_world
            mat_worlds.append(mat_world)
    return kdtrees, mat_worlds

def find_bbox():
    min_co = np.asarray([99999.9, 99999.9, 99999.9])
    max_co = np.asarray([-99999.9, -99999.9, -99999.9])
    for obj in bpy.data.objects:
        min_tmp = [99999.9, 99999.9, 99999.9]
        max_tmp = [-99999.9, -99999.9, -99999.9]
        if obj.type == 'MESH':
            bbox_corners = [obj.matrix_world * Vector(corner) for corner in obj.bound_box]
            for vec in bbox_corners:
                #print('vec', vec)
                for i in range(3):
                    if vec[i] > max_tmp[i]: max_tmp[i] = vec[i]
                    if vec[i] < min_tmp[i]: min_tmp[i] = vec[i]
            print('min_tmp',min_tmp,'max_tmp',max_tmp)
            for j in range(3):
                if min_tmp[j] < min_co[j]: min_co[j] = min_tmp[j]
                if max_tmp[j] > max_co[j]: max_co[j] = max_tmp[j]
    dimensions = max_co - min_co
    print('min',min_co,'max',max_co, 'dimensions', dimensions)
    return min_co, max_co, dimensions

def get_centers(division, dimensions, min_co):
    centers = []
    dim = dimensions / (division * 2)
    print('dim',dim)
    th = dim[0] * dim[0] + dim[1] * dim[1] + dim[2] * dim[2]
    for i in range(0, division * 2 + 1, 2):
        for j in range(0, division * 2 + 1, 2):
            for k in range(0, division * 2 + 1, 2):
                centers.append(min_co + [i * dim[0], j* dim[1], k * dim[2]])
    return centers, th

def camPosToQuaternion(cx, cy, cz):
    camDist = math.sqrt(cx * cx + cy * cy + cz * cz)
    cx = cx / camDist
    cy = cy / camDist
    cz = cz / camDist
    axis = (-cz, 0, cx)
    angle = math.acos(cy)
    a = math.sqrt(2) / 2
    b = math.sqrt(2) / 2
    w1 = axis[0]
    w2 = axis[1]
    w3 = axis[2]
    c = math.cos(angle / 2)
    d = math.sin(angle / 2)
    q1 = a * c - b * d * w1
    q2 = b * c + a * d * w1
    q3 = a * d * w2 + b * d * w3
    q4 = -b * d * w2 + a * d * w3
    return (q1, q2, q3, q4)

def quaternionFromYawPitchRoll(yaw, pitch, roll):
    c1 = math.cos(yaw / 2.0)
    c2 = math.cos(pitch / 2.0)
    c3 = math.cos(roll / 2.0)
    s1 = math.sin(yaw / 2.0)
    s2 = math.sin(pitch / 2.0)
    s3 = math.sin(roll / 2.0)
    q1 = c1 * c2 * c3 + s1 * s2 * s3
    q2 = c1 * c2 * s3 - s1 * s2 * c3
    q3 = c1 * s2 * c3 + s1 * c2 * s3
    q4 = s1 * c2 * c3 - c1 * s2 * s3
    return (q1, q2, q3, q4)


def camPosToQuaternion(cx, cy, cz):
    q1a = 0
    q1b = 0
    q1c = math.sqrt(2) / 2
    q1d = math.sqrt(2) / 2
    camDist = math.sqrt(cx * cx + cy * cy + cz * cz)
    cx = cx / camDist
    cy = cy / camDist
    cz = cz / camDist
    t = math.sqrt(cx * cx + cy * cy)
    tx = cx / t
    ty = cy / t
    yaw = math.acos(ty)
    if tx > 0:
        yaw = 2 * math.pi - yaw
    pitch = 0
    tmp = min(max(tx*cx + ty*cy, -1),1)
    #roll = math.acos(tx * cx + ty * cy)
    roll = math.acos(tmp)
    if cz < 0:
        roll = -roll
    print("%f %f %f" % (yaw, pitch, roll))
    q2a, q2b, q2c, q2d = quaternionFromYawPitchRoll(yaw, pitch, roll)
    q1 = q1a * q2a - q1b * q2b - q1c * q2c - q1d * q2d
    q2 = q1b * q2a + q1a * q2b + q1d * q2c - q1c * q2d
    q3 = q1c * q2a - q1d * q2b + q1a * q2c + q1b * q2d
    q4 = q1d * q2a + q1c * q2b - q1b * q2c + q1a * q2d
    return (q1, q2, q3, q4)

def camRotQuaternion(cx, cy, cz, theta):
    theta = theta / 180.0 * math.pi
    camDist = math.sqrt(cx * cx + cy * cy + cz * cz)
    cx = -cx / camDist
    cy = -cy / camDist
    cz = -cz / camDist
    q1 = math.cos(theta * 0.5)
    q2 = -cx * math.sin(theta * 0.5)
    q3 = -cy * math.sin(theta * 0.5)
    q4 = -cz * math.sin(theta * 0.5)
    return (q1, q2, q3, q4)

def quaternionProduct(qx, qy):
    a = qx[0]
    b = qx[1]
    c = qx[2]
    d = qx[3]
    e = qy[0]
    f = qy[1]
    g = qy[2]
    h = qy[3]
    q1 = a * e - b * f - c * g - d * h
    q2 = a * f + b * e + c * h - d * g
    q3 = a * g - b * h + c * e + d * f
    q4 = a * h + b * g - c * f + d * e
    return (q1, q2, q3, q4)

def obj_centened_camera_pos(dist, azimuth_deg, elevation_deg):
    phi = float(elevation_deg) / 180 * math.pi
    theta = float(azimuth_deg) / 180 * math.pi
    x = (dist * math.cos(theta) * math.cos(phi))
    y = (dist * math.sin(theta) * math.cos(phi))
    z = (dist * math.sin(phi))
    return (x, y, z)


# Input parameters
shape_file = sys.argv[-5]
shape_synset = sys.argv[-4]
shape_md5 = sys.argv[-3]
shape_view_params_file = sys.argv[-2]
syn_images_folder = sys.argv[-1]
if not os.path.exists(syn_images_folder):
    os.mkdir(syn_images_folder)
#syn_images_folder = os.path.join(g_syn_images_folder, shape_synset, shape_md5)
view_params = [[float(x) for x in line.strip().split(' ')] for line in open(shape_view_params_file).readlines()]

if not os.path.exists(syn_images_folder):
    os.makedirs(syn_images_folder)

bpy.ops.import_scene.obj(filepath=shape_file)

bpy.context.scene.render.alpha_mode = 'TRANSPARENT'


bpy.data.objects['Lamp'].data.energy = 0

camObj = bpy.data.objects['Camera']


# set lights
bpy.ops.object.select_all(action='TOGGLE')
if 'Lamp' in list(bpy.data.objects.keys()):
    bpy.data.objects['Lamp'].select = True # remove default light
bpy.ops.object.delete()
#print('Remesh.....')
# for obj in bpy.data.objects:
#     #bpy.ops.object.select_all(action='DESELECT')
#     if obj.type == 'MESH':
#         applyRemesh(obj)

# YOUR CODE START HERE
# scene = bpy.context.scene
# print('here')
# for i, obj in enumerate(bpy.data.objects):
#     if obj.type == 'MESH':
#         print(i, 'th obj')
#         mesh = obj.data
#         paint(obj,color[i%len(color)])


for param in view_params:
    azimuth_deg = param[0]
    elevation_deg = param[1]
    theta_deg = param[2]
    rho = param[3]

    # clear default lights
    bpy.ops.object.select_by_type(type='LAMP')
    bpy.ops.object.delete(use_global=False)

    # set environment lighting
    #bpy.context.space_data.context = 'WORLD'


    cx, cy, cz = obj_centened_camera_pos(rho, azimuth_deg, elevation_deg)
    q1 = camPosToQuaternion(cx, cy, cz)
    q2 = camRotQuaternion(cx, cy, cz, theta_deg)
    q = quaternionProduct(q2, q1)
    camObj.location[0] = cx
    camObj.location[1] = cy
    camObj.location[2] = cz
    camObj.rotation_mode = 'QUATERNION'
    camObj.rotation_quaternion[0] = q[0]
    camObj.rotation_quaternion[1] = q[1]
    camObj.rotation_quaternion[2] = q[2]
    camObj.rotation_quaternion[3] = q[3]
    scene = bpy.context.scene
    lamp_data = bpy.data.lamps.new(name="New Lamp", type='POINT')
    lamp_object = bpy.data.objects.new(name="New Lamp", object_data=lamp_data)
    scene.objects.link(lamp_object)
    lamp_object.location = (cx, cy, cz)
    lamp_data.energy = 0.5


    # ** multiply tilt by -1 to match pascal3d annotations **
    theta_deg = (-1*theta_deg)%360
    syn_image_file = './%s_%s_a%03d_e%03d_t%03d_d%03d.png' % (shape_synset, shape_md5, round(azimuth_deg), round(elevation_deg), round(theta_deg), round(rho))
    bpy.data.scenes['Scene'].render.filepath = os.path.join(syn_images_folder, syn_image_file)
    bpy.ops.render.render( write_still=True )
