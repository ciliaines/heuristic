import json
from RanNet_Generator import *
import matplotlib.pyplot as plt
import networkx as nx 

#file_input = "Solutions/input6.json"
 
def Read_ilp(file_input):
    Number_of_edges=0  #numero de switch=4
    Number_of_Streams=0 #numero de flujos=3
    Network_nodes = list()
    Network_links = list()
    Stream_Source_Destination = []
    with open(file_input, "r") as j:
        data = json.load(j)
        Network_link = list()
        for switch in data["switches"]:
            Number_of_edges = Number_of_edges+1
            Name_switch = switch["name"]
            Network_nodes = Network_nodes + [int(x) for x in Name_switch]
            change = True
            for port in switch["ports"]:
                Name_port_switch = port["name"]
                ConnectsTo_port_switch = port["connectsTo"]
                if(Network_link == []):
                    Network_link = Network_link + [(x, y) for x in Name_switch for y in ConnectsTo_port_switch]
                for link in Network_link:
                    if link[0] == ConnectsTo_port_switch and link[1] == Name_switch:
                        change = False
                        break
                    else:
                        change == True
                if change == True:
                    Network_links = Network_links + [(int(x), int(y)) for x in Name_switch for y in ConnectsTo_port_switch]
                    change = False
               
        for flow in data["flows"]:
            Number_of_Streams =Number_of_Streams+1
            Name_flow = flow["name"]
            SourceDevice_flow = flow["sourceDevice"]
            EndDevices_flow = flow["endDevices"]
            Steam = [int(SourceDevice_flow), int(EndDevices_flow)]
            Stream_Source_Destination.append(Steam)
    Adjacency_Matrix = adj(Network_links)
    plot_network = plt.figure(1, figsize=(14, 7))
    Sources = [link[0] for link in Network_links]
    Destinations = [link[1] for link in Network_links]
    
    #Build a dataframe with the Source and destination connections
    df = pd.DataFrame({ 'from': Sources , 'to': Destinations})
    # Build the graph
    G=nx.from_pandas_edgelist(df, 'from', 'to')
    # Plot the graph
    plot_network = plt.figure(1, figsize=(14, 7))
    plt.subplot(221)
    plt.title("Network  Topology")
    nx.draw(G, with_labels=True,  node_size=200, font_size=7, edge_color='gray', width=1.0)
    return Number_of_edges, Number_of_Streams, Network_nodes, Network_links, Adjacency_Matrix, plot_network, Sources, Destinations, Stream_Source_Destination,

def Read2_ilp(Number_of_Streams, file_input):
    SourceDevice_flow = list()
    Streams_size = list()   #[53, 256] hecho
    Streams_Period = {}  # {0: 5000, 1: 2500} hecho
    Streams_Period_list = list()  #[5000, 2500] hecho
    Deathline_Stream_list = list()
    Deathline_Stream = {}  # {0: 1000, 1: 1000} hecho
    with open(file_input, "r") as j:
        data = json.load(j)
        for flow in data["flows"]:
            Name_flow = flow["name"]
            SourceDevice_flow.append(flow["sourceDevice"])
            DefaultPacketPeriodicity_device = flow["period"]
            DefaultHardConstraintTime_device = flow["deathline"]
            DefaultPacketSize_device = flow["packetSize"]
            Deathline_Stream_list.append(DefaultHardConstraintTime_device)
            Streams_size.append(DefaultPacketSize_device)
            Streams_Period_list.append(DefaultPacketPeriodicity_device)                  
    for i in range(Number_of_Streams):
        Streams_Period[(i)] = Streams_Period_list[(i)]
        Deathline_Stream[(i)] = Deathline_Stream_list[(i)]
    return Streams_size , Streams_Period, Streams_Period_list, Deathline_Stream, Number_of_Streams
