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

def ILP_results_visualizer(instance, Model_Descriptor_vector):
    #print("############### This is the set of offsets ######################")
    Result_offsets = []
    Clean_offsets_collector = []
    Feasibility_indicator = 0
    for i in instance.Streams:
        for j in instance.Links:
            for k in instance.Frames:
                if Model_Descriptor_vector [i][k][j] :
                    print("The offset of stream", i, "link", j, "frame", k, "is",instance.Frame_Offset[i,j,k].value)
                    frame_indicator = ("S", i, "L", j, "F", k)
                    helper = { "Task" :str(frame_indicator), "Start": instance.Frame_Offset[i,j,k].value, "Finish" : (instance.Frame_Offset[i,j,k].value +12), "Color" : j }
                    clean_offset = { "Task" :str(frame_indicator), "Start": instance.Frame_Offset[i,j,k].value }
                    Result_offsets.append(helper)
                    Clean_offsets_collector.append(clean_offset)
                    if instance.Frame_Offset[i,j,k].value != 1 :
                        Feasibility_indicator = Feasibility_indicator + 1         
    #print("############### This is the set of latencies ######################")
    Results_latencies = []
    for stream in instance.Streams:
        #print("The latency of Stream", stream, "is",instance.Latency[stream].value)
        Results_latencies.append(instance.Latency[stream].value)

    #print("############### This is the set of queues ######################")
    for link in instance.Links:
        print("The number of queues of link ", link, "is",instance.Num_Queues[link].value)
        print("heloo ",link)

    #print("############### This is the set of queues per stream and link######################")
#    for stream in instance.Streams:
#        for link in instance.Links:
            #print("The number of queues of Link",link , "Stream" , stream, "is", instance.Queue_Assignment[stream, link].value)

    #print("############### This is the set of auxiliar queues variables######################")
#    for stream in instance.Streams :
#        for stream_2 in instance.Streams :
#            for link in instance.Links :
                #print("Aux variable for stream_1 ", stream, "Stream_2", stream_2, "link", link, ":", instance.Aux_Same_Queue[stream_2, link ,stream].value)
    return Feasibility_indicator, Result_offsets, Clean_offsets_collector, Results_latencies

##### For printing the model results and variables #####
#UNCOMMENT if necessary 

# instance.display()
# results.write()
# results.solver.status 
######################## For now on, this code is for generate the Gant chart ########################


def gantt_chart_generator(Result_offsets, Repetitions, Streams_Period) :
    #print("Result_offsets       "+str(Result_offsets))
    #print("Repetitions         "+str(Repetitions))
    #print("Streams_Period      "+str(Streams_Period))

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
    plt.show() 
    return df


def information_generator(Num_of_Frames, Streams_Period, Link_order_Descriptor, Network_links, Streams_links_paths):
    print("Num_of_Frames      " +str(Num_of_Frames))
    #print("Streams_Period     "+str(Streams_Period))
    #print("Link_order_Descriptor       "+str (Link_order_Descriptor))
    #print("Network_links          "+str(Network_links))
    #print("Streams_links_paths       "+str(Streams_links_paths))
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
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        #Result_offsets 
        #[{'Task': "('S', 0, 'L', 2, 'F', 0)", 'Start': 200.0, 'Finish': 212.0, 'Color': 2}, 
        #{'Task': "('S', 0, 'L', 3, 'F', 0)", 'Start': 100.0, 'Finish': 112.0, 'Color': 3}, 
        #{'Task': "('S', 1, 'L', 1, 'F', 0)", 'Start': 200.0, 'Finish': 212.0, 'Color': 1}, 
        #{'Task': "('S', 1, 'L', 2, 'F', 0)", 'Start': 300.0, 'Finish': 312.0, 'Color': 2}, 
        #{'Task': "('S', 2, 'L', 2, 'F', 0)", 'Start': 100.0, 'Finish': 112.0, 'Color': 2}, 
        #{'Task': "('S', 2, 'L', 4, 'F', 0)", 'Start': -0.0, 'Finish': 12.0, 'Color': 4}]

#        Result_offsets vis    
#        [{'Task': "('S', 1, 'L', 1, 'F', 1)", 'Start': 0.0, 'Finish': 100.0, 'Color': 1}, 
#        {'Task': "('S', 1, 'L', 2, 'F', 1)", 'Start': 100.8, 'Finish': 200.8, 'Color': 2}, 
#        {'Task': "('S', 0, 'L', 3, 'F', 1)", 'Start': 0.0, 'Finish': 100.0, 'Color': 3}, 
#        {'Task': "('S', 0, 'L', 2, 'F', 1)", 'Start': 100.8, 'Finish': 200.8, 'Color': 2}, 
#        {'Task': "('S', 2, 'L', 4, 'F', 1)", 'Start': 0.0, 'Finish': 100.0, 'Color': 4}, 
#        {'Task': "('S', 2, 'L', 2, 'F', 1)", 'Start': 100.8, 'Finish': 200.8, 'Color': 2}]


        Result_offsets, Repetitions, Streams_Period = Evaluation_function_generator(2,1,1)

        print("Result_offsets vis   ", Result_offsets)
        ################################################################
        df = gantt_chart_generator(Result_offsets, Repetitions, Streams_Period)
        #information_generator(Num_of_Frames, Streams_Period, Link_order_Descriptor, Network_links, Streams_links_paths)
        #dataframe_printer(instance, Clean_offsets_collector, Results_latencies, Feasibility_indicator, Adjacency_Matrix, Stream_Source_Destination,
        #             Link_order_Descriptor, Links_per_Stream, Frames_per_Stream, Deathline_Stream, Streams_Period, Streams_size)
        ### This will store the results into a txt for further usage
        
    except ValueError:
        print("One error has occurred")

for n in [4]:
    for i in range(1):
        # Evaluation_Function(number_of_nodes, connection_probability, number of streams)
        Evaluation_function(2, 1, n)