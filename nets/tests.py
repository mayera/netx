import os, re

import human.nets.nets as nets
import networkx as nx

from django.test import TestCase, Client

test_net_path = os.path.join(os.path.dirname(__file__), 'files')

class NetsTests(TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_posting_a_file_to_netupload(self):
        c = Client()
        resp = c.post('/nets/netupload/', {'file':open(os.path.join(test_net_path, 'test.adjlist'))})
        self.assertContains(resp, "uploaded")

    def test_load_net_should_load_known_net_types(self):
        files = ['test.adjlist', 'test.gml', 'test.edgelist']
        for name in files:
            try:
                g = nets.load_net(os.path.join(test_net_path, name))
            except Exception, e:
                raise Exception("'%s' failed to parse: %s" % (name, e))
            self.assertEqual(11, g.size())

    def _test_should_load_nets_from_file_streams(self):
        #:MC: this does not work properly with read_adjlist (at least).  it returns 0-sized nets.
        f = open(os.path.join(test_net_path, 'test.adjlist'))
        g = nets.load_net(f)
        self.assertEqual(11, g.size())
        f.close()

    def test_load_net_should_try_to_load_poorly_name_files(self):
        files = ['poorly_named', 'a.net.in.some.format', 'a']
        for name in files:
            g = nets.load_net(os.path.join(test_net_path, name))
            self.assertEqual(11, g.size(), '%s should have 11 nodes, has %d' % (name, g.size()))

    def test_load_net_should_raise_on_unknown_net_types(self):
        files = ['unknown.format', 'nonexistant_file.dot', 'garbage.gml']
        #:MC: at the moment, this should break a bunch
        for name in files:
            self.assertRaises(Exception, nets.load_net, os.path.join(test_net_path, name))

    def test_WebbyGraph_should_init_from_filename(self):
        g = nets.WebbyGraph(os.path.join(test_net_path, 'test.adjlist'))
        self.assert_(type(g.nx_graph) == nx.Graph)

    def test_should_color_green_for_shortest_path(self):
        # this test relies on the test data being connected correctly
        g = nets.WebbyGraph(os.path.join(test_net_path, 'test.adjlist'))
        n1 = '2'
        n2 = '9'
        g.highlight_shortest_path_between(n1, n2)
        onscreen = g.canviz_output()
        green_patt = re.compile('-green')
        black_patt = re.compile('-black')
        for n in onscreen.nodes():
            if int(n.title()) in xrange(2,10):
                self.assert_(green_patt.search(n.attr['_draw_']), 'Node %s should be green in "%s"' % (n.title(), n.attr['_draw_']))
            else:
                self.assert_(black_patt.search(n.attr['_draw_']), 'Node %s should be black in "%s"' % (n.title(), n.attr['_draw_']))
        for e in onscreen.edges():
            if int(e[0]) in xrange(2,10) and int(e[1]) in xrange(2,10):
                self.assert_(green_patt.search(e.attr['_draw_']), 'Edge %s should be green in "%s"' % (e, e.attr['_draw_']))
            else:
                self.assert_(black_patt.search(e.attr['_draw_']), 'Edge %s should be black in "%s"' % (e, e.attr['_draw_']))
