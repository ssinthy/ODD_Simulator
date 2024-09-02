import carla
import time

def draw_string(world, location, text="first"):
    world.debug.draw_string(location, text, draw_shadow=False, color=carla.Color(255,0,0), life_time=100.0)

def draw_point(world, location, size=0.1):
    world.debug.draw_point(location, size, carla.Color(255, 0, 0, 0), life_time=50.0)
    
def draw_hud_box(world, location, thickness=0.1):
    box_size = carla.Vector3D(2.0, 2.0, 0.0)
    box = carla.BoundingBox(location, box_size)
    rotation = carla.Rotation(yaw = -155)
    world.debug.draw_box(box, rotation, thickness, carla.Color(255, 0, 0, 0), life_time=50.0)

# Connect to the CARLA server
client = carla.Client('localhost', 2000)
client.set_timeout(10.0)

# path windows D:\\CARLA_0.9.15\\WindowsNoEditor\\PythonAPI\\util\\opendrive\\DE_Hamburg_S01_01_REM_101_0_1_V00_5_Yellow_Section_open_drive_1_4.xodr
# Read the OpenDRIVE file into a string
# with open('/home/sumaiya/carla/PythonAPI/util/opendrive/DE_Hamburg_S01_01_REM_101_0_1_V00_5_Yellow_Section_open_drive_1_4.xodr', 'r') as file:
#    opendrive_string = file.read()

# Set map parameters if needed
parameters = carla.OpendriveGenerationParameters(
    vertex_distance=2.0,
    max_road_length=50.0,
    wall_height=1.0,
    additional_width=0.6,
    smooth_junctions=True,
    enable_mesh_visibility=True
)

# Generate the CARLA world from the OpenDRIVE file
# world = client.generate_opendrive_world(opendrive_string, parameters)

# Get the world and map
world = client.load_world('Town05')
carla_map = world.get_map()
# Get the map's spawn points
spawn_points = world.get_map().get_spawn_points()
bp_lib = world.get_blueprint_library()

vehicle_bp = bp_lib.find('vehicle.audi.etron')
ego_vehicle = world.try_spawn_actor(vehicle_bp, spawn_points[21])

# Spawn an emergency vehicle
emergency_bp = world.get_blueprint_library().find('vehicle.carlamotors.firetruck')
emergency_vehicle = world.spawn_actor(emergency_bp, spawn_points[176])


spawn_point_motor_way = spawn_points[176]

# Get spectator
spectator = world.get_spectator()

location = ego_vehicle.get_location()

transform = carla.Transform(ego_vehicle.get_transform().transform(carla.Location(x=-4, z=2)), ego_vehicle.get_transform().rotation)

spectator_pos_motorway = carla.Transform(spawn_point_motor_way.location + carla.Location(x=20,z=8),
                            carla.Rotation(yaw = spawn_point_motor_way.rotation.yaw))
spectator.set_transform(spectator_pos_motorway)


# draw spawn points
for i in range(0, len(spawn_points)):
    str = f"point {i}"
    draw_string(world, spawn_points[i].location, str)


# draw_hud_box(world, first_spawn_point.location)
# Add some delay to visualize the changes
#time.sleep(50)

'''
# Get waypoint
waypoints = carla_map.get_topology()

# draw road_id lane_id points
for waypoint in waypoints:
    str = f"id {waypoint[0].road_id} {waypoint[0].lane_id}"
    draw_string(world, waypoint[0].transform.location, str)
    
'''