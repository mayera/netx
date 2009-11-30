import re, types, pygraphviz, os
import networkx as nx
import matplotlib.pyplot as pyplot
import settings

class NetworkParseException(Exception):
    pass
class NoConnectionError(Exception):
    pass
class NoComponentError(Exception):
    pass

class WebbyGraph:

    def __init__(self, nx_graph = settings.NXGRAPHPATH):
        self.nx_graph = load_net(nx_graph)

    def node_choices(self):
        return [(n, n) for n in self.nx_graph.nodes()]

    def highlight_shortest_path_between(self, n1, n2):
        self.highlighted_nodes = nx.shortest_path(self.nx_graph, n1, n2)
        self.draw()
        
    def draw(self, fformat='png', layout='dot', fprop='Cnt'):
        if not nx.is_connected(self.nx_graph):
            raise NoConnectionError

        self.fformat = fformat
        prop = self.basic_stats()[fprop]
        tmp_graph = nx.Graph()
        if prop == 0:
            raise NoComponentError
        #for dealing with disconnected graphs:
        #if prop is an array 
        #then iterate over the array
        #and plot the various graphs not on top of eachother; 
        #move pyplot.clf() outside of the loop for this.
        for node in prop: # if I feed node lists rather than subgraphs I get a 'cant iterate over integers' complaint 
            tmp_graph.add_node(node)
        for (u, node, d) in prop.edges(data=True):
            if node in prop:
                tmp_graph.add_edge(u, node)
        pyplot.clf()
        pyplot.figure(1, figsize=(8,8))
        # layout graphs with positions using graphviz neato
        #    layout="neato"
        pos = nx.graphviz_layout(self.nx_graph, prog=layout)

        #coloring graph in with two colors supposing to sets of nodes in prop
        green = set(prop)
        red = set(self.nx_graph.nodes()).difference(green)
        items = [ ('r', red), ('g', green) ]
        for (color, list) in items:
            nx.draw(self.nx_graph, pos,
                    nodelist=list,
                    node_color=color,
                    node_size=500,
                    alpha=0.8)
        pyplot.savefig(settings.MEDIA_ROOT + '/nets/' + self.pname() + '.' + fformat, dpi=75)

    def pname(self):
        return 'H'

    def basic_stats(self):
        #not decided on what level to deal with this yet:
        #either return error un not dealing with unconnected files,
        #or making it deal with unconnected files: the latter.
        #How about with dealing with each independently.
        #    if not nx.is_connected(g):
        #        conl= nx.connected_components(g)
        #        for n in conl:
        #            turn n into graph if it isnt
        #            calculate ec, per, cnt
        #            how and when to visualise the subgraphs?
        #            iterate to next n

        if nx.is_connected(self.nx_graph):
            ec = nx.eccentricity(self.nx_graph) 
        else:
            ec = 'NA - graph is not connected'

        per = nx.periphery(self.nx_graph)
        cnt = nx.center(self.nx_graph)
        result = { #"""fast betweenness algorithm"""  
            'bbc': nx.brandes_betweenness_centrality(self.nx_graph),
            'tn': nx.triangles(self.nx_graph), # number of triangles
            'ec': ec,
            'per': per,
            'cnt': cnt,
            'Per': self.nx_graph.subgraph(per),
            'Cnt': self.nx_graph.subgraph(cnt)
            }
        return result

    def undirected_stats(self):
        if nx.is_connected(self.nx_graph):
            conl = nx.connected_components(self.nx_graph) #needs work-around for unconnected subgraphs
            conl = conl.pop()
        else:
            conl = 'NA - graph is not connected'

        result = { #"""returns boolean"""
            'con': nx.is_connected(self.nx_graph),
            'conn': nx.number_connected_components(self.nx_graph), 
            'conl': conl,
            'Conl': g.subgraph(conl)
            }
        return result

    def directed_stats(self):
        #   UG = nx.to_undirected(g) #claims to not have this function     
        if nx.is_strongly_connected(g): 
            sconl = nx.strongly_connected_components(g)
        else: sconl = 'NA - graph is not strongly connected'
        result = {#"""returns boolean"""
            'scon': nx.is_strongly_connected(g), 
            'sconn': nx.number_connected_components(g),
            # """returns boolean"""        
            'dag': nx.is_directed_acyclic_graph(g),
            # """returns lists"""
            'sconl': nx.strongly_connected_components(g),
            #Conl = connected_component_subgraphs(Ug)
            }
        return result

    def save(self):
        self.save_nx_graph()

    def save_nx_graph(self):
        nx.write_adjlist(self.nx_graph, settings.NXGRAPHPATH)

def load_net(f):
    if type(f) in types.StringTypes:
        return load_net_from_string(f)
    else:
        return load_net_from_file(f)


def load_net_from_string(s):
    format = re.match(".*\.([a-zA-Z]+)$", s)
    if format:
        read_name = "read_" + format.groups()[0]
        if nx.__dict__.has_key(read_name):
            read = nx.__dict__[read_name]
            g = read(s)
            return(g)
    return try_all_readers_on(s)

def load_net_from_file(f):
    return try_all_readers_on(f)

def try_all_readers_on(f):
    for method in nx.__dict__.keys():
        if type(f) not in types.StringTypes:
            f.seek(0)
        #:MC: read_dot segfaults (yes, segfaults) on read failures...
        if re.match('^read_(?!dot)', method):
            g = None
            try:
                g = getattr(nx, method)(f)
            except:
                pass
            if g and g.size() > 0:
                return g
    raise NetworkParseException("Unparseable file format")
