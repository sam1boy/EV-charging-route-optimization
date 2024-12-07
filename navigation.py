from map_graph import *
import heapq

def fastest_path(nodes, start, dest):
    """
    Finds the fastest path from the start node to the destination node using Dijkstra's algorithm
    based on travel time (distance / speed limit).
    
    Parameters:
        nodes (Nodes): Nodes object containing all Node objects.
        start (Node): Starting node object.
        dest (Node): Destination node object.
    
    Returns:
        path (list): List of node IDs in the fastest path from start to destination.
    """
    # Initialize travel times and predecessors
    travel_times = {node.id: float('inf') for node in nodes.nodes.values()}
    previous_nodes = {node.id: None for node in nodes.nodes.values()}
    travel_times[start.id] = 0  # Travel time to the start node is zero

    # Priority queue to store (travel_time, node_id)
    priority_queue = [(0, start.id)]
    visited = set()  # Set of visited nodes

    # Process the priority queue
    while priority_queue:
        current_time, current_node_id = heapq.heappop(priority_queue)

        # Skip nodes that are already visited
        if current_node_id in visited:
            continue
        visited.add(current_node_id)

        # Check if we have reached the destination
        if current_node_id == dest.id:
            break

        # Get current node and its neighbors
        current_node = nodes.nodes[current_node_id]
        for edge in current_node.edges:
            neighbor = edge.other_node(current_node)
            if neighbor.id in visited:
                continue

            # Calculate travel time for this edge (in minutes)
            edge_travel_time = (edge.distance / edge.speed_limit) * 60
            new_time = current_time + edge_travel_time

            # If the new travel time is shorter, update times and predecessors
            if new_time < travel_times[neighbor.id]:
                travel_times[neighbor.id] = new_time
                previous_nodes[neighbor.id] = current_node_id
                heapq.heappush(priority_queue, (new_time, neighbor.id))

    # Reconstruct the path from start to destination
    path = []
    current_id = dest.id
    while current_id is not None:
        path.insert(0, current_id)
        current_id = previous_nodes[current_id]

    return path



def path_length(path, nodes):
    """
    Calculates the total length of a path based on an array of node IDs and Node objects.
    
    Parameters:
        path (list): List of node IDs representing the path.
        nodes (Nodes): Nodes object containing all Node objects.
    
    Returns:
        float: Total length of the path in kilometers.
    """
    if not path or len(path) < 2:
        return 0.0  # No path or insufficient nodes to form a path
    
    total_length = 0.0
    
    for i in range(len(path) - 1):
        # Get the current and next node in the path
        current_node = nodes.get_node(path[i])
        next_node = nodes.get_node(path[i + 1])
        
        # Find the edge connecting the current and next node
        edge = next((edge for edge in current_node.edges if edge.other_node(current_node) == next_node), None)
        
        if edge:
            total_length += edge.distance  # Add edge distance to total length
    return total_length

def travel_time(path, nodes):
    """
    Calculates the total travel time for a path based on an array of node IDs and Node objects.
    
    Parameters:
        path (list): List of node IDs representing the path.
        nodes (Nodes): Nodes object containing all Node objects.
    
    Returns:
        float: Total travel time in minutes.
    """
    if not path or len(path) < 2:
        return 0.0  # No path or insufficient nodes to form a path
    
    total_time = 0.0
    
    for i in range(len(path) - 1):
        # Get the current and next node in the path
        current_node = nodes.nodes[path[i]]
        next_node = nodes.nodes[path[i + 1]]
        
        # Find the edge connecting the current and next node
        edge = next((edge for edge in current_node.edges if edge.other_node(current_node) == next_node), None)
        
        if edge:
            # Calculate time for this edge: time = (distance / speed_limit) * 60
            edge_time = (edge.distance / edge.speed_limit) * 60
            total_time += edge_time
    
    return total_time