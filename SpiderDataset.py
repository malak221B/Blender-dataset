import bpy
import math
import random
import os
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view


NUM_IMAGES = 50
OUTPUT_DIR = "D:/tmp/alankaboot/"
IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080
CLASS_ID = 0


os.makedirs(os.path.join(OUTPUT_DIR, "images"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "labels"), exist_ok=True)

scene = bpy.context.scene
camera = scene.camera
scene.render.resolution_x = IMAGE_WIDTH
scene.render.resolution_y = IMAGE_HEIGHT
scene.render.image_settings.file_format = 'PNG'

target_obj = bpy.context.active_object
if not target_obj:
    raise ValueError("Click on the spider")
    


def get_yolo_bounding_box(obj, scene, camera):
    matrix_world = obj.matrix_world
    bounding_box = [matrix_world @ Vector(corner) for corner in obj.bound_box]
    
    min_x, max_x = 1.0, 0.0
    min_y, max_y = 1.0, 0.0
    
    for coord in bounding_box:
        uv = world_to_camera_view(scene, camera, coord)
        min_x = min(min_x, uv.x)
        max_x = max(max_x, uv.x)
        min_y = min(min_y, uv.y)
        max_y = max(max_y, uv.y)
        
    min_x = max(0.0, min(1.0, min_x))
    max_x = max(0.0, min(1.0, max_x))
    min_y = max(0.0, min(1.0, min_y))
    max_y = max(0.0, min(1.0, max_y))
    
    if min_x >= max_x or min_y >= max_y:
        return None
        
    width = max_x - min_x
    height = max_y - min_y
    x_center = (min_x + max_x) / 2.0
    y_center = 1.0 - ((min_y + max_y) / 2.0)
    
    return [CLASS_ID, x_center, y_center, width, height]



for i in range(NUM_IMAGES):
    target_obj.location.x = random.uniform(-4.0, 4.0)
    target_obj.location.y = random.uniform(-2.5, 2.5)
    target_obj.rotation_euler.z = math.radians(random.uniform(0, 360))
    
    bpy.context.view_layer.update()
    
    bbox = get_yolo_bounding_box(target_obj, scene, camera)
    if not bbox:
        continue
        
    img_filename = f"img_{i:04d}.png"
    lbl_filename = f"img_{i:04d}.txt"
    
    scene.render.filepath = os.path.join(OUTPUT_DIR, "images", img_filename)
    bpy.ops.render.render(write_still=True)
    
    lbl_path = os.path.join(OUTPUT_DIR, "labels", lbl_filename)
    with open(lbl_path, "w") as f:
        f.write(f"{bbox[0]} {bbox[1]:.6f} {bbox[2]:.6f} {bbox[3]:.6f} {bbox[4]:.6f}\n")