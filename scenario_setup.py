import carla
import random
import time
import math

# Parameters for RSS
response_time = 2.0  # seconds, time to respond
max_brake = 8.0  # m/s^2, maximum braking capability
comfortable_brake = 4.0  # m/s^2, comfortable braking capability

def rss_safe_longitudinal_distance(ego_speed, other_speed):
    # RSS longitudinal safe distance calculation based on speeds and braking
    safe_distance = (ego_speed * response_time) + (0.5 * ego_speed ** 2 / comfortable_brake) - (0.5 * other_speed ** 2 / max_brake)
    return max(safe_distance, 0.0)  # Ensure non-negative distance

def rss_safe_lateral_distance():
    # RSS typically defines a constant safe lateral distance (e.g., based on lane width)
    return 1.5  # meters, arbitrary safe lateral distance

def get_lateral_longitudinal_distance(vehicle1, vehicle2):
    # Get the positions of both vehicles
    location1 = vehicle1.get_location()
    location2 = vehicle2.get_location()

    # Get the yaw (orientation) of vehicle1 in radians
    yaw1 = math.radians(vehicle1.get_transform().rotation.yaw)

    # Calculate the difference in positions
    dx = location2.x - location1.x
    dy = location2.y - location1.y

    # Calculate longitudinal and lateral distances
    longitudinal_distance = math.cos(yaw1) * dx + math.sin(yaw1) * dy
    lateral_distance = -math.sin(yaw1) * dx + math.cos(yaw1) * dy

    return lateral_distance, longitudinal_distance

def main():
    # Connect to the Carla server
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    spectator = world.get_spectator()
    
    # Get a blueprint library and choose a vehicle blueprint
    blueprint_library = world.get_blueprint_library()
    vehicle_bp = blueprint_library.filter('vehicle.*')[0]  # Use the first vehicle blueprint
    emv_bp = blueprint_library.filter(vehicle.ford.ambulance)

    # Get a random spawn point
    spawn_points = world.get_map().get_spawn_points()
    spawn_point = spawn_points[1]
    
    vehicles = world.get_actors().filter('vehicle.*')
    
    for vehicle in vehicles:
        vehicle.destroy()

    # Spawn the vehicle
    vehicle1 = world.spawn_actor(vehicle_bp, spawn_points[0])
    
    # Spawn the vehicle
    vehicle2 = world.spawn_actor(emv_bp, spawn_point)
    
    transform = carla.Transform(spawn_point.location + carla.Location(x=20, y=10, z=4),
                                carla.Rotation(yaw = spawn_point.rotation.yaw - 155))
    spectator.set_transform(transform)
    
    vehicle1.set_autopilot(True)
    vehicle2.set_autopilot(True)
    
    while True:
        time.sleep(1)
        # Get the speeds of both vehicles in m/s
        ego_velocity = vehicle1.get_velocity()
        other_velocity = vehicle2.get_velocity()

        ego_speed = math.sqrt(ego_velocity.x**2 + ego_velocity.y**2 + ego_velocity.z**2)
        other_speed = math.sqrt(other_velocity.x**2 + other_velocity.y**2 + other_velocity.z**2)

        # Get the lateral and longitudinal distances between the vehicles
        lateral_distance, longitudinal_distance = get_lateral_longitudinal_distance(vehicle1, vehicle2)

        # Calculate RSS safe distances
        safe_longitudinal = rss_safe_longitudinal_distance(ego_speed, other_speed)
        safe_lateral = rss_safe_lateral_distance()

        # Print out distances and safety checks
        print(f"Longitudinal Distance: {longitudinal_distance:.2f} m, Safe Longitudinal: {safe_longitudinal:.2f} m")
        print(f"Lateral Distance: {lateral_distance:.2f} m, Safe Lateral: {safe_lateral:.2f} m")

        # Safety check
        if longitudinal_distance < safe_longitudinal:
            print("Warning: Unsafe longitudinal distance!")
        if lateral_distance < safe_lateral:
            print("Warning: Unsafe lateral distance!")

        world.wait_for_tick()
    
if __name__ == '__main__':
    main()
