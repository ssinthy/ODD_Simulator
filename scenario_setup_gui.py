import tkinter as tk
from tkinter import ttk
import carla

# Initialize the main window
root = tk.Tk()
root.title("ScenarioInfoManager")
root.geometry("600x500")  # Set the window size

global_ego_vehicle = None
global_emv_vehicle = None
world = None
client = None

# Default values for each field
default_values = {
    "road_type": "Motorway",
    "ego_vehicle_position": "Traffic Lane",
    "emv_position": "Same Road",
    "emv_direction": "Approaches from Behind",
    "weather_condition": "Clear",
    "time_of_day": "Day time",
    "safety_distance": "0",
}

# Dictionary to store previous values of comboboxes and spinbox
previous_values = default_values.copy()

# Define the options for each combobox
road_type_options = ["Motorway", "Expressway"]
ego_vehicle_position_options = ["Traffic Lane", "Approaching Intersection", "Approaching T-Junction"]
emv_position_options = ["Same Road", "Parallel Road", "Opposite Road", "Cross Road"]
emv_direction_options = ["Approaches from Behind", "As Lead Vehicle", "Approaches from Right Lane", "Approaches from Left Lane", "Approaches on Opposite Lane", 
                         "Approaches Intersection", "Approaches T-Junction"]
weather_options = ["Clear", "Cloudy", "Light Rain", "Moderate Rain", "Heavy Rain"]
time_of_day_options = ["Day time", "Night time"]

# Function to handle value changes in comboboxes
def on_combobox_change(event, combobox_name):
    current_value = event.widget.get()  # Get the current value of the combobox
    if current_value != previous_values[combobox_name]:
        print(f"{combobox_name} changed to {current_value}")
        previous_values[combobox_name] = current_value  # Update the stored value


def connect_to_carla():
    global world, client
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.load_world("Town05")

# TODO Separate ego vehicle and emv spawning
def spawn_ego_vehicle(ego_spawn_point = 21):
    global global_ego_vehicle, world, client
    # Spawn an emergency vehicle town 5 spawn point 108 / HH map 154
    spawn_points = world.get_map().get_spawn_points()
    vehicle_bp = world.get_blueprint_library().find('vehicle.audi.etron')
    global_ego_vehicle = world.try_spawn_actor(vehicle_bp, spawn_points[ego_spawn_point])
    
    # Set spectator manual navigation
    spectator = world.get_spectator()
    transform = carla.Transform(global_ego_vehicle.get_transform().transform(carla.Location(x=-20, y= 0, z=5)), global_ego_vehicle.get_transform().rotation)
    spectator.set_transform(transform)
   
    global_ego_vehicle.set_autopilot(True)
    
def spawn_emergency_vehicle(emv_spawn_point = 176):
    global global_ego_vehicle, global_emv_vehicle, world, client
    spawn_points = world.get_map().get_spawn_points()
    
    emergency_bp = world.get_blueprint_library().find('vehicle.carlamotors.firetruck')
    global_emv_vehicle = world.spawn_actor(emergency_bp, spawn_points[emv_spawn_point])
    traffic_manager = client.get_trafficmanager()
    traffic_manager_port = traffic_manager.get_port()

    # Set the vehicle to drive 30% faster than the current speed limit
    traffic_manager.vehicle_percentage_speed_difference(global_emv_vehicle, -30)  # No speed variation
    
    # Make the vehicle ignore traffic lights
    traffic_manager.ignore_lights_percentage(global_emv_vehicle, 100)
    
    # Turn on the vehicle's (emergency lights)
    from carla import VehicleLightState as vls
    global_emv_vehicle.set_light_state(carla.VehicleLightState(vls.Special1))
        
    global_emv_vehicle.set_autopilot(True, traffic_manager_port)
    
def change_vehicle_spawn_point(ego_spawn_point, emv_spawn_point):
    global global_ego_vehicle, global_emv_vehicle
    
    global_ego_vehicle.destroy()
    global_emv_vehicle.destroy()
    
    spawn_ego_vehicle(ego_spawn_point)
    spawn_emergency_vehicle(emv_spawn_point)
    
def map_user_input_to_carla_map(scenario_info):
    
    if scenario_info["road_type"] == "Motorway":
        if scenario_info["ego_vehicle_position"] == "Traffic Lane":
            pass
        elif scenario_info["ego_vehicle_position"] == "Approaching Intersection":
            pass
        elif scenario_info["ego_vehicle_position"] == "Approaching T-Junction":
            pass
    elif scenario_info["road_type"] == "Expressway":
        pass
        
# Function to handle the Start Simulation button click
def start_simulation():
    
    connect_to_carla()
    
    spawn_ego_vehicle()
    
    spawn_emergency_vehicle()
    

# Function to handle the Set Up Scenario button click
def setup_scenario():
    # Gather all the values from the comboboxes
    road_type = road_type_cb.get()
    ego_vehicle_position = ego_vehicle_position_cb.get()
    emv_position = emv_position_cb.get()
    emv_direction = emv_direction_cb.get()
    weather_condition = weather_cb.get()
    time_of_day = time_of_day_cb.get()
    safety_distance = safety_distance_sb.get()
    
    scenario_info = {
    "road_type": road_type,
    "ego_vehicle_position": ego_vehicle_position,
    "emv_position": emv_position,
    "emv_direction": emv_direction,
    "weather_condition": weather_condition,
    "time_of_day": time_of_day,
    "safety_distance": safety_distance,
    }
    
    map_user_input_to_carla_map(scenario_info)
    change_vehicle_spawn_point(200, 22)

# Define a larger font
large_font = ("Helvetica", 14)

# Create and place the widgets
ttk.Label(root, text="Road Type", font=large_font).grid(row=0, column=0, padx=20, pady=10, sticky=tk.W)
road_type_cb = ttk.Combobox(root, values=road_type_options, state="readonly", font=large_font)
road_type_cb.set(default_values["road_type"])
road_type_cb.grid(row=0, column=1, padx=20, pady=10)

ttk.Label(root, text="Ego Vehicle Position", font=large_font).grid(row=1, column=0, padx=20, pady=10, sticky=tk.W)
ego_vehicle_position_cb = ttk.Combobox(root, values=ego_vehicle_position_options, state="readonly", font=large_font)
ego_vehicle_position_cb.set(default_values["ego_vehicle_position"])
ego_vehicle_position_cb.grid(row=1, column=1, padx=20, pady=10)

ttk.Label(root, text="Emergency Vehicle Position", font=large_font).grid(row=2, column=0, padx=20, pady=10, sticky=tk.W)
emv_position_cb = ttk.Combobox(root, values=emv_position_options, state="readonly", font=large_font)
emv_position_cb.set(default_values["emv_position"])
emv_position_cb.grid(row=2, column=1, padx=20, pady=10)

ttk.Label(root, text="EMV Travel Direction", font=large_font).grid(row=3, column=0, padx=20, pady=10, sticky=tk.W)
emv_direction_cb = ttk.Combobox(root, values=emv_direction_options, state="readonly", font=large_font)
emv_direction_cb.set(default_values["emv_direction"])
emv_direction_cb.grid(row=3, column=1, padx=20, pady=10)

ttk.Label(root, text="Weather Condition", font=large_font).grid(row=4, column=0, padx=20, pady=10, sticky=tk.W)
weather_cb = ttk.Combobox(root, values=weather_options, state="readonly", font=large_font)
weather_cb.set(default_values["weather_condition"])
weather_cb.grid(row=4, column=1, padx=20, pady=10)

ttk.Label(root, text="Time of Day", font=large_font).grid(row=5, column=0, padx=20, pady=10, sticky=tk.W)
time_of_day_cb = ttk.Combobox(root, values=time_of_day_options, state="readonly", font=large_font)
time_of_day_cb.set(default_values["time_of_day"])
time_of_day_cb.grid(row=5, column=1, padx=20, pady=10)

ttk.Label(root, text="Safety Distance (m)", font=large_font).grid(row=6, column=0, padx=20, pady=10, sticky=tk.W)
safety_distance_sb = tk.Spinbox(root, from_=0, to=100, increment=1, font=large_font)
safety_distance_sb.grid(row=6, column=1, padx=20, pady=10)

start_button = ttk.Button(root, text="Start Simulation", command=start_simulation, style='TButton')
start_button.grid(row=7, column=0, columnspan=2, pady=20, ipadx=10, ipady=5)

setup_button = ttk.Button(root, text="Set Up Scenario", command=setup_scenario, style='TButton')
setup_button.grid(row=8, column=0, columnspan=2, pady=10, ipadx=10, ipady=5)

# Start the main event loop
root.mainloop()
