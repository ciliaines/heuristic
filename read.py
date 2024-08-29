import json
from RanNet_Generator import *
import matplotlib.pyplot as plt
import networkx as nx 
import random

def Read(file_input):
    Number_of_edges=0  #numero de switch=4
    Number_of_Streams=0 #numero de flujos=3
    Network_nodes = list()
    Network_links = list()
    Number_enlace = list()
    Stream_Source_Destination = []
    Stream_Source_Destination_total = []
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
        for link in data["links"]:
            Name_link = link["name"]
            Number = link["number"]
            #print("Name_link  ", Name_link)
            #print("Number   ", Number)
            #Number_enlace = Number_enlace + [(int(x), int(y)) for x in Name_link for y in Number]
            Devices = list()
            for e in link["devices"]:
                Devices = Devices + [int(x) for x in e]             
            Stream_Source_Destination_total.append(Devices)
        #print("Number_enlace   ",Number_enlace)
      
    Adjacency_Matrix = adj(Network_links)
    plot_network = plt.figure(1, figsize=(14, 7))
    Sources = [link[0] for link in Network_links]
    Destinations = [link[1] for link in Network_links]

    # Build a dataframe with the Source and destination connections
    df = pd.DataFrame({ 'from': Sources , 'to': Destinations})
    # Build the graph
    G=nx.from_pandas_edgelist(df, 'from', 'to')
    # Plot the graph
    plot_network = plt.figure(1, figsize=(14, 7))
    plt.subplot(221)
    plt.title("Network  Topology")
    nx.draw(G, with_labels=True,  node_size=200, font_size=7, edge_color='gray', width=1.0)
    print("Number_of_edges  ",Number_of_edges)
    return Number_of_edges, Number_of_Streams, Network_nodes, Network_links, Adjacency_Matrix, plot_network, Sources, Destinations, Stream_Source_Destination_total

def Random(Stream_Source_Destination_total, Hiperperiod, Stream_Source_Destination, Streams_Period, Deathline_Stream, Number_of_Streams,Streams_size  ):
    Number_of_Streams = Number_of_Streams+1

    #Ecoger los Streams
    choice = random.choice(Stream_Source_Destination_total)   
    Stream_Source_Destination.append([choice[0], choice[-1]])
    periodos = []
    #Escoger los periodos
    if Hiperperiod == 1000:
       periodos = [100, 200, 500, 1000]
    if Hiperperiod == 6000:
        periodos = [100, 150, 500, 1000, 2000, 6000]
    if Hiperperiod == 30000:
        periodos = [100, 150, 200, 300, 500, 5000, 10000, 30000]
    Periodo = random.choice(periodos)
    Streams_Period[len(Stream_Source_Destination)-1] = Periodo #{0:5000, 1:2500}
    
    #Equiparar el deathline
    Deathline_Stream[len(Stream_Source_Destination)-1] = Periodo * 3

    #Escoger el datasize
    if Periodo == 100 or Periodo == 150 or Periodo == 200 or Periodo == 300 or Periodo == 500:
        size_pos = [1500,3000,4500]
    else:
        size_pos = [15000, 30000, 60000, 90000, 150000]
    size = random.choice(size_pos)
    Streams_size = Streams_size + [size]             

    #print("Stream_Source_Destination    ", Stream_Source_Destination)
    #print("Streams_Period   ", Streams_Period)
    #print("Number_of_Streams    ", Number_of_Streams)
    #print("Streams_size     ", Streams_size)

    return Stream_Source_Destination, Streams_Period, Deathline_Stream, Number_of_Streams, Streams_size

def Read_Complete(file_result):
    Number_of_edges=0  #numero de switch=4
    Number_of_Streams=0 #numero de flujos=3
    Network_nodes = list()
    Network_links = list()
    Stream_Source_Destination = []
    Streams_size = list()
    Streams_Period = {}
    Streams_Period_list = list()
    Deathline_Stream_list = list()
    Deathline_Stream = {}
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
            Number_of_Streams = Number_of_Streams + 1
            Name_flow = flow["name"]
            Period = flow["Period"]
            Streams_Period_list.append(Period)
            Streams_Period[int(Name_flow)] = Period
            Deathline = flow["Deathline"]
            Deathline_Stream[int(Name_flow)] = Deathline
            Size = flow["Size"]
            Streams_size.append(Size)
            SourceDevice = flow["SourceDevice"]
            EndDevice = flow["EndDevices"]
            Steam = [int(SourceDevice), int(EndDevice)]
            Stream_Source_Destination.append(Steam)

    Adjacency_Matrix = adj(Network_links)
    plot_network = plt.figure(1, figsize=(14, 7))
    Sources = [link[0] for link in Network_links]
    Destinations = [link[1] for link in Network_links]

    # Build a dataframe with the Source and destination connections
    df = pd.DataFrame({ 'from': Sources , 'to': Destinations})
    # Build the graph
    G=nx.from_pandas_edgelist(df, 'from', 'to')
    # Plot the graph
    plot_network = plt.figure(1, figsize=(14, 7))
    plt.subplot(221)
    plt.title("Network  Topology")
    nx.draw(G, with_labels=True,  node_size=200, font_size=7, edge_color='gray', width=1.0)
    return Number_of_edges, Number_of_Streams, Network_nodes, Network_links, Adjacency_Matrix, plot_network, Sources, Destinations, Stream_Source_Destination, Streams_size, Streams_Period, Streams_Period_list, Deathline_Stream, Number_of_Streams
