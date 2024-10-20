# This code is for calculation the previous parameters of the ILP  
# This code generates a matrix that will be used to 
# indicate wheter of not a frame in a stream and in a link exists or not
from RanNet_Generator import Random_Network_Generator
from Djikstra_Path_Calculator import *
from RandStream_Parameters import *
def Model_Descriptor_generator(Number_of_Streams, Max_frames, Network_links, Frames_per_Stream, Links_per_Stream) :
    Model_Descriptor = {}

    for stream in range(Number_of_Streams):
        for frame in range(Max_frames):
            for link in range(len(Network_links)):
                Model_Descriptor[(stream,frame,link)]= 0

    Model_Descriptor_vector = [[[0 for link in range(len(Network_links))] for frame in range(Max_frames)] for stream in range(Number_of_Streams)]

    x = 0
    for stream in Frames_per_Stream:
        y = 0
        for frame in stream:
            z = 0
            for link in Links_per_Stream[x]:
                Model_Descriptor[(x,y,z)] = frame * link 
                Model_Descriptor_vector [x][y][z] = frame * link
                z = z +  1
            y = y + 1
        x = x + 1
    Streams = range(Number_of_Streams)

    return Model_Descriptor, Model_Descriptor_vector, Streams


# Links per stream, basically is a list that indicates if a link is used for transmitting in a stream
def Links_per_Stream_generator(Network_links, Link_order_Descriptor) : 
    Links_per_Stream = [[0 for link in range(len(Network_links))] for stream in range(len(Link_order_Descriptor))]
    stream_index = 0
    for stream in Link_order_Descriptor :
        for link in stream :
            Links_per_Stream[stream_index][link] = 1
        stream_index = stream_index + 1 
    return Links_per_Stream  

# Boolean function that indicates if a combination of Frame Link and Stream exists or not
def frame_exists(Model_Descriptor_vector, stream, frame) :
    return len([*filter(lambda x: x >= 1, Model_Descriptor_vector[stream][frame])])

# Simply, fills the duration of the streams with a fixed value, can be changed in future
def Frame_Duration_Generator(Number_of_Streams, Max_frames, Network_links ) :
    Frame_Duration = {}
    for stream in range(Number_of_Streams):
        for frame in range(Max_frames):
            for link in range(len(Network_links)):
                Frame_Duration[(stream,frame,link)]= 12 # This has to be 12
    return Frame_Duration


#This function generates the following:

# Repetitions: a vector with all the number of repetitions
# Repetition matrix: a matrix filled with ones regarding the number of repetitions in each stream
# Repetitions Descriptor: a matrix used for determining if a repetition in a determined stream exists or not
# max_repetitions: Simply the maximum number of repetitions in any stream
def Repetitions_generator(Streams_Period, Streams, Hyperperiod) :
    Repetitions = []
    for period in range(len(Streams_Period)):
        Repetitions.append(float(Hyperperiod)/Streams_Period[(period)] - 1)


    Repetitions_Matrix = []
    for repetition in Repetitions :
        Repetitions_Matrix.append([1 for rep in range(int(repetition))])

    if max(Repetitions) == 0 :
        Repetitions_Descriptor = [[0] for stream in Streams ]
    else :
        Repetitions_Descriptor = [[0 for repetition in range(int(max(Repetitions)))] for stream in Streams ]
    x = 0
    for stream in Repetitions_Matrix:
        y = 0
        for repetition in stream:
            Repetitions_Descriptor[x][y] = repetition * (y+1)
            y = y +1
        x = x + 1
    try :
        max_repetitions = max([max(stream) for stream in Repetitions_Descriptor])
    except :
        max_repetitions = 0


    # This is a patch for including the repetition 0 in the constraints 34 and 35
    y = 0
    try :
        for stream in Repetitions_Descriptor :
            x = 0
            for repetition in stream :
                if repetition == 0 :
                    Repetitions_Descriptor[y][x] = 9
                x = x +1
            Repetitions_Descriptor[y].insert(0 ,0)
            y = y +1

    except :
        print("Then it is not necessary")
    return Repetitions, Repetitions_Matrix, Repetitions_Descriptor, max_repetitions

### Defined unused links
def unused_links_generator(Network_links, Link_order_Descriptor):
    number_of_links = len(Network_links)
    unused_links = []
    for i in range(number_of_links) :
        totalizer = 0
        for link in Link_order_Descriptor:
            for sub_link in link:
                if sub_link == i :
                    totalizer = 1
        if totalizer == 0:
            unused_links.append(i)
    return unused_links
