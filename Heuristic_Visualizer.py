# This set of functions is for the visualization of the values of the ILP 

import pandas as pd
import matplotlib.pyplot as plt

from RanNet_Generator import *
from Djikstra_Path_Calculator import *
from RandStream_Parameters import *
from Preprocessing import *
from ILP_Generator import *
from Heuristic_Generator import *
import time
from read import *

def Heuristic_results_visualizer(instance, Model_Descriptor_vector):
    print("############### This is the set of offsets ######################")
    Result_offsets = []
    Clean_offsets_collector = []
    Feasibility_indicator = 0
    for i in instance.Streams:
        for j in instance.Links:
            for k in instance.Frames:
                if Model_Descriptor_vector [i][k][j] :
                    print("The offset of stream", i, "link", j, "frame", k, "is",instance.Frame_Offset[i,j,k].value)
                    frame_indicator = ("S", i, "L", j, "F", k, "Q",instance.Queue_Assignment[i, j].value, "La",instance.Latency[i].value+100)
                    helper = { "Task" :str(frame_indicator), "Start": instance.Frame_Offset[i,j,k].value, "Finish" : instance.Frame_Offset_up[i,j,k].value, "Color" : j }
                    clean_offset = { "Task" :str(frame_indicator), "Start": instance.Frame_Offset[i,j,k].value }
                    Result_offsets.append(helper)
                    Clean_offsets_collector.append(clean_offset)
                    if instance.Frame_Offset[i,j,k].value != 1 :
                        Feasibility_indicator = Feasibility_indicator + 1         
    print("############### This is the set of latencies ######################")
    Results_latencies = []
    for stream in instance.Streams:
        #print("The lower latency of Stream", stream, "is",instance.Lower_Latency[stream].value)
        print("The latency of Stream ", stream, "is", instance.Latency[stream].value)
        Results_latencies.append(instance.Latency[stream].value)#

    print("############### This is the set of queues ######################")
    for link in instance.Links:
        print("The number of queues of link ", link, "is",instance.Num_Queues[link].value)#

    print("############### This is the set of queues per stream and link######################")
    for stream in instance.Streams:
        for link in instance.Links:
            print("The number of queues of Link",link , "Stream" , stream, "is", instance.Queue_Assignment[stream, link].value)

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


def gantt_chart_generator(Result_offsets, Repetitions, Streams_Period):
    data = [[frame['Task'], frame['Start']] for frame in Result_offsets]
    Repetitions = [repetition + 1 for repetition in Repetitions]
    color=['black', 'red', 'green', 'blue', 'cyan', 'magenta', 'fuchsia', 'yellow', 'grey', 'orange', 'pink']
    # This set of code is for generating the repetitions values in the dataset
    #For printing the full gant Chart
    New_offsets = []
    stream_index = 0
    for repetition in Repetitions :
        #print("repetition   "+str(repetition))
        for frame in Result_offsets:
            #print("frame   "+str(frame))
            substring = "'S', " +  str(stream_index)
            if substring in frame["Task"] :
                #print("substring   "+substring)
                for i in range(int(repetition)) :
                    Repeated_Stream = {'Task' : frame["Task"] , 'Start' : frame["Start"] + Streams_Period[stream_index]*(i), 'Color' : color[frame["Color"]]}
                    New_offsets.append(Repeated_Stream)
        stream_index = stream_index + 1

    Result_offsets = New_offsets
    data = [[frame['Task'], frame['Start'], frame['Color']] for frame in New_offsets]
    df = pd.DataFrame(data, columns = ['Process_Name', 'Start', 'Color'])
    #rint("df.Process_Name     "+df.Process_Name)

    # This is for printing the gant Chart 
    plt.subplot(212)
    #plt.figure(figsize=(12, 5))
    plt.barh(y=df.Process_Name, left=df.Start, width=100, color=df.Color)
    plt.grid(axis='x', alpha=0.5)
    plt.ylabel("Frames")
    plt.xlabel("Time in miliseconds")
    plt.title("Gantt Chart")
    plt.savefig('testing.png')
    #plt.show() 
    return df


def information_generator(Num_of_Frames, Streams_Period, Link_order_Descriptor, Network_links, Streams_links_paths):
    plt.subplot(222)
    plt.text(0.1, 0.9, "Network-links: \n" + str(Network_links), bbox=dict(facecolor='red', alpha=0.5))
    plt.text(0.1, 0.7, "Frames per stream: \n" + str(Num_of_Frames), bbox=dict(facecolor='red', alpha=0.5))
    plt.text(0.1, 0.5, "Streams periods: \n" + str(Streams_Period), bbox=dict(facecolor='red', alpha=0.5))
    plt.text(0.1, 0.3, "Indexed Links order per stream: \n " + str(Link_order_Descriptor), bbox=dict(facecolor='red', alpha=0.5))
    plt.text(0.1, 0.1, "Streams Paths: \n " + str(Streams_links_paths), bbox=dict(facecolor='red', alpha=0.5))
    plt.axis('off')
    plt.show() # comment for avoiding showing de result


def dataframe_printer(instance, Clean_offsets, Results_latencies, Feasibility_indicator, Adjacency_Matrix, Stream_Source_Destination,
                    Link_order_Descriptor, Links_per_Stream, Frames_per_Stream, Deathline_Stream, Streams_Period, Streams_size):
    Feasibility = False
    if Feasibility_indicator > 1 :
        Feasibility = True
    # Definition of the Data Frame
    # Each schedule provides the following:
    Full_scheduled_data = {
        #Parameter of the network 
        "Adjacency_Matrix" : Adjacency_Matrix, 
        #Parameters of the Streams
        "Stream_Source_Destination" : Stream_Source_Destination, 
        "Link_order_Descriptor" : Link_order_Descriptor,
        "Links_per_Stream" : Links_per_Stream, 
        "Number_of_Streams" : len(instance.Streams),
        "Frames_per_Stream" : Frames_per_Stream,
        "Deathline_Stream" : Deathline_Stream,
        "Streams_Period" : Streams_Period,
        #Results
        "Streams_size" : Streams_size,
        "Clean_offsets" : Clean_offsets,
        "Latencies" : Results_latencies,
        "Feasibility" : Feasibility
    }


    #print(Full_scheduled_data)
    ### This will store the results into a txt for further usage
    with open('results.txt', 'a') as f :
        f.write("\n" + str(Full_scheduled_data))

def Evaluation_function(Number_of_edges, Connection_probability,Number_of_Streams) :

### This is just the part where the program can select betweeen generating a new network
#Number_of_edges, Connection_probability = 2 , 0.8
#Number_of_Streams = 5

################################################################
    # Generation of random Network
    try :
        #print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        Number_of_edges, Number_of_Streams, Network_nodes, Network_links, Adjacency_Matrix, plot_network, Sources, Destinations, Stream_Source_Destination = Read()
        ################################################################

        #Djikstra scheduler
        network = Network_Topology(Adjacency_Matrix) 
        all_paths_matrix = all_paths_matrix_generator(Network_nodes, network)
        Streams_paths = Streams_paths_generator(all_paths_matrix, Stream_Source_Destination)
        Streams_links_paths = Streams_links_paths_generator(Streams_paths)
        Link_order_Descriptor = Link_order_Descriptor_generator(Streams_links_paths, Network_links)
        ################################################################
        
        # Random Streams parameters
        Streams_size , Streams_Period, Streams_Period_list, Deathline_Stream, Number_of_Streams = Read2(Number_of_Streams)
        #Link_order_Descriptor = cambiar la funcion a la del heuritsto ahora lo hago en el fichero 
        Sort_Stream_Source_Destination = Sort_flow(Stream_Source_Destination, Deathline_Stream, Streams_Period, Streams_size)
        Hyperperiod = Hyperperiod_generator(Streams_Period_list)
        Frames_per_Stream, Max_frames, Num_of_Frames = Frames_per_Stream_generator(Streams_size)
        ################################################################
        
        # Preprocessing
        Links_per_Stream = Links_per_Stream_generator(Network_links, Link_order_Descriptor)
        Model_Descriptor, Model_Descriptor_vector, Streams = Model_Descriptor_generator(Number_of_Streams, Max_frames, Network_links, Frames_per_Stream, Links_per_Stream)
        Frame_Duration = Frame_Duration_Generator(Number_of_Streams, Max_frames, Network_links )
        Repetitions, Repetitions_Matrix, Repetitions_Descriptor, max_repetitions= Repetitions_generator(Streams_Period, Streams, Hyperperiod)

        ################################################################
        scheduler = Heuristic_class(Number_of_Streams, Network_links, \
                Link_order_Descriptor, \
                Streams_Period, Hyperperiod, Frames_per_Stream, Max_frames, Num_of_Frames, \
                Model_Descriptor, Model_Descriptor_vector, Deathline_Stream, \
                Repetitions, Repetitions_Descriptor, Frame_Duration, \
                Stream_Source_Destination, Streams_size, Streams_paths, Sort_Stream_Source_Destination) #unused_links¿?

        instance, results = scheduler.instance, scheduler.results

        Greedy_Heuristic(instance)
        
        ################################################################

        ################################################################
        #Heuristic_results_visualizer
        Feasibility_indicator, Result_offsets, Clean_offsets_collector, Results_latencies = Heuristic_results_visualizer(instance, Model_Descriptor_vector)

        df = gantt_chart_generator(Result_offsets, Repetitions, Streams_Period)
        information_generator(Repetitions, Streams_Period, Link_order_Descriptor, Network_links, Streams_links_paths)


        Results_latencies = []
        for stream in instance.Streams:
            #print("The latency of Stream", stream, "is",instance.Latency[stream].value)
            Results_latencies.append(instance.Latency[stream].value)

        dataframe_printer(instance, Clean_offsets_collector, Results_latencies, Feasibility_indicator, Adjacency_Matrix, Stream_Source_Destination,
                     Link_order_Descriptor, Links_per_Stream, Frames_per_Stream, Deathline_Stream, Streams_Period, Streams_size)
        ### This will store the results into a txt for further usage
        
    except ValueError:
        print("One error has occurred")

for n in [4]:
    for i in range(1):
        # Evaluation_Function(number_of_nodes, connection_probability, number of streams)
        Evaluation_function(2, 1, n)