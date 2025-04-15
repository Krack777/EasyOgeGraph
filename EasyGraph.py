from typing import Optional
import networkx as nx
import matplotlib.pyplot as plt

class EasyGraph:
    def __init__(self, edges : list, thripleroute: Optional[bool] = False):
        self.Graph = nx.Graph()
        self.edges = edges
        self.thripleroute = thripleroute
        self.Graph.add_weighted_edges_from(self.edges)

    def task(self, pointA: str, pointB: str, pointC: Optional[int] = None):
        if self.thripleroute == True:
            part1 = nx.shortest_path(self.Graph, pointA, pointB, weight='weight')
            part2 = nx.shortest_path_length(self.Graph, pointB, pointC, weight='weight')
            full_route = part1 + part2[1:]
            route_length = nx.path_weight(self.Graph, full_route, weight='weight')

            return route_length, full_route

        if self.thripleroute == False:
            route = nx.shortest_path(self.Graph, pointA, pointB, weight='weight')
            route_length = nx.path_weight(self.Graph, route, weight='weight')

            return route_length, route

    def make(self, route: list, filename: str):
        route_edges = [(route[i], route[i + 1]) for i in range(len(route) - 1)]
        pos = nx.spring_layout(self.Graph)
        nx.draw(self.Graph, pos, with_labels=True, node_color='grey', node_size=1000, font_size=16) # make grey graph
        nx.draw_networkx_edges(self.Graph, pos, edge_color='black', width=2) # unused edges
        nx.draw_networkx_edges(self.Graph, pos, edgelist=route_edges, edge_color='red', width=4) # used in route edges
        nx.draw_networkx_edge_labels(self.Graph, pos, edge_labels={(pos1, pos2): dict['weight'] for pos1, pos2, dict in self.Graph.edges(data=True)}) # combining nodes and edges
        nx.draw_networkx_nodes(self.Graph, pos, nodelist=route, node_color='red') # used in route nodes
        plt.savefig(f"pics\\{filename}.png", format="png", dpi=300, bbox_inches="tight")
        plt.show()

    def textmaker(self, route_length: int, route: list):
        visual_route = ""
        for i in range(len(route)):
            visual_route += "->" + route[i]
        return f"Длинна пути - {route_length}", f"Маршрут - {visual_route[2:]}"