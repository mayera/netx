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

#from django.conf import settings #needs both this and the settings * import

import re
import os

#base_dir=settings.BASE_DIR
graphpath = MEDIA_ROOT+"/nets/test.adjlist"

"""Views for network tools"""


def netbase(request):
    return render_to_response('netbase.html')


class UploadException(Exception):
    pass

def netupload(request):
    # Create a form and validate it
    form = UploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return render_to_response('netupload.html', {'UploadException':True})
        raise UploadException, "Invalid form"


    # Identify the correct read/write functions based on regular expressions
    file = request.FILES['file']
    formats = [ (".*\.adjlist", nx.read_adjlist, nx.write_adjlist) ]
    read, write = None, None
    for f in formats:
        if re.match(f[0], file.name):
            read, write = f[1], f[2]
            break

    # If we have not found a known format, abort
    if not read:
        raise UploadException, "Unknown format"

    # Attempt to read in the graph.
    try:
        G = read(file)
    except Exception, e:
        # Just propagate any errors for the moment.
        # Later we should inform the user.
        #raise e
        return render_to_response('netupload.html', {'UploadException':True})

    # Store the uploaded graph.
#    path = os.path.join(MEDIA_ROOT, 'nets/test.adjlist') #settings.GRAPH_DIR, 'graph.gml.bz2')
#    nx.write_gml(G, path)
    
    nx.write_adjlist(G, graphpath)
    return render_to_response('netupload.html', {'UploadException':False})


class UploadException(Exception):
    pass


#def handle_uploaded_file(f):
## dostuffwithfilelike clean read convert output graph or error)
##    f = request.FILES['file'] #seems to be the name of the file; unicode object
#    fread = f.read() #is the content of the file; string - .readlines() will stick in newlinesr/n
#    fsize = f.size #in bits
#    fname = f.name
##   gmlfile = fread.parse_gml()
##    G = fread.from_edgelist()
#    return (fread, fsize, fname)


#number and letters for validation - no control characters
#generate name perhaps by hashing or date

class UploadForm(forms.Form):
    file=forms.FileField(required=True)

def netstats_simple(graph):
    G = graph
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
#              """number of the largest clique"""
              'cn': nx.graph_clique_number(G),
#              """number of maximal cliques"""
              'mcn': nx.graph_number_of_cliques(G),
#              """transitivity - """
              'tr': nx.transitivity(G),
              #cc = nx.clustering(G) """clustering coefficient"""
              'avgcc': nx.average_clustering(G) } 
#    result['d'] = nx.diameter(G)
    print result
    return result


def netstats_lists(graph):
    G = graph
    """return lists"""
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
        
    per = nx.periphery(G)
    cnt = nx.center(G) 

    if nx.is_connected(G):
        ec = nx.eccentricity(G) 
    else: ec = 'NA - graph is not connected'
    
    result = { #"""fast betweenness algorithm"""  
               'bbc': nx.brandes_betweenness_centrality(G),
#              """number of triangles"""
               'tn': nx.triangles(G),
               'ec': ec,
               'per': per,
               'cnt': cnt,
               'Per': G.subgraph(per),
               'Cnt': G.subgraph(cnt)
               }
    return result 

def netstats_listsundi(graph):
    G = graph
    if nx.is_connected(G): 
        conl= nx.connected_components(G)
        print "conl: "
        print conl
        conl = conl.pop()
  #      print "conl: "
        print conl
    else: conl = 'NA - graph is not connected'

    result = { #"""returns boolean"""
               'con': nx.is_connected(G),
               'conn': nx.number_connected_components(G), 
               'conl': conl,
               'Conl': G.subgraph(conl)
               }
    return result    

def netstats_listsdi(graph):
    G = graph
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
#              Conl = connected_component_subgraphs(UG)
              }
    return result    

def netinfo(request):
    """Take uploaded network, find its values, output them"""
#    cleans out images, so that only the most recent upload displays: to be replaced with session handling
    format = ['png', 'svg']    
    for f in format:
        if os.path.isfile(MEDIA_ROOT + '/nets/H.' + f):
            os.remove(MEDIA_ROOT + '/nets/H.' + f)

    if os.path.isfile(MEDIA_ROOT+"/nets/degree_histogram.png"):
        os.remove(os.path.join(MEDIA_ROOT+"/nets/degree_histogram.png"))

   #Generate graph
#    G = nx.petersen_graph()
#    G=nx.path_graph(12)
#    G=nx.random_geometric_graph(50,0.125)

   # Store the generated graph.
#    path = os.path.join(MEDIA_ROOT, 'nets/test.adjlist') #settings.GRAPH_DIR, 'graph.gml.bz2')
#    nx.write_gml(G, path)
    G=nx.read_adjlist(MEDIA_ROOT+"/nets/test.adjlist")
#    nx.write_adjlist(G, path)

    nssresult = netstats_simple(G)
#    raise fromInfo
#    try:
#        true
#    except fromInfo:
    return render_to_response('netinfo.html', nssresult) 
#, 'fromInfo':True})

#so might speak against returned 'request' here, together with the others vars by using locals?
#and how to get around that? 
#so, optimally, I want to pass netdisplay what graph and state I want it to display, and in what format and layout
 
#class fromInfo(Exception): #it isn't an exception: what's my options?
#    pass

class NoComponentError(Exception):
    pass

class NoConnectionError(Exception):
    pass

class FileNotFoundError(Exception):
    pass

def netdisplaytest(G,fprop,fformat,layout):
#stat: speed of matlab vs pydot in generating layouts and saving
    if not os.path.isfile(graphpath):
        raise FileNotFoundError

    G=nx.read_adjlist(graphpath)
#    G = nx.read_gml(BASE_DIR+'/halftoy.gml') #doesn't read cytoscape gml; prob too much annotation - perhaps parseable via external library

    if not nx.is_connected(G):
        print 'raised \n'
        raise NoConnectionError

    nslresult = netstats_lists(G)
    test = netstats_listsundi(G)
    print 'Showing dict:'
    print nslresult
    print 'Showing DICT:'  
    print test
    print 'Shown:'
    if not nx.is_directed(G):
        nslresult.update(test)
        print 'Showing dircdict:'
        print nslresult
    else:
        nslresult = dict((n, nslresult.get(n,0)) for n in set(nslresult).union(netstats_listsdi(G)))
        print 'Showing undircdict:'
        print nslresult
#defines a dict for every element of the set 
    print 'Showing added to dict test:'
    print nslresult
    
#    prop = fprop
    prop = nslresult[fprop]    
    layout=layout
    fformat=fformat
    print 'prop:'
    print prop
    print "graph and nodes: %s %s" %(G, G.nodes())
    if prop == 0:
        print 'raised NoComponentError\n'
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

    plt.savefig(MEDIA_ROOT+'/nets/H.'+fformat,dpi=75)

#        for m in Per: #or Per for J
#            nodecol = [float(G.degree(m)) for m in J] # "g"
#            nx.draw(G,
#             pos,
#             node_size=1000,
#             node_color=nodecol,
#             with_labels=True
#             )

#refactor the below; created via http://networkx.lanl.gov/examples/drawing/labels_and_colors.html
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
##             vmin=0.0,
##             vmax=1.0,
#             with_labels=True
#             )

#            for m in n:
#                m.set_color('red')

#how to calculate weakly connected components? convert to undirected graph...
#does matlab do all the formats in fformat? emf, eps, pdf, png, ps, raw, rgba, svg, svgz - no jpg, nor dot
    
def netdisplay(request): #based on showpathgraph
    if not os.path.isfile(graphpath):
        raise FileNotFoundError
     #   return render_to_response('netinfo.html', {'FileNotFoundError': True}) #do sth else

    G=nx.read_adjlist(graphpath)
    if request.method == 'GET':
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

#           G = nx.path_graph(7)
           print 'fprop here:' + fprop
           pname = 'H'
#           fformat = 'png'
#           layout = 'neato'
#           print fprop

           try:
               netdisplaytest(G,fprop,fformat,layout)
           except NoConnectionError:
               return render_to_response("netinfo.html", {'form':f,'format':fformat,'pname':pname,'noComponent':False,'noConnection':True})
           except NoComponentError:
               return render_to_response("netinfo.html", {'form':f,'format':fformat,'pname':pname,'noComponent':True, 'noConnection':False})
           print 'fformat: '
           print fformat

           return render_to_response("netinfo.html", {'form':f,'format':fformat,'pname':pname, 'noComponent':False, 'noConnection':False})


class netdispform(forms.Form):  #needs to be solved differently
    if os.path.isfile(graphpath):
        G=nx.read_adjlist(graphpath)
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

#    G = nx.star_graph(44)
#    G = nx.path_graph(10)
#    G = nx.petersen_graph() 
#    G=nx.random_geometric_graph(50,0.125)

    G=nx.read_adjlist(MEDIA_ROOT+"/nets/test.adjlist")

    degree_sequence=sorted(nx.degree(G),reverse=True) # degree sequence
#print "Degree sequence", degree_sequence
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



