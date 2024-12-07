import math
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

class Node:
    def __init__(self, id, longitude, latitude, node_type):
        self.id = id
        self.longitude = longitude
        self.latitude = latitude
        self.type = node_type  # Type of node (CS, start, dest, intersection)
        self.edges = []  # List of edges connected to this node
    
    def add_edge(self, edge):
        """Adds an edge to the node."""
        self.edges.append(edge)
    
    def set_node(self, type):
        """Sets a node's type"""
        self.type = type

    def __repr__(self):
        return f"Node({self.id}, lat={self.latitude}, long={self.longitude}, type={self.type})"
    
    def connections(self):
        """Returns a list of nodes connected to this node by edges."""
        return [e.other_node(self) for e in self.edges]
    

class Nodes:
    def __init__(self):
        """Initialize the Nodes object with a dictionary of Node objects."""
        self._nodes = {}  # Dictionary to store nodes by their ID

    def add_node(self, id, node):
        """
        Add a node to the collection.
        
        Parameters:
            id (int): The ID of the node.
            node (Node): The Node object to add.
        """
        self._nodes[id] = node

    # For testing
    @property
    def nodes(self):
        """Returns all nodes as a dictionary."""
        return self._nodes

    # For testing
    @property
    def start(self):
        """Returns the start node."""
        for node in self._nodes.values():
            if node.type == 'start':
                return node
        return None

    @property
    def dest(self):
        """Returns the destination node."""
        for node in self._nodes.values():
            if node.type == 'dest':
                return node
        return None

    @property
    def all_cs(self):
        """Returns a list of all charging station nodes."""
        return [node for node in self._nodes.values() if node.type == 'CS']
    
    def get_node(self, id):
        """Returns the node with corresponding id."""
        return self._nodes.get(id)
    
    def set_start_dest(self, start, dest):
        """Set the start and destination"""
        self._nodes.get(start).set_node("start")
        self._nodes.get(dest).set_node("dest")
        return
    
    def is_CS(self, id):
        """Checks if the node is a charging station"""
        node = self._nodes.get(id)
        if node and node.type == 'CS':
            return True
        return False

class Edge:
    def __init__(self, node1, node2, distance, speed_limit):
        self.node1 = node1  # First node this edge connects
        self.node2 = node2  # Second node this edge connects
        self._distance = distance  # Calculated distance between the nodes in kilometers
        self._speed_limit = speed_limit  # Speed limit in km/h
        
        # Automatically add this edge to both nodes
        self.node1.add_edge(self)
        self.node2.add_edge(self)
    
    def __repr__(self):
        return f"Edge(Node1={self.node1.id}, Node2={self.node2.id}, distance={self.distance:.1f}m, speed_limit={self.speed_limit}km/h)"
    
    def other_node(self, current_node):
        """Returns the other node connected by this edge."""
        return self.node2 if current_node == self.node1 else self.node1

    @property
    def distance(self):
        """Returns the distance between the two nodes."""
        return self._distance
    
    @property
    def speed_limit(self):
        """Returns the speed limit for this edge."""
        return self._speed_limit

def select_road(node1_id, node2_id, edges):
    """
    Selects an edge from the edges list that connects the given node IDs.
    
    Parameters:
        node1_id (int): The ID of the first node.
        node2_id (int): The ID of the second node.
        edges (list): List of Edge objects.
    
    Returns:
        Edge: The edge connecting node1_id and node2_id, or None if no such edge exists.
    """
    for edge in edges:
        if (edge.node1.id == node1_id and edge.node2.id == node2_id) or (edge.node1.id == node2_id and edge.node2.id == node1_id):
            return edge
    return None

def euclidean_distance(node1, node2):
    """Calculates the Euclidean distance between two nodes based on latitude and longitude."""
    lon1, lat1 = node1.longitude, node1.latitude
    lon2, lat2 = node2.longitude, node2.latitude
    return math.sqrt((lon2 - lon1) ** 2 + (lat2 - lat1) ** 2) # Approx conversion to kilometers


def create_map(nodes_file_path, edges_file_path, ADJUST):
    """
    Creates a map by reading nodes and edges from CSV files.
    
    Parameters:
        nodes_file_path (str): Path to the nodes.csv file.
        edges_file_path (str): Path to the edges.csv file.
    
    Returns:
        nodes (Nodes): A Nodes object containing all Node objects.
        edges (list): A list of Edge objects.
    """
    # Read nodes from nodes.csv
    nodes_df = pd.read_csv(nodes_file_path)
    nodes = Nodes()  # Create an instance of the Nodes class

    for _, row in nodes_df.iterrows():
        # Add each node to the Nodes object
        node = Node(row['id'], row['longitude'], row['latitude'], row['type'])
        nodes.add_node(row['id'], node)

    # Read edges from edges.csv
    edges_df = pd.read_csv(edges_file_path)
    edges = []

    for _, row in edges_df.iterrows():
        # Find nodes by their IDs using the Nodes class
        node1 = nodes.nodes[row['node1']]
        node2 = nodes.nodes[row['node2']]
        
        # Set speed limit based on road type
        if row['road_type'] == 'highway':
            speed_limit = 100
        elif row['road_type'] == 'local':
            speed_limit = 70
        elif row['road_type'] == 'nbhd':
            speed_limit = 40

        # Calculate distance between nodes
        distance = euclidean_distance(node1, node2) * ADJUST
        
        # Create Edge object
        edge = Edge(node1, node2, distance, speed_limit)
        edges.append(edge)

    return nodes, edges


def draw_map(draw, title, nodes, edges, fastest_path=None):
    """
    Draws the map graph using NetworkX and Matplotlib, with an optional highlight for the fastest path.
    
    Parameters:
        nodes (Nodes): Nodes object containing all Node objects.
        edges (list): List of Edge objects.
        fastest_path (list, optional): List of node IDs representing the fastest path. Default is None.
    """
    if not draw:
        return

    G = nx.Graph()

    # Add nodes with positions and colors based on type
    pos = {}  # Positions for nodes
    node_colors = []  # Colors for nodes
    for node in nodes.nodes.values():
        G.add_node(node.id)
        pos[node.id] = (node.longitude, node.latitude)
        
        # Color based on node type
        if node.type == 'CS':
            node_colors.append('blue')
        elif node.type == 'start':
            node_colors.append('green')
        elif node.type == 'dest':
            node_colors.append('red')
        else:  # Intersection
            node_colors.append('yellow')

    # Draw all edges with appropriate colors based on speed limit
    for edge in edges:

        if edge.speed_limit == 100:
            color = 'black'
        elif edge.speed_limit == 70:
            color = 'red'    
        elif edge.speed_limit == 40:
            color = 'lightcoral'

        nx.draw_networkx_edges(G, pos, edgelist=[(edge.node1.id, edge.node2.id)], edge_color=color, width=2)

    # Highlight the fastest path, if provided
    if fastest_path:
        fastest_path_edges = []
        for i in range(len(fastest_path) - 1):
            fastest_path_edges.append((fastest_path[i], fastest_path[i + 1]))
        
        nx.draw_networkx_edges(G, pos, edgelist=fastest_path_edges, edge_color='green', width=3)

    # Draw nodes with their colors
    nx.draw(G, pos, with_labels=True, node_size=500, node_color=node_colors, font_weight='bold')

    plt.title(title)
    plt.show()
