import re, types, pygraphviz, os
import networkx as nx
import settings

class NetworkParseException(Exception):
    pass

class WebbyGraph:

    def __init__(self, nx_graph = settings.NXGRAPHPATH):
        self.nx_graph = load_net(nx_graph)

    def node_choices(self):
        return [(n, n) for n in self.nx_graph.nodes()]

    def highlight_shortest_path_between(self, n1, n2):
        path = nx.shortest_path(self.nx_graph, n1, n2)

        def colorize(thing):
            for att in thing.attr.items():
                name, val = att
                if re.search('draw', name):
                    thing.attr[name], unused_count = re.subn('-black', '-green', val)

        #         for node in self.canviz_output().nodes():
        #             if node.title() in path:
        #                 colorize(node)
        #         for edge in self.canviz_output().edges():
        #             if edge[0] in path and edge[1] in path:
        #                 colorize(edge)
        #         self.save_canviz_graph()

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
