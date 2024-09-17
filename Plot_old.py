

import pandas as pd
import matplotlib.pyplot as plt

from RanNet_Generator import *
from Djikstra_Path_Calculator import *
from RandStream_Parameters import *
from Preprocessing import *
from ILP_Generator_2 import *
import time
import textwrap
from read import *

def network_topology(Sources, Destinations):
    # Build a dataframe with the So,urce and destination connections
    df = pd.DataFrame({ 'from': Sources , 'to': Destinations})
    # Build the graph
    G=nx.from_pandas_edgelist(df, 'from', 'to')
    # Plot the graph
    plot_network= plt.figure(1,figsize=(28, 14))
    #plt.subplot(221)
    plt.subplot2grid((4,2),(0,0))
    plt.axis('off')
    plt.title("Network  Topology", fontsize=12)
    nx.draw(G, with_labels=True,  node_size=400, font_size=15, edge_color='gray', width=1.0)   

    

def gantt_chart_generator(Result_offsets, Repetitions, Streams_Period):
    data = [[frame['Task'], frame['Start']] for frame in Result_offsets]
    Repetitions = [repetition + 1 for repetition in Repetitions]
    color=['black', 'red', 'green', 'blue', 'cyan', 'magenta', 'yellow', 'grey', 'orange', 'pink','fuchsia']
    # This set of code is for generating the repetitions values in the dataset
    #For printing the full gant Chart
    New_offsets = []
    stream_index = 0
    for repetition in Repetitions :
        for frame in Result_offsets:
            substring = "'S', " +  str(stream_index)
            if substring in frame["Task"] :
                for i in range(int(repetition)) :
                    Repeated_Stream = {'Task' : frame["Task"] , 'Start' : frame["Start"] + Streams_Period[stream_index]*(i), 'Color' : color[frame["Color"]]}
                    New_offsets.append(Repeated_Stream)
        stream_index = stream_index + 1

    Result_offsets = New_offsets
    data = [[frame['Task'], frame['Start'], frame['Color']] for frame in New_offsets]
    df = pd.DataFrame(data, columns = ['Process_Name', 'Start', 'Color'])

    print("data  ", len(data))
    # This is for printing the gant Chart 
    #plt.subplot(212)
    plt.subplot2grid((4,2),(1,0), colspan=2, rowspan=3)
    #plt.figure(figsize=(12, 5))
    plt.barh(y=df.Process_Name, left=df.Start, width=12, color=df.Color)
    plt.grid(axis='x', alpha=1)
    plt.grid(axis='y',alpha=1)
    plt.ylabel("Frames")
    plt.xlabel("Time in microseconds")
    plt.xticks(fontsize=5)
    plt.yticks(fontsize=5)
    plt.title("Gantt Chart", fontsize=15)
    plt.tight_layout()
    #plt.savefig('testing.png')
    #plt.show() 
    #return df


def information_generator(Num_of_Frames, Streams_Period, Link_order_Descriptor, Network_links, Streams_links_paths,input_name):
    #plt.subplot(222)
    plt.subplot2grid((4,2),(0,1))
    plt.text(0.1, 0.9, "Network links: " + str(Network_links), bbox=dict(facecolor='red', alpha=0.6), fontsize=20)
    plt.text(0.1, 0.7, "Frames per stream: " + str(Num_of_Frames), bbox=dict(facecolor='red', alpha=0.6), fontsize=20)
    plt.text(0.1, 0.5, "Stream periods: " + str(Streams_Period), bbox=dict(facecolor='red', alpha=0.6), fontsize=20)
    plt.text(0.1, 0.3, "Indexed link order per stream:  " + str(Link_order_Descriptor), bbox=dict(facecolor='red', alpha=0.6), fontsize=20)
    wrapped_text = "\n".join(textwrap.wrap(str(Streams_links_paths), width=120))
    plt.text(0.1, 0.1, "Stream paths:  " + str(wrapped_text), bbox=dict(facecolor='red', alpha=0.6), fontsize=20)
    #plt.text(0.1, 0.1, "Stream paths: \n " + str(Streams_links_paths), bbox=dict(facecolor='red', alpha=0.5), fontsize=10)
    #plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
    plt.axis('off')
    name="Solutions/"+input_name+".png"
    plt.savefig(name, bbox_inches='tight', pad_inches=0)
    plt.show() # comment for avoiding showing de result

    #plot_network.tight_layout()
    #plot_network.savefig("Solutions/input_name.png", bbox_inches='tight', pad_inches=0)

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
    #with open('results.txt', 'a') as f :
    #    f.write("\n" + str(Full_scheduled_data))
