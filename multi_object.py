import blenderproc as bproc
import numpy as np
import random
import glob
import os
import json
import bpy
import cv2
# Function to load a random object from the "data/objects" folder
def load_random_object(object_dir):
    object_files = glob.glob(object_dir+"/*.blend")
    if not object_files:
        print("No objects found in data/objects/. Using a primitive shape instead.")
        shape = np.random.choice(['CUBE', 'SPHERE', 'CYLINDER'])
        obj = bproc.object.create_primitive(shape)
    else:
        chosen_file = random.choice(object_files)
        obj = bproc.loader.load_blend(chosen_file)[0]  # Load first object in file

    random_x=np.random.uniform(-3,3)
    random_y=np.random.uniform(-3,3)
    size = random.choice([1, 2, 3])
    if size==1:
        obj.set_scale([0.5,0.5,0.5])
    elif size==2:
        obj.set_scale([1,1,1])
    elif size==3:
        obj.set_scale([1.5,1.5,1.5])
    bbox = obj.get_bound_box()  # Returns an array of 8 corner points

    # Get the min and max coordinates along each axis
    bbox_min = np.min(bbox, axis=0)  # Minimum x, y, z coordinates
    bbox_max = np.max(bbox, axis=0)  # Maximum x, y, z coordinates
    obj_height = bbox_max[2] - bbox_min[2]  # Height of the object
    obj.set_location([random_x, random_y, obj_height / 2])  # Adjust so it sits on the ground

    obj.set_rotation_euler([0, 0, np.random.uniform(0, 2*np.pi)])  # Random rotation
    return obj,size,(random_x,random_y)

# Function to apply a random material from "data/materials" folder
def apply_random_material(obj, material_dir):
    material_files = ["Metallic.blend", "Rubber.blend"]
    
    # Randomly pick one of the materials
    chosen_material_file = random.choice(material_files)
    material_path = os.path.join(material_dir, chosen_material_file)
    #print(material_path)
    # Load the blend file
    bproc.loader.load_blend(material_path)

    # Extract materials from the loaded objects
    materials = [mat for mat in bpy.data.materials if mat.users > 0]  # Only materials in use
    print(f"Materials found in {chosen_material_file}:",materials)
    if materials:
        if chosen_material_file=="Metallic.blend":
            material = materials[1]  
        else:
            material = materials[0]
        #print(f"Applying Material: {material.name}")
        obj.blender_obj.data.materials.append(material)  # Assign it to the object
    else:
        raise RuntimeError(f"No materials found in {chosen_material_file}")
    
def apply_random_material_self(obj):
     

    # Randomly choose between metallic and rubbery
    material_type = random.choice(["metallic", "rubbery"])
    
    if material_type == "metallic":
        mat = bproc.material.create('Metallic')
        mat.set_principled_shader_value("Metallic", 1.0)  # Fully metallic
        mat.set_principled_shader_value("Roughness", 0.1)  # Slight shine
        mat.set_principled_shader_value("Base Color", np.append(np.random.uniform(0, 1, size=3),1))  # Light metallic tones
        #mat.set_principled_shader_value("Base Color", [0,1,0,1])
    elif material_type == "rubbery":
        mat = bproc.material.create('Rubber')
        mat.set_principled_shader_value("Metallic", 0.0)  # Non-metallic
        mat.set_principled_shader_value("Roughness", 0.9)  # Matte, rough look
        mat.set_principled_shader_value("Base Color", np.append(np.random.uniform(0, 1, size=3),1))  # Darker, rubber-like tones
        #mat.set_principled_shader_value("Base Color", [1,0,0,1])
    obj.replace_materials(mat)
    

#need to reassign the numbers if required 
def assign_numeric_shape(shape):
    #print(shape)
    if shape=="SmoothCube_v2":
        return 1
    elif shape=="SmoothCylinder":
        return 2
    elif shape=="Sphere":
        return 3

#need to reassign the numbers if required
def assign_numeric_material(material):
    #print(material)
    if material.get_name()=="Metallic":
        return 1
    elif material.get_name()=="Rubber":
        return 2

def render_scene(output_image_path, output_annotation_dir, material_dir, object_dir , light_type, light_num):
    # Initialize BlenderProc
    bproc.clean_up()
    
    # Reset keyframes (optional)
    bproc.utility.reset_keyframes()
    

    min_radius=6
    max_radius=6

    #bproc.camera.set_intrinsics_from_blender_params(35, 256,256)
    bproc.camera.set_intrinsics_from_blender_params(36, 480, 320) #according to clevr
    radius=np.random.uniform(min_radius,max_radius)
    azimuth=np.random.uniform(0,2*np.pi)
    elevation = np.random.uniform(np.pi /6, np.pi / 2) #restricted elevation to 45-90 degrees
    random_x =radius*np.cos(azimuth)*np.cos(elevation)  
    random_y = radius*np.sin(azimuth)*np.cos(elevation)
    random_z = radius*np.sin(elevation)
    # random_camera_position = np.array([random_x, random_y, random_z])
    # bproc.camera.set_location(random_camera_position)
    # bproc.camera.look_at([0, 0, 0])

    random_camera_position = np.array([random_x, random_y, random_z])


    poi = np.array([0, 0, 0])  
    rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - random_camera_position)
    cam_pose = bproc.math.build_transformation_mat(random_camera_position, rotation_matrix)
    bproc.camera.add_camera_pose(cam_pose)

    for i in range(light_num):
        if light_type=="point":
            light = light = bproc.types.Light()
            light.set_type("POINT")
            radius=np.random.uniform(min_radius,max_radius)
            azimuth=np.random.uniform(0,2*np.pi)
            elevation = np.random.uniform(np.pi / 12, np.pi / 2) #restricted elevation to 30-60 degrees
            random_x =radius*np.cos(azimuth)*np.cos(elevation)  
            random_y = radius*np.sin(azimuth)*np.cos(elevation)
            random_z = radius*np.sin(elevation)
            random_light_position = np.array([random_x, random_y, random_z])
            light.set_location(random_light_position)
            #random_light_energy = np.random.uniform(100, 500)
            random_light_energy = 10
            light.set_energy(random_light_energy)
            light.set_radius(5)
        #can add other light types here
        elif light_type=="sun":
            light = light = bproc.types.Light()
            light.set_type("SUN")
            radius=np.random.uniform(min_radius,max_radius)
            azimuth=np.random.uniform(0,2*np.pi)
            elevation = np.random.uniform(np.pi /4, np.pi / 2) #restricted elevation to 30-60 degrees
            random_x =radius*np.cos(azimuth)*np.cos(elevation)  
            random_y = radius*np.sin(azimuth)*np.cos(elevation)
            random_z = radius*np.sin(elevation)
            random_light_position = np.array([random_x, random_y, random_z])
            light.set_location(random_light_position)
            random_light_energy = np.random.uniform(100, 500)
            light.set_energy(random_light_energy)
        elif light_type=="area":
            light = light = bproc.types.Light()
            light.set_type("AREA")
            radius=np.random.uniform(min_radius,max_radius)
            azimuth=np.random.uniform(0,2*np.pi)
            elevation = np.random.uniform(np.pi / 12, np.pi / 2) #restricted elevation to 30-60 degrees
            random_x =radius*np.cos(azimuth)*np.cos(elevation)  
            random_y = radius*np.sin(azimuth)*np.cos(elevation)
            random_z = radius*np.sin(elevation)
            random_light_position = np.array([random_x, random_y, random_z])
            light.set_location(random_light_position)
            #random_light_energy = np.random.uniform(100, 500)
            random_light_energy = 50
            light.set_energy(random_light_energy)
            light.set_radius(5)
        elif light_type=="spot":
            light = light = bproc.types.Light()
            light.set_type("SPOT")
            radius=np.random.uniform(min_radius,max_radius)
            azimuth=np.random.uniform(0,2*np.pi)
            elevation = np.random.uniform(np.pi / 4, np.pi / 2) #restricted elevation to 30-60 degrees
            random_x =radius*np.cos(azimuth)*np.cos(elevation)  
            random_y = radius*np.sin(azimuth)*np.cos(elevation)
            random_z = radius*np.sin(elevation)
            random_light_position = np.array([random_x, random_y, random_z])
            light.set_location(random_light_position)
            #random_light_energy = np.random.uniform(100, 500)
            random_light_energy = 100
            light.set_energy(random_light_energy)

    # Create ground plane
    ground = bproc.object.create_primitive('PLANE', size=10000)
    ground.set_location([0, 0, 0])
    ground_material = bproc.material.create('ground_material')
    ground_material.set_principled_shader_value("Roughness", 1.0)  # Matte red surface
    ground_material.set_principled_shader_value("Base Color", [0.73, 0.73, 0.73, 1])
    ground.replace_materials(ground_material)
    #ground.set_cp("reflective", True)


    min_distance=0.1
    positions=[]
    sizes=[]
    max_num_objects=10
    num_objects=np.random.randint(1,max_num_objects+1)
    print("original number of objects",num_objects)
    max_tries=10
    successful=0
    for n in range(num_objects):
        is_placed=False
        tries=0
        while not is_placed and tries<max_tries:
            tries+=1
            obj,size,position=load_random_object(object_dir)
            x,y=position
            for i in range(len(positions)):
                xx,yy=positions[i]
                sizesize=sizes[i]
                if np.linalg.norm(np.array([xx,yy])-np.array([x,y]))-size-sizesize<min_distance:
                    obj.delete()
                    break 
            else:
                apply_random_material_self(obj)
                positions.append(position)
                sizes.append(size)
                is_placed=True
                successful+=1
    num_objects=successful
    print("number of objects placed",num_objects)


 
    
    
   
    # camera_poses = bproc.camera.get_camera_pose()  # List of 4×4 matrices
   
    # tmat = camera_poses 

    # # Extract camera position from the transformation matrix
    # x_camera, y_camera, z_camera = tmat[:3, 3]
    # #print(x_camera, y_camera, z_camera)
    # x_light,y_light,z_light=light.get_location()
    # x_pos,y_pos,z_pos=obj.get_location()
    # # material=  obj.get_materials()
    # # print(material)
    # colour=obj.get_materials()[0].get_principled_shader_value("Base Color")
    # colour=list(colour[:3])
    # properties = {
    #     "num_objects": 1,
    #     "x_light": x_light,
    #     "y_light": y_light,
    #     "z_light": z_light,
    #     "x_camera": x_camera,
    #     "y_camera": y_camera,
    #     "z_camera": z_camera,
    #     "light_energy": light.get_energy(),
    #     "object_properties": [{ "x_position": x_pos,
    #                             "y_position": y_pos,
    #                             "z_position": z_pos,
    #                             "z_rotation": obj.get_rotation_euler()[2],
    #                             "shape": assign_numeric_shape(obj.get_name()),
    #                             "colour" : colour,
    #                             "material": assign_numeric_material(obj.get_materials()[0]),
    #                             "size":size
    #                             }
    #                         ] 
    #     } 
    # marker = bproc.object.create_primitive('SPHERE', radius=0.2)
    # marker.set_location([0, 0, 0])

    # # Optional: Make it a bright color
    # marker_material = bproc.material.create('marker_material')
    # marker_material.set_principled_shader_value("Base Color", [0.0, 0.0, 1.0, 1])  # Blue
    # marker.replace_materials(marker_material)


    #bproc.camera.set_resolution(1024, 1024)  # Increase resolution
    bproc.renderer.set_max_amount_of_samples(1024)  # Increase samples for better quality
    #bproc.renderer.set_render_devices()
    bproc.renderer.set_world_background([0.73,0.73,0.73],1)

    # Render the scene
    #bproc.renderer.enable_depth_output(True)
    bproc.renderer.set_light_bounces(glossy_bounces=8, diffuse_bounces=8)
    bproc.renderer.set_output_format("PNG")
    data=bproc.renderer.render()
    #print(data)
    color_image = data["colors"][0]
    color_image = np.flipud(color_image)
    print("shape:",np.shape(color_image))
    cv2.imwrite(output_image_path, cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR))

    #return properties

    # Save the annotation 





def main():
    type = "multi"
    version = "1.0"
    material_dir = "data/materials"
    object_dir = "data/shapes"
    output_path = "output"
    output_image_dir = os.path.join(output_path,type,version,"images")#output/multi/1.0/images
    output_properties_dir = os.path.join(output_path,type,version,"properties")#output/multi/1.0/properties
    if not os.path.exists(output_image_dir):
        os.makedirs(output_image_dir)
    if not os.path.exists(output_properties_dir):
        os.makedirs(output_properties_dir)
    
    num_images = 10
    light_type="point" #spot is too dark sun is too bright point and area are similar
    light_num=3
    dataset_properties=[]

    bproc.init()

    for i in range(num_images):
        output_image_path=os.path.join(output_image_dir, f"image_{i}.png")
        #output_properties_path=os.path.join(output_properties_dir, f"properties_{i}.json")
    #     dataset_properties.append(render_scene(output_image_path, output_properties_dir, material_dir, object_dir, light_type, light_num))
    # output_properties_path=os.path.join(output_properties_dir,"properties.json")    
    # json_string = json.dumps(dataset_properties, indent=4)
    # with open(output_properties_path, "w") as json_file:
    #     json.dump(dataset_properties, json_file, indent=4)
        render_scene(output_image_path, output_properties_dir, material_dir, object_dir, light_type, light_num)


if __name__=="__main__":
    main()