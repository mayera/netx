from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import TemplateDoesNotExist
from django.views.generic.simple import direct_to_template #about_pages view
from django.shortcuts import render_to_response
#from tb.models import *
from django import forms
#from nets.forms import forms
from django.db.models import Q
from settings import *
import networkx as nx
import pydot #relative value of importing modules here vs in specific view?
import matplotlib.pyplot as plt
import matplotlib
from django.http import HttpResponse
# from django.conf import settings #needs both this and the settings * import

import re, os
import nets #.nets.nets as nets

"""Helper classes"""

class NoComponentError(Exception):
    pass

class NoConnectionError(Exception):
    pass

class FileNotFoundError(Exception):
    pass

class UploadException(Exception):
    pass

class UploadForm(forms.Form):
    file=forms.FileField(required=True)

"""Views for network tools"""

def netbase(request):
    return render_to_response('netbase.html')

def netupload(request):
    form = UploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return render_to_response('netupload.html', {'UploadException':True})

    file = request.FILES['file']
    G = nets.WebbyGraph(file)
    G.save()
    
    return render_to_response('netupload.html', {'UploadException':False})

def netstats_simple(G):
    if nx.is_connected(G): 
        d = nx.diameter(G)
        r = nx.radius(G)
    else: 
        d = 'NA - graph is not connected' #should be calculatable on unconnected graph - see example code for hack
        r = 'NA - graph is not connected'

    #using dictionary to pack values and variablesdot, eps, ps, pdf break equally
    result = {#"""single value measures"""  
        'nn': G.number_of_nodes(),
        'ne': G.number_of_edges(),
        'd': d,
        'r': r,
        'conn': nx.number_connected_components(G),
        'asp': nx.average_shortest_path_length(G), 
        'cn': nx.graph_clique_number(G), # number of the largest clique
        'mcn': nx.graph_number_of_cliques(G), # number of maximal cliques
        'tr': nx.transitivity(G), # transitivity
        'cc': nx.clustering(G), # clustering coefficient
        'avgcc': nx.average_clustering(G),
        } 
    return result

def netstats_lists(G):
    #not decided on what level to deal with this yet: 
    #either return error un not dealing with unconnected files, 
    #or making it deal with unconnected files: the latter.
    #How about with dealing with each independently.
    #    if not nx.is_connected(G):
    #        conl= nx.connected_components(G)
    #        for n in conl:
    #            turn n into graph if it isnt
    #            calculate ec, per, cnt
    #            how and when to visualise the subgraphs?
    #            iterate to next n
        
    if nx.is_connected(G):
        ec = nx.eccentricity(G) 
    else:
        ec = 'NA - graph is not connected'
    
    per = nx.periphery(G)
    cnt = nx.center(G)
    result = { #"""fast betweenness algorithm"""  
        'bbc': nx.brandes_betweenness_centrality(G),
        'tn': nx.triangles(G), # number of triangles
        'ec': ec,
        'per': per,
        'cnt': cnt,
        'Per': G.subgraph(per),
        'Cnt': G.subgraph(cnt)
        }
    return result 

def netstats_listsundi(G):
    if nx.is_connected(G): 
        conl = nx.connected_components(G) #needs work-around for unconnected subgraphs
        conl = conl.pop()
    else:
        conl = 'NA - graph is not connected'

    result = { #"""returns boolean"""
               'con': nx.is_connected(G),
               'conn': nx.number_connected_components(G), 
               'conl': conl,
               'Conl': G.subgraph(conl)
               }
    return result    

def netstats_listsdi(G):
    #   UG = nx.to_undirected(G) #claims to not have this function     
    if nx.is_strongly_connected(G): 
        sconl = nx.strongly_connected_components(G)
    else: sconl = 'NA - graph is not strongly connected'
    result = {#"""returns boolean"""
              'scon': nx.is_strongly_connected(G), 
              'sconn': nx.number_connected_components(G),
             # """returns boolean"""        
              'dag': nx.is_directed_acyclic_graph(G),
             # """returns lists"""
              'sconl': nx.strongly_connected_components(G),
              #Conl = connected_component_subgraphs(UG)
              }
    return result    

def netinfo(request):
    """Take uploaded network, find its values, output them"""
    # cleans out images, so that only the most recent upload displays: to be replaced with session handling
    format = ['png', 'svg']    
    for f in format:
        if os.path.isfile(MEDIA_ROOT + '/nets/H.' + f):
            os.remove(MEDIA_ROOT + '/nets/H.' + f)

    if os.path.isfile(os.path.join(MEDIA_ROOT, "nets", "degree_histogram.png")):
        os.remove(os.path.join(MEDIA_ROOT, "nets", "degree_histogram.png"))

    G = nets.WebbyGraph()
    if request.GET.has_key('node_zero') and request.GET.has_key('node_one'):
        G.highlight_shortest_path_between(request.GET['node_zero'], request.GET['node_one'])
    nssresult = netstats_simple(G.nx_graph)
    return render_to_response('netinfo.html', nssresult) 

def netdisplaytest(G,fprop,fformat,layout):
    #stat: speed of matlab vs pydot in generating layouts and saving
    if not os.path.isfile(NXGRAPHPATH):
        raise FileNotFoundError

    G = nets.WebbyGraph().nx_graph

    if not nx.is_connected(G):
        print 'raised \n'
        raise NoConnectionError

    nslresult = netstats_lists(G)
    test = netstats_listsundi(G)
    #print 'Showing dict:'
    #print nslresult
    #print 'Showing DICT:'  
    #print test
    #print 'Shown:'
    if not nx.is_directed(G):
        nslresult.update(test)
        #print 'Showing dircdict:'
        #print nslresult
    else:
        nslresult = dict((n, nslresult.get(n,0)) for n in set(nslresult).union(netstats_listsdi(G)))
        #print 'Showing undircdict:'
        #print nslresult
    #defines a dict for every element of the set 
    #print 'Showing added to dict test:'
    #print nslresult
    
    #    prop = fprop
    prop = nslresult[fprop]    
    layout=layout
    fformat=fformat
    #print 'prop:'
    #print prop
    #print "graph and nodes: %s %s" %(G, G.nodes())
    if prop == 0:
        #print 'raised NoComponentError\n'
        raise NoComponentError
        
    #    print "%s %s" %(prop, prop.nodes())
    #    print Per.has_node(2)
    #    Per = nx.to_pydot(Per)
  
    #    if prop = 0:
    #        return error "there are 0 of such components"

    #Creating graph
    J=nx.Graph()
    #for dealing with disconnected graphs:
    #if prop is an array 
    #then iterate over the array
    #and plot the various graphs not on top of eachother; 
    #move plt.clf() outside of the loop for this.
    for v in prop: # if I feed node lists rather than subgraphs I get a 'cant iterate over integers' complaint 
        J.add_node(v)
    for (u,v,d) in prop.edges(data=True):
        if v in prop:
            J.add_edge(u,v)
    plt.clf()
    plt.figure(1,figsize=(8,8))
    # layout graphs with positions using graphviz neato
    #    layout="neato"
    pos=nx.graphviz_layout(G,prog=layout)

    #coloring graph in with two colors supposing to sets of nodes in prop
    green = set(prop)
    red = set(G.nodes()).difference(green)
    items = [ ('r', red), ('g', green) ]
    for (color, list) in items:
        nx.draw(G, pos,
                nodelist=list,
                node_color=color,
                node_size=500,
                alpha=0.8)

    #looking into multi-coloration of graphs; 
    #this should do it instead of the above, with some fudging 
    #    pos=nx.graphviz_layout(G,prog="neato")
    # color nodes the same in each connected subgraph
    #    C=nx.connected_component_subgraphs(G)
    #    for g in C:
    #        c=[random.random()]*nx.number_of_nodes(g) # random color...
    #        nx.draw(g,
    #             pos,
    #             node_size=40,
    #             node_color=c,
    #             vmin=0.0,
    #             vmax=1.0,
    #             with_labels=False
    #             )
    plt.savefig(MEDIA_ROOT+'/nets/H.'+fformat,dpi=75)
    #        for m in Per: #or Per for J
    #            nodecol = [float(G.degree(m)) for m in J] # "g"
    #            nx.draw(G,
    #             pos,
    #             node_size=1000,
    #             node_color=nodecol,
    #             with_labels=True
    #             )
    
    # refactor the below; created via http://networkx.lanl.gov/examples/drawing/labels_and_colors.html
    #    nx.draw(G,pos,
    #            nodelist=G.nodes(),
    #            node_color='r',
    #            node_size=500,
    #            alpha=0.8) #prob. transparency
    
    #    nx.draw(G,pos,
    #            nodelist=Per,
    #            node_color='g',
    #            node_size=500,
    #            alpha=0.8)

    #        for n in conl: #works methinks
    #            nx.draw(n,
    #             pos,
    #             node_size=1000,
    #             node_color='g',
    #             vmin=0.0,
    #             vmax=1.0,
    #             with_labels=True
    #             )

    #            for m in n:
    #                m.set_color('red')
    
    # how to calculate weakly connected components? convert to
    # undirected graph; see Hongwu example. does it make sense?  does
    # matlab do all the formats in fformat? emf, eps, pdf, png, ps,
    # raw, rgba, svg, svgz - no jpg, nor dot
    
def netdisplay(request): #based on showpathgraph
    if not os.path.isfile(NXGRAPHPATH):
        raise FileNotFoundError

    G = nets.WebbyGraph() #.nx_graph
    class ShortestPathForm(forms.Form):
        node_one = forms.ChoiceField(label="First Node", choices=G.node_choices(), required=True)
        node_two = forms.ChoiceField(label="Second Node", choices=G.node_choices(), required=True)
        def clean(self):
            cleaned_data = self.cleaned_data
            if cleaned_data.get('node_one') and cleaned_data.get('node_two') and (
                cleaned_data.get('node_one') == cleaned_data.get('node_two') ):
                raise forms.ValidationError("Please choose two different nodes")
            return cleaned_data
                    

    if request.method == 'POST':
        shortest_path_form = ShortestPathForm(request.POST)
        if shortest_path_form.is_valid():
            highlighted_node_one = shortest_path_form.cleaned_data['node_one']
            highlighted_node_two = shortest_path_form.cleaned_data['node_two']
            G.highlight_shortest_path_between(highlighted_node_one, highlighted_node_two)
        form = netdispform(request.POST)
        return render_to_response('netinfo.html', locals())
    elif request.method == 'GET':
        shortest_path_form = ShortestPathForm()
        f = netdispform()
        return render_to_response('netinfo.html', {'form': f, 'shortest_path_form': shortest_path_form})

        f = netdispform(request.GET)
        if not f.is_valid():
           return render_to_response('netinfo.html', {'form': f}) #do sth else
        else:
           if f.cleaned_data["fformat"]:
              fformat=f.cleaned_data["fformat"] #not sure this is working; uncommenting fformat = 'svg' makes difference^M
           else:   
              fformat='png' #was jpg but not yet supported via matlab netdisplaytest; might be the httpresponse error cause
 
           if f.cleaned_data["layout"]:
              layout=f.cleaned_data["layout"]
           else:   
              layout='dot'
           if f.cleaned_data["fprop"]:
              fprop=f.cleaned_data["fprop"]
           else:   
              fprop='Cnt'

           print 'fprop here:' + fprop
           pname = 'H'
           #           fformat = 'png'
           #           layout = 'neato'

           try:
               netdisplaytest(G,fprop,fformat,layout)
           except NoConnectionError:
               return render_to_response("netinfo.html", {'form':f,'format':fformat,'pname':pname,'noComponent':False,'noConnection':True})
           except NoComponentError:
               return render_to_response("netinfo.html", {'form':f,'format':fformat,'pname':pname,'noComponent':True, 'noConnection':False})

           return render_to_response("netinfo.html", {'form':f,'format':fformat,'pname':pname, 'noComponent':False, 'noConnection':False})


class netdispform(forms.Form):  #needs to be solved differently
    if os.path.isfile(NXGRAPHPATH):
        G=nx.read_adjlist(NXGRAPHPATH)
        if nx.is_directed(G):
            props= ('sconl', 'Strongly connected components')
            #       nslundiresult = netstats_listsundi(G)
        else:
            #        nsldiresult = netstats_listsdi(G)
            props= ('Conl', 'Connected components')
    else: 
        props= ('Conl', 'Connected components')
    foptions=[('png','png'),('svg','svg')]
    #,('eps','eps'),('ps','ps'),('pdf','pdf')] # are theoretically supported but actually don't work: in firefox, using the current setup
    poptions=[('dot','dot'),('neato','neato'),('twopi','twopi'),('circo','circo'),('fdp','fdp')]
    
    fprops=[('Cnt','center'), ('Per','periphery'), props]
    fprop=forms.ChoiceField(label="",choices=fprops,required=False)
    fformat=forms.ChoiceField(label="format", choices=foptions,required=False)
    layout=forms.ChoiceField(label="layout", choices=poptions,required=False)

def degreedist(request):
    """
    Random graph from given degree sequence.
    Draw degree histogram with matplotlib.

    Based on degree_histogram.pb by Aric Hagberg (hagberg@lanl.gov)
    """

    G = nets.WebbyGraph().nx_graph

    degree_sequence=sorted(nx.degree(G),reverse=True) # degree sequence
    # print "Degree sequence", degree_sequence
    dmax=max(degree_sequence)
    plt.clf()
    plt.loglog(degree_sequence,'b-',marker='o')
    plt.title("Degree rank plot")
    plt.ylabel("degree")
    plt.xlabel("rank")

    # draw graph in inset
    plt.axes([0.45,0.45,0.45,0.45])
    Gcc=nx.connected_component_subgraphs(G)[0]
    pos=nx.spring_layout(Gcc)
    plt.axis('off')
    nx.draw_networkx_nodes(Gcc,pos,node_size=20)
    nx.draw_networkx_edges(Gcc,pos,alpha=0.4)

    plt.savefig(MEDIA_ROOT+"/nets/degree_histogram.png", dpi=50)

    #    plt.show()
    return render_to_response('netinfo.html', locals())


"""
multiple values returned: sets of nodes or edges, paths,..., or graph 
objects etc, display to be suited
    a = nx.single_source_shortest_path_length(G,go,cutoff=None)
"""
  

"""Read in graphs of various formats"""
"""read in form data on what the input format is: test that assertion
def readgraph(request, filetype): this needs a URL
    if 'pathn' in request.POST:
        message = 'You uploaded: %r' % request.POST['pathn']
        H=nx.read_adjlist(%r) % request.POST['pathn']
    else:
        message = 'You must enter a path to you graph file to upload it.'
    return HttpResponse(message)

  """

"""Graphic interface for node information - click on two nodes and return shortest path etc - what kind of annotated graph object would be required?"""

"""Tests on more than one graph - isomorphism, etc."""



