import os
# from line_profiler_pycharm import profile
from graph import *
from graph_io import *
import itertools
import time


# sys.setrecursionlimit(2000)

# Main function to find  Isomorphic graphs and their isomorphism count
def findIsomorphismCount(filelocation, mode):
    # The function has 3 modes: 1 to just find AUT#, 2 to find both, 3 to just find Iso

    print("--" + filelocation + "--")
    with open(filelocation) as f:
        filegraphs = load_graph(f, read_list=True)[0]

    # starting time
    st = time.time()

    # dict with list of graphs isomorphic as key and isomorphism count as value
    countdict = {}

    if mode == 1:
        for graph in filegraphs:
            countdict[filegraphs.index(graph)] = 0
    else:
        # If mode 2 or 3 then we want the isomorphic graphs lists
        # If two graphs are Isomorphic you can ignore one of the two for the rest of the code. example [0,1] so we can ignore 1 for the rest of the code, transitivity rule
        ignorelist = []

        # list with all combinations of graphs for this file
        graphcombinations = list(itertools.combinations(filegraphs, 2))

        # We iterate over all the graph combinations possible in the file and find isomorphic graphs
        for graphcomb in graphcombinations:
            graph1nb = filegraphs.index(graphcomb[0])
            graph2nb = filegraphs.index(graphcomb[1])
            # Simple check that graphs have same nb of vertices, should never happen
            if len(graphcomb[0]) != len(graphcomb[1]):
                # print("Graphs not the same amount of vertices")
                continue
            # Here we make use of the transitivity rule to avoid unneccessary calculations, use of ignorelist like described in initialization
            elif graph1nb in ignorelist or graph2nb in ignorelist:
                # no need to check because of transitivity
                continue

            initialcoloring = [0] * len(graphcomb[0].vertices * 2)
            # Here we go into the main call of countIsomorphism(). Taking the 2 graphs and the initalcoloring as params. And indicating we simply want to know if an Isoexists
            count = countIsomorphism(graphcomb[0], graphcomb[1], initialcoloring, False)

            # After having done branching and counting, if graphs are isomorphic(count>0) then we adjust countdict accordingly, and we can ignore graph2 further on
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

    if mode == 2:
        # Now we have list of isographs we can calculate the number of automorphisms for each
        for isographs in countdict.keys():
            graph1 = filegraphs[isographs[0]]
            # Preprocessing of graphs
            initialcoloring = preProcessGraph(graph1)
            # initialcoloring = [0] * len(graph1.vertices * 2)
            count = countIsomorphism(graph1, graph1, initialcoloring, True)
            countdict[isographs] = count
    elif mode == 1:
        for graphnb in countdict.keys():
            graph = filegraphs[graphnb]
            # Preprocessing of graphs
            initialcoloring = preProcessGraph(graph)
            # initialcoloring = [0] * len(graph.vertices * 2)
            count = countIsomorphism(graph, graph, initialcoloring, True)
            countdict[graphnb] = count
    else:
        for isographs in countdict.keys():
            countdict[isographs] = ""

    # We now have lists of graphs isomorphic as keys in dict and their isocount as values, and we just print them all
    for isographs in countdict.keys():
        print(str(isographs) + "  " + str(countdict[isographs]))
    # get the execution time
    elapsed_time = time.time() - st
    print('Execution time:', round(elapsed_time, 2), 'seconds')


# Method to preprocess graphs and remove false twins.
# We return a coloring of union of graph to itself to use in countIsomorphism.
def preProcessGraph(graph1):
    # We do a first colorrefinment with colornum=degree of vertex
    uniongraph, vertmap = graphunion([graph1, graph1])
    for vertex in uniongraph:
        vertex.colornum = vertex.degree
    uniongraph, partition = colorRefinement(uniongraph)

    # In this dict we will put vertices as keys, and their list of twins as key
    twindict = {}

    coloringlist = []
    # We build coloringlist from colorrefined uniongraph.
    # half since we only need to check false twins once, and we adapt coloring list of the first part of the union. Later we just double the list to get our full coloringlist for countIso
    for vertex in uniongraph.vertices[:len(uniongraph.vertices)//2]:
        coloringlist.append(vertex.colornum)

    availablecolor = max(coloringlist) + 1

    # dict with falsetwins boolean for each vertices

    # for vertex in graph1:


    # We no now check for falsetwins and give them unique colors
    # We iterate though all colors
    for color in partition.keys():

        if len(partition[color]) < 4:
            # If less than 2 vertices per graph in color class then there's no twins, so we continue
            continue


        # list with vertices already seen, so to ignore
        ignorelist = []
        # We go through each color class and check for false twins in the first half of the union graph(we could also choose the 2nd half since same graphs)
        vertices = partition[color][:len(partition[color])//2]
        for vert1 in vertices:
            if vert1.label not in ignorelist:
                ignorelist.append(vert1.label)
                vert1neighbours = set(vert1.neighbours)

                for vert2 in vertices:
                    if vert2.label not in ignorelist:
                        vert2neighbours = set(vert2.neighbours)
                        vert1neighbourswithanditself = vert1.neighbours.append(vert1)
                        vert2neighbourswithanditself = vert2.neighbours.append(vert2)

                        if vert1neighbours == vert2neighbours:
                        # if vert1neighbourswithanditself == vert2neighbourswithanditself:
                            print("False twins detected")
                            # Then they are false twins
                            coloringlist[vert1.label] = availablecolor
                            coloringlist[vert2.label] = availablecolor+1
                            availablecolor += 2
                            ignorelist.append(vert2.label)
                        # Now if they're real twins then we can add vert2inunion to ignore list
                        # elif vert1neighbourswithanditself == vert2neighbourswithanditself:
                        #     ignorelist.append(vert2.label)

    # Now we have coloring for graph with false twins handled, so we just double the list to get full coloringlist for countIso
    coloringlist = coloringlist+coloringlist

        # # First we check false twins in graph1
        # for vert1 in graph1.vertices:
        #     vert1inunion = vertmap[vert1]
        #     if vert1inunion.label not in ignorelist and vert1inunion in partition[color]:
        #         # So we have now found a vertex from graph1 that has the color we want in the uniongraph and that is not in ignorelist
        #         # we then will go through other vertices in graph1 in this same color to find false twins
        #         ignorelist.append(vert1inunion.label)
        #         vert1neighbours = set(vert1inunion.neighbours)
        #
        #         for vert2 in graph1.vertices:
        #             vert2inunion = vertmap[vert2]
        #             if vert2inunion.label not in ignorelist and vert2inunion in partition[color]:
        #                 vert2neighbours = set(vert2inunion.neighbours)
        #                 vert1neighbourswithanditself = vert1inunion.neighbours.append(vert1inunion)
        #                 vert2neighbourswithanditself = vert2inunion.neighbours.append(vert2inunion)
        #
        #                 if vert1neighbours == vert2neighbours:
        #                     # Then they are false twins
        #                     coloringlist[vert2inunion.label] = colorfortwin
        #                     colorfortwin += 1
        #                     ignorelist.append(vert2inunion.label)
        #
        #                 # # Now if they're real twins then we can add vert2inunion to ignore list
        #                 # elif vert1neighbourswithanditself == vert2neighbourswithanditself:
        #                 #     ignorelist.append(vert2inunion.label)
        #     # we have checked for all vertices in graph1 if they are false twins of vert1 of graph1

        # # We have now checked all false twins in graph1 for this color, and we do the same for graph2
        # colorfortwin = availablecolor
        # for vert1 in graph2.vertices:
        #     vert1inunion = vertmap[vert1]
        #     if vert1inunion.label not in ignorelist and vert1inunion in partition[color]:
        #         ignorelist.append(vert1inunion.label)
        #         vert1neighbours = set(vert1inunion.neighbours)
        #
        #         for vert2 in graph2.vertices:
        #             vert2inunion = vertmap[vert2]
        #             if vert2inunion.label not in ignorelist and vert2inunion in partition[color]:
        #                 vert2neighbours = set(vert2inunion.neighbours)
        #                 vert1neighbourswithanditself = vert1inunion.neighbours.append(vert1inunion)
        #                 vert2neighbourswithanditself = vert2inunion.neighbours.append(vert2inunion)
        #
        #                 if vert1neighbours == vert2neighbours:
        #                     # Then they are false twins
        #                     coloringlist[vert2inunion.label] = colorfortwin
        #                     colorfortwin += 1
        #                     ignorelist.append(vert2inunion.label)
        #
        #                 # # Now if they're real twins then we can add vert2inunion to ignore list
        #                 # elif vert1neighbourswithanditself == vert2neighbourswithanditself:
        #                 #     ignorelist.append(vert2inunion.label)
    print("PreProcess done")
    return coloringlist


def countIsomorphism(graph1, graph2, branchcoloring, automorphism):
    # This function can count the number of isomorphisms(used to find AUT#), but also used to simply check if an isomorphism exists depending on automorphism boolean

    # available unique color depends on the depth of branch, unique colors to assign are -1,-2,...,
    # can find branchdepth with amount of branchcolorings given.
    # branchdepth = (len(branchcoloring) - branchcoloring.count(0)) / 2
    # availablecolor = int((branchdepth + 1) * -1)
    # At depth0 we assign -1, at depth 1(so first branching) we assign -2 etc...

    # We give negative numbers for branching, so the available number is the min in branchcoloring-1
    availablecolor = min(branchcoloring) - 1

    # We get the uniongraph and vertmap, for the union of the 2 graphs. (I think we could put this outside of countIsomorphism actually not sure.)
    uniongraph, vertmap = graphunion([graph1, graph2])
    # Color the uniongraph according to branchcoloring list which has a color for each vert in the uniongraph.
    for vertex in uniongraph:
        vertex.colornum = branchcoloring[vertex.label]

    # Now we do colorefining on the uniongraph starting with a set coloring we just applied to it.
    # We get back the uniongraph colored to the coarsest stable partitionning. Partition is a dict with key color and value list of vertices which have that color
    uniongraph, partition = colorRefinement(uniongraph)
    # We then check if the coloring is balanced and discrete(meaning bijection)
    balanced, discrete = balancedAndDiscrete(uniongraph)

    if not balanced:
        return 0
    if discrete:
        # If discrete then we have found an (actual)Isomorphism
        return 1
    # else we have to branch

    # We choose a color class with at least 4 vertices in uniongraph (so 2 in each).
    # IMPROVEMENT branching rule, we choose the color with most vertices
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
    # for vertex in graph1:
    #     if vertmap[vertex].colornum == color:
    #         branch1 = vertmap[vertex]
    #         break

    # To work with graph on union of itself we avoid vertmap, first half of vertices is graph1
    graphlen = len(uniongraph.vertices)
    for i in range(int(graphlen / 2)):
        if uniongraph.vertices[i].colornum == color:
            branch1 = uniongraph.vertices[i]
            break

    # We initalize num to 0
    num = 0
    # We make a copy of branchcoloring which we need later.
    # Example once we're done branching into a vertex of graph2, we have to go into branching of another vertex of graph2 if possible with the same branchcoloring as before, not the branchcoloring resulting from the first branch
    branchcoloringcopy = list(branchcoloring)

    # Now we branch with all possible verts in graph2 with this same color.
    # Meaning for all verts in graph2 with that color in uniongraph.
    # We run countisomorphism again with coloring list where we set this vertex and the vertex picked a unique color in the list
    for i in range(int(graphlen / 2), graphlen):
        if uniongraph.vertices[i].colornum == color:
            branch2 = uniongraph.vertices[i]
            # We make sure branchcoloring is not the one of branching of a previous vertex in graph2
            branchcoloring = list(branchcoloringcopy)
            # Set unique color in branchcoloring list to the vertices chosen, and countIsomorphism on it
            branchcoloring[branch1.label] = availablecolor
            branchcoloring[branch2.label] = availablecolor
            count = countIsomorphism(graph1, graph2, branchcoloring, automorphism)

            # If we are not looking for AUT# then we can return as soon as we have found 1 isomorphism
            if not automorphism and count > 0:
                return count
            num = num + count
    return num


# @profile
# Refine graphs to find the coarsest stable partitioning takes uniongraph as param
def colorRefinement(uniongraph):
    # partition dict of equivalence classes. Color as key and vertices as values
    partition = {}

    highestcolornum = 0
    for vertex in uniongraph:
        highestcolornum = max(vertex.colornum, highestcolornum)
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
    for vertex in uniongraph.vertices:
        if vertex.colornum not in partition.keys():
            partition[vertex.colornum] = []
        partition[vertex.colornum].append(vertex)

    # coloring iteration count
    dotnumber = 0
    # Variable to check if we have recolored any vertices, meaning we are not done with colorrefinement(haven't reached a stable partition)
    prevhighestcolornum = -1
    # As soon as we have unbalanced then we stop coloring
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

        # Check if still balanced, if not then loop will stop as they will not be Iso
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
    # The first half is part of graph1 and the second half is part of graph2
    for vertex in uniongraph:
        if vertex.label < (vertcount / 2):
            colorcountdict1[vertex.colornum] = colorcountdict1.get(vertex.colornum, 0) + 1
        if vertex.label >= (vertcount / 2):
            colorcountdict2[vertex.colornum] = colorcountdict2.get(vertex.colornum, 0) + 1

    if colorcountdict1 == colorcountdict2:
        return True
    return False


# Method to check if coloring is balanced(so possibly iso) and if discrete(actually iso). Returns 2 booleans
def balancedAndDiscrete(uniongraph):
    # We check if all the colors in first graph are unique, if yes then discrete
    # We also count the amount of vertices with each color in 2 dicts to later compare, if they're the same then possibly iso
    graph1colors = []
    discrete = True

    colorcountdict1 = {}
    colorcountdict2 = {}
    graphlen = len(uniongraph.vertices)

    for i in range(int(graphlen / 2)):
        vertexcolor = uniongraph.vertices[i].colornum
        if vertexcolor in graph1colors:
            # if this color was already in graph1colors then it is not discrete
            discrete = False
        else:
            graph1colors.append(vertexcolor)
        colorcountdict1[vertexcolor] = colorcountdict1.get(vertexcolor, 0) + 1
    for i in range(int(graphlen / 2), graphlen):
        vertexcolor = uniongraph.vertices[i].colornum
        colorcountdict2[vertexcolor] = colorcountdict2.get(vertexcolor, 0) + 1

    if colorcountdict1 == colorcountdict2:
        match = True
        return match, discrete

    return False, False


# Method to make uniongraph out of list of graphs
def graphunion(graphslist):
    graph1 = graphslist[0]
    graph2 = graphslist[1]
    U = Graph(False)
    vertmap = dict()
    for vertex in graph1.vertices:
        newvertex = Vertex(U)
        vertmap[vertex] = newvertex
        U.add_vertex(newvertex)
    for edge in graph1.edges:
        newvertex1 = vertmap[edge.head]
        newvertex2 = vertmap[edge.tail]
        newedge = Edge(newvertex1, newvertex2)
        U.add_edge(newedge)
    for vertex in graph2.vertices:
        newvertex = Vertex(U)
        vertmap[vertex] = newvertex
        U.add_vertex(newvertex)
    for edge in graph2.edges:
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
        findIsomorphismCount(filelocation, 2)
    # get the execution time
    elapsedtotaltime = time.time() - totalstarttime
    print('Total execution time:', round(elapsedtotaltime, 2), 'seconds')


# folderrun("SampleGraphSetBranching")

# findIsomorphismCount("SampleGraphSetBranching/torus24.grl", 2)
# findIsomorphismCount("SampleGraphSetBranching/torus72.grl", 2)
# findIsomorphismCount("SampleGraphSetBranching/torus144.grl", 2)
# findIsomorphismCount("SampleGraphSetBranching/products72.grl", 2)
findIsomorphismCount("SampleGraphSetBranching/trees11.grl", 2)
# findIsomorphismCount("SampleGraphSetBranching/trees36.grl", 2)
# findIsomorphismCount("SampleGraphSetBranching/trees90.grl", 2)
# findIsomorphismCount("SampleGraphSetBranching/modulesC.grl", 2)
# findIsomorphismCount("SampleGraphSetBranching/modulesD.grl", 2)
# findIsomorphismCount("SampleGraphSetBranching/cubes3.grl", 2)
# findIsomorphismCount("SampleGraphSetBranching/cubes5.grl", 2)
# findIsomorphismCount("SampleGraphSetBranching/cubes6.grl", 2)
# findIsomorphismCount("SampleGraphSetBranching/cubes7.grl", 2)
# findIsomorphismCount("SampleGraphSetBranching/cubes8.grl", 2)
# findIsomorphismCount("SampleGraphSetBranching/wheeljoin14.grl", 2)


# folderrun("test")
totalst = time.time()
# findIsomorphismCount("test/BasicGI1.grl", 3)
# findIsomorphismCount("test/BasicGI2.grl", 3)
# findIsomorphismCount("test/BasicGI3.grl", 3)
# findIsomorphismCount("test/BasicGIAut1.grl", 2)
# findIsomorphismCount("test/BasicAut1.gr", 1)
# findIsomorphismCount("test/BasicAut2.gr", 1)
totaltime = time.time() - totalst
print('Total execution time:', round(totaltime, 2), 'seconds')
