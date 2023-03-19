import os
# from line_profiler_pycharm import profile
from graph import *
from graph_io import *
import itertools
import time

# sys.setrecursionlimit(2000)


# @profile
# Main function to find possibly isomorphic graphs
def findPossibleIso(filelocation):
    print("--" + filelocation + "--")
    # starting time
    st = time.time()
    with open(filelocation) as f:
        filegraphs = load_graph(f, read_list=True)[0]

    # disjoint union of all graphs with a dict to know the mapping, used to later check if posIso
    uniongraph, vertmap = graphunion(filegraphs)
    # color refine the union of all graphs
    colorRefinement(uniongraph)

    # dict with graphs possibly isomorphic as key, and boolean discrete as value
    matchdict = {}

    # If two graphs are posIso you can ignore one of the two for the rest of the code. example [0,1] so we can ignore 1 for the rest of the code, transivity rule
    ignorelist = []

    # list with all combinations of graphs for this file
    graphcombinations = list(itertools.combinations(filegraphs, 2))
    # iterate through all of them and do check if they're possiblyIso using the coloring of the disjoint union and the mapping of vertices
    for graphs in graphcombinations:
        graph1nb = filegraphs.index(graphs[0])
        graph2nb = filegraphs.index(graphs[1])

        if len(graphs[0]) != len(graphs[1]):
            print("Graphs not the same amount of vertices")
        elif graph1nb in ignorelist or graph2nb in ignorelist:
            # no need to check
            continue
        else:
            match, discretebool = balancedAndDiscrete(graphs[0], graphs[1], vertmap)
            if match:
                added = False
                for isographs in list(matchdict.keys()):
                    if graph1nb in isographs:
                        # Remove this list of posIso graphs as key from the dict, and then add the same list only with graph2nb appended and discretebool as value
                        del matchdict[isographs]
                        # Newlist done this way to keep it type tuple
                        newlist = isographs + (graph2nb,)
                        # apply discrete bool
                        matchdict[newlist] = discretebool
                        ignorelist.append(graph2nb)
                        added = True
                    # Removed code with identical check for graph2, because graph1 is always the one possibly already in matchdict
                if not added:
                    matchdict[tuple([graph1nb, graph2nb])] = discretebool
                    ignorelist.append(graph2nb)

    print("Sets of possibly isomorphic graphs:")
    for isographs in matchdict.keys():
        discrete = ""
        if matchdict[isographs]:
            discrete = "discrete"
        print(str(isographs) + "  " + discrete)

    # get the execution time
    elapsed_time = time.time() - st
    print('Execution time:', round(elapsed_time, 2), 'seconds')


# Main function to find  Isomorphic graphs and their isomorphism count
def findIsomorphismCount(filelocation):
    print("--" + filelocation + "--")
    with open(filelocation) as f:
        filegraphs = load_graph(f, read_list=True)[0]

    # starting time
    st = time.time()

    # dict with list of graphs isomorphic as key and isomorphism count as value
    countdict = {}
    # If two graphs are Isomorphic you can ignore one of the two for the rest of the code. example [0,1] so we can ignore 1 for the rest of the code, transitivity rule
    ignorelist = []

    # list with all combinations of graphs for this file
    graphcombinations = list(itertools.combinations(filegraphs, 2))

    # We iterate over all the graph combinations possible in the file
    for graphcomb in graphcombinations:
        graph1nb = filegraphs.index(graphcomb[0])
        graph2nb = filegraphs.index(graphcomb[1])
        # Simple check that graphs have same nb of vertices, should never happen
        if len(graphcomb[0]) != len(graphcomb[1]):
            print("Graphs not the same amount of vertices")
        # Here we make use of the transitivity rule to avoid unneccessary calculations, use of ignorelist like described in initialization
        elif graph1nb in ignorelist or graph2nb in ignorelist:
            # no need to check because of transitivity
            continue

        # Initial coloring is all 0. Later with branching will have set unique colors for certain pairs of vertices
        initialcoloring = [0] * len(graphcomb[0].vertices * 2)

        # Here we go into the main call of countIsomorphism(). Taking the 2 graphs and the initalcoloring of 0s as params
        count = countIsomorphism(graphcomb[0], graphcomb[1], initialcoloring)

        # If isomorphic(count>0) then we adjust countdict accordingly and we can ignore graph2 further on
        # code underneath is just to update coundict(needed for print like they want) and ignorelist(for transititvity)
        if count > 0:
            added = False
            # First check if graph1 is already in one of the countdict lists, If yes then we append graph2 to that list
            for isographs in list(countdict.keys()):
                if graph1nb in isographs:
                    # Remove this list of iso graphs as key from the dict, and then add the same list only with graph2nb appended and count as value
                    del countdict[isographs]
                    # Newlist done this way to keep it type tuple
                    newlist = isographs + (graph2nb,)
                    # make value of key the count
                    countdict[newlist] = count
                    ignorelist.append(graph2nb)
                    added = True
            # If graph1 is not in any of the countdict keys then we add list with graph1 and graph2 as new entry in countdict with count as value
            if not added:
                countdict[tuple([graph1nb, graph2nb])] = count
                ignorelist.append(graph2nb)

    # We now have lists of graphs isomorphic as keys in dict and their isocount as values and we just print them all
    for isographs in countdict.keys():
        print(str(isographs) + "  " + str(countdict[isographs]))
    # get the execution time
    elapsed_time = time.time() - st
    print('Execution time:', round(elapsed_time, 2), 'seconds')


def countIsomorphism(graph1, graph2, branchcoloring):
    # available unique color depends on the depth of branch, unique colors to assign are -1,-2,...,
    # can find branchdepth with amount of branchcolorings given.
    branchdepth = (len(branchcoloring) - branchcoloring.count(0)) / 2
    availablecolor = int((branchdepth + 1) * -1)
    # At depth0 we assign -1, at depth 1(so first branching) we assign -2 etc...

    # We get the uniongraph and vertmap, for the union of the 2 graphs. (I think we could put this outside of countIsomorphism actually not sure.)
    uniongraph, vertmap = graphunion([graph1, graph2])
    # Color the uniongraph according to branchcoloring list which has a color for each vert in the uniongraph. Initially all 0s
    for vertex in uniongraph:
        vertex.colornum = branchcoloring[vertex.label]

    # Now we do colorefining on the uniongraph starting with a set coloring we just applied to it.
    # We get back the uniongraph colored to the coarsest stable partitionning. Partition is a dict with key color and value list of vertices which have that color
    uniongraph, partition = colorRefinement(uniongraph)
    # We then check if the coloring is balanced and discrete(meaning bijection)
    balanced, discrete = balancedAndDiscrete(graph1, graph2, vertmap)

    if not balanced:
        return 0
    if discrete:
        # If discrete then we have found an (actual)Isomorphism
        return 1

    # else we have to branch
    # We choose a color class with at least 4 vertices in uniongraph (so 2 in each). IMPROVEMENT branching rule, we choose the color with most vertices
    color = 0
    colorcount = 0
    for itcolor in partition.keys():
        vertices = partition[itcolor]
        if len(vertices) >= 4:
            if len(partition[itcolor]) > colorcount:
                color = itcolor
                colorcount = len(partition[itcolor])

    # for color in partition.keys():
    #     vertices = partition[color]
    #     if len(vertices) >= 4:
    #         break

    # We pick a vertex from graph1 with this color
    # There's probably diff ways to do this, but I go over all vertices in graph1 and check if the vertex that it maps to in the uniongraph has the color we want
    for vertex in graph1:
        if vertmap[vertex].colornum == color:
            branch1 = vertmap[vertex]
            break

    #We initalize num to 0
    num = 0
    # We make a copy of branchcoloring which we need later.
    # Example once we're done branching into a vertex of graph2, we have to go into branching of another vertex of graph2 if possible with the same branchcoloring as before, not the branchcoloring resulting from the first branch
    branchcoloringcopy = list(branchcoloring)

    # Now we branch with all possible verts in graph2 with this same color.
    # Meaning for all verts in graph2 with that color in uniongraph.
    # We run countisomorphism again with coloring list where we set this vertex and the vertex picked a unique color in the list
    for vertex in graph2:
        if vertmap[vertex].colornum == color:
            branch2 = vertmap[vertex]
            # We make sure branchcoloring is not the one of branching of a previous vertex in graph2
            branchcoloring = list(branchcoloringcopy)
            # Set unique color in branchcoloring list to the vertices chosen, and countIsomorphism on it
            branchcoloring[branch1.label] = availablecolor
            branchcoloring[branch2.label] = availablecolor
            count = countIsomorphism(graph1, graph2, branchcoloring)
            # if count == 1:
                # print("Depth: " + str(branchdepth))
            num = num + count

    return num


# @profile
# Refine graphs to find the coarsest stable partitioning takes uniongraph as param
def colorRefinement(uniongraph):
    # partition dict of equivalence classes. Color as key and vertices as values
    partition = {}

    highestcolornum = 0
    # # initial coloring all with their degree
    # for vertex in uniongraph.vertices:
    #     degree = len(vertex.neighbours)
    #     vertex.colornum = degree
    #     if degree not in partition.keys():
    #         partition[degree] = []
    #     partition[len(vertex.neighbours)].append(vertex)
    #     highestcolornum = max(highestcolornum, degree)
    
    # !!! Modified for branching, we color the uniongraph beforehand according to branching
    # build the color partition dict
    partition = {}
    for vertex in uniongraph.vertices:
        if vertex.colornum not in partition.keys():
            partition[vertex.colornum] = []
        partition[vertex.colornum].append(vertex)

    # coloring iteration count
    dotnumber = 0
    # Variable to check if we have recolored any vertices, meaning we are not done with colorrefinement(havent reached a stable partition)
    prevhighestcolornum = -1
    #As soon as we have unbalanced then we stop coloring
    balanced = True
    while highestcolornum != prevhighestcolornum and balanced:
        dotnumber += 1
        prevhighestcolornum = highestcolornum

        # dict for new colornum assignments for coloring to be applied after each iteration
        loopmapping = {}

        # refine all partition
        for color in partition.keys():
            # neighbour of this partition should be equal if not then give vertex diff color
            # partition's first vertex neighbours' colors to compare with
            firstneighbourcolors = []
            for neighbours in partition[color][0].neighbours:
                firstneighbourcolors.append(neighbours.colornum)
            firstneighbourcolors.sort()

            # now check if all vertices in partition have the same neighbours if not give new color
            # neighbourhoodcolor mapping neighbours colors to a newcolor, used if different neighbours but same as another vertex with different neighbours than first reference one of this equi class
            neighbourhoodcolor = {}
            for vertex in partition[color]:
                neighbourcolors = []
                for neighbours in vertex.neighbours:
                    neighbourcolors.append(neighbours.colornum)
                neighbourcolors.sort()
                # if not the same neighbours then we have to split partition, give vertex a new color
                if neighbourcolors != firstneighbourcolors:
                    # check if these diff neighbours is already seen in this color partition
                    if tuple(neighbourcolors) in neighbourhoodcolor.keys():
                        newcolor = neighbourhoodcolor[tuple(neighbourcolors)]
                        loopmapping[vertex] = newcolor
                    else:
                        highestcolornum += 1
                        loopmapping[vertex] = highestcolornum
                        neighbourhoodcolor[tuple(neighbourcolors)] = highestcolornum

        # apply the new colormapping
        for vertex in loopmapping:
            vertex.colornum = loopmapping[vertex]

        #Check if still balanced, if not then loop will stop as they wont be Iso
        balanced = checkIfBalanced(uniongraph)

        # rebuild the color partition dict
        partition = {}
        for vertex in uniongraph.vertices:
            if vertex.colornum not in partition.keys():
                partition[vertex.colornum] = []
            partition[vertex.colornum].append(vertex)

    # We now have a stable partition and return a graph with final coloring
    return uniongraph, partition


# Method used in each colorrefinment iteration to check if still Balanced coloring. To avoid coloring more unnecessarily
def checkIfBalanced(uniongraph):
    vertcount = len(uniongraph.vertices)
    colorcountdict1 = {}
    colorcountdict2 = {}
    #The first half is part of graph1 and the second half is part of graph2
    for vertex in uniongraph:
        if vertex.label < (vertcount/2):
            colorcountdict1[vertex.colornum] = colorcountdict1.get(vertex.colornum, 0) + 1
        if vertex.label >= (vertcount/2):
            colorcountdict2[vertex.colornum] = colorcountdict2.get(vertex.colornum, 0) + 1

    if colorcountdict1 == colorcountdict2:
        return True
    return False


# Method to check if coloring is balanced(so possibly iso) and if discrete(actually iso). Returns 2 booleans
def balancedAndDiscrete(graph1, graph2, vertmap):
    # We check if all the colors in first graph are unique, if yes then discrete
    # We also count the amount of vertices with each color in 2 dicts to later compare, if they're the same then possibly iso
    graph1colors = []
    discrete = True

    colorcountdict1 = {}
    colorcountdict2 = {}
    for vertex in graph1:
        vertexmapcolor = vertmap[vertex].colornum
        if vertexmapcolor in graph1colors:
            # if this color was already in graph1colors then it is not discrete
            discrete = False
        else:
            graph1colors.append(vertexmapcolor)
        colorcountdict1[vertexmapcolor] = colorcountdict1.get(vertexmapcolor, 0) + 1
    for vertex in graph2:
        vertexmapcolor = vertmap[vertex].colornum
        colorcountdict2[vertexmapcolor] = colorcountdict2.get(vertexmapcolor, 0) + 1

    if colorcountdict1 == colorcountdict2:
        match = True
        return match, discrete

    return False, False


# Method to make uniongraph out of list of graphs
def graphunion(graphslist):
    vertexlist = []
    edgelist = []
    for graph in graphslist:
        vertexlist = vertexlist + graph.vertices
        edgelist = edgelist + graph.edges

    U = Graph(False)
    vertmap = dict()
    for vertex in vertexlist:
        newvertex = Vertex(U)
        vertmap[vertex] = newvertex
        U.add_vertex(newvertex)
    for edge in edgelist:
        newvertex1 = vertmap[edge.head]
        newvertex2 = vertmap[edge.tail]
        newedge = Edge(newvertex1, newvertex2)
        U.add_edge(newedge)
    return U, vertmap


# Function to run possibleIso for all files in a folder with total execution time
def folderrun(directory):
    # starting time
    totalstarttime = time.time()
    for filename in os.listdir(directory):
        filelocation = os.path.join(directory, filename)
        # findPossibleIso(filelocation)
        findIsomorphismCount(filelocation)
    # get the execution time
    elapsedtotaltime = time.time() - totalstarttime
    print('Total execution time:', round(elapsedtotaltime, 2), 'seconds')

# folderrun("SampleGraphSetBranching")

# findIsomorphismCount("SampleGraphSetBranching/torus24.grl")
findIsomorphismCount("SampleGraphSetBranching/torus72.grl")
# findIsomorphismCount("SampleGraphSetBranching/torus144.grl")
# findIsomorphismCount("SampleGraphSetBranching/products72.grl")
# findIsomorphismCount("SampleGraphSetBranching/trees11.grl")
# findIsomorphismCount("SampleGraphSetBranching/trees36.grl")
# findIsomorphismCount("SampleGraphSetBranching/modulesD.grl")
# findIsomorphismCount("SampleGraphSetBranching/cubes3.grl")
# findIsomorphismCount("SampleGraphSetBranching/cubes5.grl")
# findIsomorphismCount("SampleGraphSetBranching/cubes6.grl")

# findIsomorphismCount("branchlecture.grl")
