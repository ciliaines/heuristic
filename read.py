import json
from RanNet_Generator import *
from read import *
import matplotlib.pyplot as plt
import networkx as nx 


def Read():
    #input give by input.conf
    Number_of_edges=0  #numero de switch=4
    Number_of_Streams=0 #numero de flujos=3
    Network_nodes = list()
    Network_links = list()
    Stream_Source_Destination = []
    #"c:/Users/cilia/TSN-CNC-CUC-UPC/CNC/Microservices/Random_generator_microservice/input.json"
    with open("input.json", "r") as j:
        data = json.load(j)
        Network_link = list()
        for switch in data["switches"]:
            Number_of_edges = Number_of_edges+1
            Name_switch = switch["name"]
            Network_nodes = Network_nodes + [int(x) for x in Name_switch]
            ScheduleType_switch = switch["scheduleType"]
            DefaultTimeToTravel_switch = switch["defaultTimeToTravel"]
            DefaultPortSpeed_switch = switch["defaultPortSpeed"]
            change = True
            for port in switch["ports"]:
                Name_port_switch = port["name"]
                ConnectsTo_port_switch = port["connectsTo"]
                Network_link = Network_link + [(x, y) for x in Name_switch for y in ConnectsTo_port_switch]
                for link in Network_link:
                    if link[0] == ConnectsTo_port_switch and link[1] == Name_switch:
                        break
                    else:
                        if change == True:
                            Network_links = Network_links + [(int(x), int(y)) for x in Name_switch for y in ConnectsTo_port_switch]
                            change = False
                TimeToTravel_port_switch = port["timeToTravel"]
                #print(port["portSpeed"])
                #print(port["scheduleType"])
                #print(port["guardBandSize"])
                #MaximunSlotDuration_port_switch = port["maximumSlotDuration"]
                #CycleStart_port_switch = port["cycleStart"]
        for flow in data["flows"]:
            Number_of_Streams =Number_of_Streams+1
            Name_flow = flow["name"]
            Type_flow = flow["type"]
            SourceDevice_flow = flow["sourceDevice"]
            for e in flow["endDevices"]:
                EndDevices_flow = e
            Steam = [int(SourceDevice_flow), int(EndDevices_flow)]
            Stream_Source_Destination.append(Steam)
            for hops in flow["hops"]:
                CurrentNodeName_hops_flow = hops["currentNodeName"]
                NextNodeName_hops_flow = hops["nextNodeName"]

    Adjacency_Matrix = adj(Network_links)
    plot_network = plt.figure(1, figsize=(14, 7))
    Sources = [link[0] for link in Network_links]
    Destinations = [link[1] for link in Network_links]


     # Build a dataframe with the Source and destination connections

    df = pd.DataFrame({ 'from': Sources , 'to': Destinations})
    #print("Sources   "+str(Sources))
    #print("Destinations    "+str(Destinations))

    # Build the graph
    G=nx.from_pandas_edgelist(df, 'from', 'to')
    # Plot the graph
    plot_network = plt.figure(1, figsize=(14, 7))
    plt.subplot(221)
    plt.title("Network  Topology")
    nx.draw(G, with_labels=True)
    
    return Number_of_edges, Number_of_Streams, Network_nodes, Network_links, Adjacency_Matrix, plot_network, Sources, Destinations, Stream_Source_Destination,


def Read2(Number_of_Streams):
    SourceDevice_flow = list()
    Streams_size = list()   #[53, 256] hecho
    Streams_Period = {}  # {0: 5000, 1: 2500} hecho
    Streams_Period_list = list()  #[5000, 2500] hecho
    Deathline_Stream_list = list()
    Deathline_Stream = {}  # {0: 1000, 1: 1000} hecho
    with open("input.json", "r") as j:
        data = json.load(j)
        for flow in data["flows"]:
            SourceDevice_flow.append(flow["sourceDevice"])
        for device in data["devices"]:
            Name_device = device["name"]
            DefaultFirstSendingTime_device = device["defaultFirstSendingTime"]
            DefaultPacketPeriodicity_device = device["defaultPacketPeriodicity"]
            #print("DefaultPacketPeriodicity_device " + str(DefaultPacketPeriodicity_device))
            DefaultHardConstraintTime_device = device["defaultHardConstraintTime"]
            DefaultPacketSize_device = device["defaultPacketSize"]
            Deathline_Stream_list.append(DefaultHardConstraintTime_device)
            for s in SourceDevice_flow:
                name = "dev"+str(s)
                if(Name_device == name):
                    Streams_size.append(DefaultPacketSize_device)
                    Streams_Period_list.append(DefaultPacketPeriodicity_device)
    for i in range(Number_of_Streams):
        Streams_Period[(i)] = Streams_Period_list[(i)]
        Deathline_Stream[(i)] = Deathline_Stream_list[(i)]

    # print("Streams_size  " + str(Streams_size))
    #print("Stream_Period " + str(Streams_Period))
    # print("Strams_Period_list " + str(Streams_Period_list))
    #print("Deathline_Stream " + str(Deathline_Stream))
    # print("Number_of_stream " + str(Number_of_Streams))
    return Streams_size , Streams_Period, Streams_Period_list, Deathline_Stream, Number_of_Streams

