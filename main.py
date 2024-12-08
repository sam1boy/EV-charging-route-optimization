import random

from map_graph import *
from navigation import *
from vehicle import *
from CS_data_storage import *
from TRmax import *
from result import *

TESTS = 5
# for testing and generating results

DISTANCE_ADJUST = 2
# distance unit in km, this is a multiplier

DRAW = 0
# 0 does not show the map, 1 shows the map

# SEASON = "spring" # 20 celcius
# SEASON = "summer" # 30 celcius
# SEASON = "fall" # 10 celcius
SEASON = "winter" # -5 celcius

THRESHOLD = 50
# SOC in percentage
END_TRIP_SOC = 5
# SOC in percentage, at least 5%
MODEL = 0
# 0: Original paper
# 1: Purposed method


for test in range(TESTS):
    # Initialize map graph information and vehicle
    nodes, roads = create_map("nodes.csv", "edges.csv", DISTANCE_ADJUST)
    ev = EVehicle(
        start_id=1,
        dest_id=18,
        capacity=57.0,
        SOC=60.0,
        efficiency=0.13
    )
    nodes.set_start_dest(ev.start_id, ev.dest_id)

    # Connect to charging station data storage base
    CS = []
    CS_nodes = nodes.all_cs
    for station in CS_nodes:
        level = station.id % 2 + 2
        CS.append(ChargingStationManager(station, random.randint(0, level*20+10), random.randint(1, 4*level), level))

    # Show the initial map without vehicle
    draw_map(DRAW, f"Map loaded, ready to drive", nodes, roads)

    # Store path to destination in a reversed stack
    path_rstack = fastest_path(nodes, nodes.start, nodes.dest)
    draw_map(DRAW, f"Start driving, expected travel distance: {path_length(path_rstack, nodes):.2f}km", nodes, roads, path_rstack)

    # Start driving
    past_path = []
    total_time = 0
    total_length = 0


    r = result()
    r.initial_path = path_rstack.copy()
    r.distance_adjust = DISTANCE_ADJUST
    r.season = SEASON
    r.threshold = THRESHOLD
    r.model = MODEL

    while path_rstack[0] != ev.dest_id:
        # print(path_rstack)
        cur_node = path_rstack[0]
        next_node = path_rstack[1]
        # Set the direction that the vehicle is going to
        road = select_road(cur_node, next_node, roads)
        draw_map(DRAW, f"At intersection {cur_node}, driving towards {next_node}", nodes, roads, path_rstack)
        # print(road.distance)
        path_rstack.pop(0)
        ev.redirect(next_node, road.distance)

        # Drives to the next intersection
        speed = road.speed_limit
        distance = road.distance - 10
        ev.drive(distance, SEASON, speed)

        road_travel_time = road.distance / speed * 60

        # Update travel history
        r.add_travel_history({
            "current_node": cur_node,
            "next_node": next_node,
            "distance": distance,
            "speed": speed,
            "SOC": ev.SOC
        })

        # Checks battery status
        # Checks if the battery is below threshold or if the vehicle will not reach destination
        reachable = ev.check_reachable(SEASON, path_rstack, roads, END_TRIP_SOC)
        if ev.SOC < THRESHOLD and not reachable:
            # Find the nearest charging station if the car is no where near one
            if not nodes.is_CS(cur_node):
                title = ""
                if ev.SOC < THRESHOLD:
                    title += f"Vehicle battery below thereshold ({ev.SOC:.2f}%),\n"
                
                if not reachable:
                    title += f"Vehicle couldn't finish trip with SOC at {END_TRIP_SOC}%,\n"
                
                draw_map(DRAW, title + f"10km before reaching intersection {next_node}", 
                        nodes, roads, [cur_node, next_node])
                
                TRmax_all = []
                paths = []
                for station in CS:
                    path = fastest_path(nodes, nodes.get_node(ev.cur_id), station.node)
                    cur_CS = CS[len(TRmax_all)]
                    if MODEL == 0:
                        available = station._occupy * ev.check_reachable(SEASON, path, roads, 0)
                    elif MODEL == 1:
                        available = ev.check_reachable(SEASON, path, roads, 0)
                    
                    path = []
                    trmax = math.inf
                    # infinite if TRmax is not available
                    if available:
                        target = ev.optimal_SOC(SEASON, nodes, nodes.dest, roads, END_TRIP_SOC)
                        # print("optimal:", target)
                        if target > 100:
                            target = 80

                        charge_time = cur_CS.charge_time_check(ev, target)
                        path1 = fastest_path(nodes, nodes.get_node(ev.cur_id), cur_CS.node)
                        time1 = travel_time(path1, nodes)

                        path2 = fastest_path(nodes, cur_CS.node, nodes.dest)
                        time2 = travel_time(path2, nodes)

                        if MODEL == 0:
                            trmax = TRmax(time1,
                                    0,
                                    charge_time,
                                    time2)
                        elif MODEL == 1:
                            trmax = TRmax(time1,
                                    cur_CS.queue_time,
                                    charge_time,
                                    time2)
                        path = [path1, path2]
                    
                    r.add_trmax_history({"At intersection": cur_node, "station_id": cur_CS.node.id, "trmax": trmax})
                    TRmax_all.append(trmax)
                    paths.append(path)


                id = TRmax_all.index(min(TRmax_all))
                if not paths[id]:
                    r.summarize()
                    print("trip falied")
                    continue
                path_rstack = paths[id][0] + paths[id][1][1:]

                r.add_trmax_history({"min station_id": CS[id].node.id, "min trmax": min(TRmax_all)})
                
                r.add_station_history({"station_id": CS[id].node.id, "queue_time": CS[id].queue_time})

                draw_map(DRAW, f"Path to charging station", nodes, roads, paths[id][0])

            # Charge the car if its at a charging station
            else:
                cur_CS = next((station for station in CS if station.node.id == cur_node), None)
        
                if cur_CS:
                    pre_SOC = ev.SOC

                    title = f"Reached charging station, charging.\nCar charged to {target}%"

                    target = ev.optimal_SOC(SEASON, nodes, nodes.dest, roads, END_TRIP_SOC)
                    # print("charge to", target)

                    if target > 100:
                        target = 80
                        title += "Choosing optimal battery at 80% SOC"

                    charge_time = cur_CS.charge_time_check(ev, target)
                    cur_CS.charge_car(ev, target)
                    road_travel_time += charge_time

                    # Update charging event in histories
                    r.add_station_history({
                        "station_id": cur_CS.node.id,
                        "charge time": charge_time,
                        "SOC_before": pre_SOC,
                        "SOC_after": ev.SOC
                    })

                    draw_map(DRAW, title, 
                            nodes, roads, past_path + [cur_node])
                    
                else:
                    print("charging station location error")
                    exit(1)

        # Drive the leftover 10 km to the next intersection
        ev.drive(10, SEASON, speed)
        past_path.append(cur_node)
        # print(past_path, path_rstack)
        # print(road.distance)

        for station in CS:
            station.update(road_travel_time)
        total_time += road_travel_time
        total_length += road.distance

            # Record EV state
        r.add_ev_history({
            "cur_node": cur_node,
            "SOC": ev.SOC,
            "distance_to_next": road.distance,
            "total_time": total_time,
            "total_length": total_length
        })

    draw_map(DRAW, f"Total travel time: {total_time:.2f} minutes and {total_length:.2f}km long",
            nodes, roads, past_path+path_rstack)

    # Print summary of results
    print(f"test {test}:")
    r.summarize()