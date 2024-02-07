


"""
____________Input Variables______________ 


This values are received from the outside. According to our microservices topology, 
all these parameters should ber provided as a input from preprocessing microservice
Number_of_Streams
Network_links,
Link_order_Descriptor,
Streams_Period, 
Hyperperiod,
Frames_per_Stream, 
Max_frames, 
Num_of_Frames,
Model_Descriptor, 
Model_Descriptor_vector, 
Deathline_Stream, 
Repetitions, 
Repetitions_Descriptor, 
Unused_links, 
Frame_Duration

"""


class Heuristic_solver :
	def __init__(self,Stream_Source_Destination, Deathline_Stream, 
				Streams_Period, Streams_size, Network_links, \
        		Links, Num_Queues, Streams_paths, Num_of_Frames):

		self.Stream_Source_Destination = Stream_Source_Destination
		self.Deathline_Stream = Deathline_Stream
		self.Streams_Period = Streams_Period
		self.Streams_size = Streams_size
		self.Network_links = Network_links
		self.Links = Links
		self.Num_Queues = Num_Queues
		slef.Streams_paths = Streams_paths
		self.Num_of_Frames = Num_of_Frames

        self.model = AbstractModel()

        self.model.Frames = Set(initialize= frozenset(range(Max_frames))) # Maximum number of streams
        self.model.Links = Set(initialize = frozenset(range(len(Network_links)))) # Links Ids

        #Parameters
        self.model.Num_Queues = Var(self.model.Links, within=NonNegativeIntegers, initialize=1)

        #Variables
        self.model.Frame_Offset =
        self.model.Queue_Assigment =

        self.model.Lower_Latency =
        self.model.Num_Queues =