#This set of functions is for the visualization of the values of the ILP 

import pandas as pd
import matplotlib.pyplot as plt

from RanNet_Generator import *
from Djikstra_Path_Calculator import *
from RandStream_Parameters import *
from Preprocessing import *
from ILP_Generator_2 import *
import time
from read_ilp_2 import *
from Plot import *

#leer la variable timestamp
with open('variable.txt', 'r') as file:
    timestamp = file.read().strip()
print("timestamp  ", timestamp)
latency=1
queue=0

input = "input1"
input_timestamp = input +"_" + timestamp
input_name = input + "_ilp_" + str(latency) + "_" + str(queue) + "_" + timestamp
file_input = "Solutions/" + input_timestamp + ".json"
file_resultado_input = "Resultado/" + input_timestamp + ".json"
file_image = "Solutions/" + input_name + ".html"
Hyperperiod = 1000
#Hyperperiod = 6000
#Hyperperiod = 30000

def ILP_results_visualizer(instance, Model_Descriptor_vector):
    print("############### This is the set of offsets ######################")
    Result_offsets = []
    Clean_offsets_collector = []
    Feasibility_indicator = 0
    for i in instance.Streams:
        for j in instance.Links:
            for k in instance.Frames:
                if Model_Descriptor_vector [i][k][j] :
                    print("The offset of stream", i, "link", j, "frame", k, "is",instance.Frame_Offset[i,j,k].value)
                    frame_indicator = ("S", i, "L", j, "F", k, "Q",int(instance.Queue_Assignment[i, j].value), "La",int(instance.Latency[i].value),"O",int(instance.Frame_Offset[i,j,k].value))
                    helper = { "Task" :str(frame_indicator), "Start": instance.Frame_Offset[i,j,k].value, "Finish" : (instance.Frame_Offset[i,j,k].value +12), "Color" : j }
                    clean_offset = { "Task" :str(frame_indicator), "Start": instance.Frame_Offset[i,j,k].value }
                    Result_offsets.append(helper)
                    Clean_offsets_collector.append(clean_offset)
                    if instance.Frame_Offset[i,j,k].value != 1 :
                        Feasibility_indicator = Feasibility_indicator + 1

    print("############### This is the set of latencies ######################")
    Results_latencies = []
    for stream in instance.Streams:
        #print("The lower latency of Stream", stream, "is",instance.Lower_Latency[stream].value)
        print("The latency of Stream ", stream, "is", int(instance.Latency[stream].value))
        Results_latencies.append(instance.Latency[stream].value)
    print("############### This is the set of queues ######################")
    for link in instance.Links:
        print("The number of queues of link ", link, "is",int(instance.Num_Queues[link].value))
    print("############### This is the set of queues per stream and link######################")
    for stream in instance.Streams:
        for link in instance.Links:
            print("The number of queues of Link",link , "Stream" , stream, "is", int(instance.Queue_Assignment[stream, link].value))

    #    print("############### This is the set of auxiliar queues variables######################")
    #    for stream in instance.Streams :
    #        for stream_2 in instance.Streams :
    #            for link in instance.Links :
    #                print("Aux variable for stream_1 ", stream, "Stream_2", stream_2, "link", link, ":", instance.Aux_Same_Queue[stream_2, link ,stream].value)
    return Feasibility_indicator, Result_offsets, Clean_offsets_collector, Results_latencies
      
    ##### For printing the model results and variables #####
    #UNCOMMENT if necessary 
    # instance.display()
    # results.write()
    # results.solver.status 
    ######################## For now on, this code is for generate the Gant chart ########################

def Evaluation_function(Number_of_edges, Connection_probability,Number_of_Streams) :

### This is just the part where the program can select betweeen generating a new network
#Number_of_edges, Connection_probability = 2 , 0.8
#Number_of_Streams = 5

################################################################
    # Generation of random Network
    try :
        initial_time = time.time()
        ####LEER DEL FICHERO
        Number_of_edges, Number_of_Streams, Network_nodes, Network_links, Adjacency_Matrix, plot_network, Sources, Destinations, Stream_Source_Destination = Read_ilp(file_resultado_input)
        # Adjacency_Matrix, plot_network, 
        ################################################################
        
        #Djikstra scheduler
        network = Network_Topology(Adjacency_Matrix) # Using the Network Topology class
        all_paths_matrix = all_paths_matrix_generator(Network_nodes, network)
        Streams_paths = Streams_paths_generator(all_paths_matrix, Stream_Source_Destination)
        Streams_links_paths = Streams_links_paths_generator(Streams_paths)
        Link_order_Descriptor = Link_order_Descriptor_generator(Streams_links_paths, Network_links)
        ################################################################
        
        # Random Streams parameters
        Streams_size , Streams_Period, Streams_Period_list, Deathline_Stream, Number_of_Streams = Read2_ilp(Number_of_Streams,file_resultado_input)
        #Hyperperiod = Hyperperiod_generator(Streams_Period_list)
        Frames_per_Stream, Max_frames, Num_of_Frames = Frames_per_Stream_generator(Streams_size)
        ################################################################
        
        # Preprocessing
        Links_per_Stream = Links_per_Stream_generator(Network_links, Link_order_Descriptor)
        Model_Descriptor, Model_Descriptor_vector, Streams = Model_Descriptor_generator(Number_of_Streams, Max_frames, Network_links, Frames_per_Stream, Links_per_Stream)
        Frame_Duration = Frame_Duration_Generator(Number_of_Streams, Max_frames, Network_links )
        Repetitions, Repetitions_Matrix, Repetitions_Descriptor, max_repetitions= Repetitions_generator(Streams_Period, Streams, Hyperperiod)
        unused_links = unused_links_generator(Network_links, Link_order_Descriptor)

        ################################################################
        scheduler = ILP_Raagard_solver(Number_of_Streams, Network_links, \
                        Link_order_Descriptor, \
                        Streams_Period, Hyperperiod, Frames_per_Stream, Max_frames, Num_of_Frames, \
                        Model_Descriptor, Model_Descriptor_vector, Deathline_Stream, \
                        Repetitions, Repetitions_Descriptor, unused_links, Frame_Duration, latency, queue)
        instance, results = scheduler.instance, scheduler.results
        final_time = time.time()
        ################################################################
        #Plot the values
        Feasibility_indicator, Result_offsets, Clean_offsets_collector, Results_latencies  = ILP_results_visualizer(instance, Model_Descriptor_vector)

        time_evaluation = final_time - initial_time
        with open('Results/' + input_name + '.txt', 'a') as f :
            f.write("\n")
            f.write("Execution time:    ")
            f.write(str(time_evaluation) + "\n")
            f.write("############### This is the set of offsets ######################" + "\n")
            for i in instance.Streams:
                for j in instance.Links:
                    for k in instance.Frames:
                        if Model_Descriptor_vector [i][k][j] :
                            f.write("The offset of stream " + str(i) + " link " +str(j)+ " frame " + str(k) + " is " + str(instance.Frame_Offset[i,j,k].value) + "\n")
            f.write("############### This is the set of latencies ######################" + "\n")
            for stream in instance.Streams:
                f.write("The lower latency of Stream " + str(stream) + " is " + str(instance.Lower_Latency[stream].value) + "\n")
            f.write("############### This is the set of queues ######################" + "\n")
            for link in instance.Links:
                f.write("The number of queues of link " + str(link) + " is " + str(instance.Num_Queues[link].value) + "\n")
            f.write("############### This is the set of queues per stream and link######################" + "\n")
            for stream in instance.Streams:
                for link in instance.Links:
                    f.write("The number of queues of Link " + str(link) + " stream " + str(stream) + " is " + str(instance.Queue_Assignment[stream, link].value) + "\n")
        #PLOT
        network_fig = network_topology(Sources,Destinations)
        gantt_fig = gantt_chart(Result_offsets, Repetitions, Streams_Period)
        info_fig = info_box(Network_links, Repetitions, Streams_Period, Link_order_Descriptor, 
        Streams_links_paths, )
        combined(network_fig,gantt_fig,info_fig, file_image)
    except ValueError:
        print("One error has occurred")

for n in [4]:
    for i in range(1):
        # Evaluation_Function(number_of_nodes, connection_probability, number of streams)
        Evaluation_function(2, 1, n)
