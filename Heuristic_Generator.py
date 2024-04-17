##################################### Heuristic Strategy starts here #####################################

from pyomo.environ import *
from pyomo.opt import SolverFactory
from pyomo.core import Var

flexibility_solution = {}

class Heuristic_class :
    def __init__(self, Number_of_Streams, Network_links, \
                Link_order_Descriptor, \
                Streams_Period, Hyperperiod, Frames_per_Stream, Max_frames, Num_of_Frames, \
                Model_Descriptor, Model_Descriptor_vector, Deathline_Stream, \
                Repetitions, Repetitions_Descriptor, Frame_Duration, \
                Stream_Source_Destination, Streams_size, Streams_paths, Sort_Stream_Source_Destination):

        self.Number_of_Streams = Number_of_Streams
        self.Network_links = Network_links
        self.Link_order_Descriptor = Link_order_Descriptor
        self.Streams_Period = Streams_Period
        self.Hyperperiod = Hyperperiod
        self.Frames_per_Stream = Frames_per_Stream 
        self.Max_frames = Max_frames 
        self.Num_of_Frames = Num_of_Frames
        self.Model_Descriptor = Model_Descriptor
        self.Model_Descriptor_vector = Model_Descriptor_vector
        self.Deathline_Stream = Deathline_Stream
        self.Repetitions = Repetitions
        self.Repetitions_Descriptor = Repetitions_Descriptor
        self.Frame_Duration = Frame_Duration
        self.Stream_Source_Destination = Stream_Source_Destination
        self.Streams_size = Streams_size
        self.Streams_paths = Streams_paths
        self.Sort_Stream_Source_Destination = Sort_Stream_Source_Destination
        #print("self  ",self.Number_of_Streams, self.Network_links, self.Link_order_Descriptor, self.Streams_Period, self.Hyperperiod)
        #print("2",self.Frames_per_Stream,self.Max_frames, self.Num_of_Frames,self.Model_Descriptor,self.Model_Descriptor_vector)
        #print("3",self.Deathline_Stream,self.Repetitions, self.Repetitions_Descriptor,self.Frame_Duration)
        #print("4",self.Stream_Source_Destination,self.Streams_size,self.Streams_paths, self.Sort_Stream_Source_Destination)

        self.model = AbstractModel()
        self.model.Streams = Set(initialize= range(self.Number_of_Streams)) 
        self.model.Repetitions = Set(initialize= range(int(max(Repetitions) + 1))) # This is the maximum number of Repetitions
        self.model.Frames = Set(initialize= frozenset(range(Max_frames))) # Maximum number of streams = [1,1,1]
        self.model.Links = Set(initialize = frozenset(range(len(Network_links)))) # Links Ids

        # Parameters
        self.model.Hyperperiod = Param(initialize=Hyperperiod)
        self.model.Max_Syn_Error = Param(initialize=0)
        self.model.Frame_Duration = Param(self.model.Streams, self.model.Frames, self.model.Links, initialize = self.Frame_Duration)
        self.model.Stream_Source_Destination = self.Stream_Source_Destination
        self.model.Deathline_Stream = self.Deathline_Stream
        self.model.Streams_Period = self.Streams_Period
        self.model.Streams_size = self.Streams_size
        self.model.Streams_paths = self.Streams_paths
        self.model.Sort_Stream_Source_Destination = self.Sort_Stream_Source_Destination

        self.model.Num_of_Frames_Dic = {key: value for key, value in enumerate(self.Num_of_Frames)}
        self.model.Streams_paths_Dic = {key: value for key, value in enumerate(self.Streams_paths)}
        self.model.Network_links_Dic = {key: value for key, value in enumerate(self.Network_links)}
        self.model.Stream_Source_Destination_Dic = {key: value for key, value in enumerate(self.Stream_Source_Destination)}
        self.model.Streams_Size_Dic = {key: value for key, value in enumerate(self.Streams_size)}
        # Variables
        self.model.Num_Queues = Var(self.model.Links, within=NonNegativeIntegers, initialize=1)
        self.model.Latency = Var(self.model.Streams, within=Integers, initialize=0)
        self.model.Queue_Link_Dic = {}
        self.model.Frame_Offset = Var(self.model.Streams, self.model.Links, self.model.Frames, within=NonNegativeIntegers, initialize=0)
        self.model.Frame_Offset_up = Var(self.model.Streams, self.model.Links, self.model.Frames, within=NonNegativeIntegers, initialize=0)
        #self.model.Queue_Link_Dic = {key: (self.model.Network_links_Dic[key], self.model.Num_Queues[key].value) for key in self.model.Network_links_Dic}
        self.model.Queue_total = {0: 2, 1: 2, 2: 2, 3: 2}
        self.model.Sort_Deathline_Stream = {}
        self.model.Queue_Assignment = Var(self.model.Streams, self.model.Links, within=NonNegativeIntegers, initialize=0)
        
        ### This part is the creation of the instance in the ilp system
        opt = SolverFactory('gurobi')
        #opt = SolverFactory('gurobi', solver_io="python")
        self.instance = self.model.create_instance()
        self.results = opt.solve(self.instance)
        self.instance.solutions.load_from(self.results)

def Greedy_Heuristic(model):
    #Ordenar los flows para su tratamiento
    #Sort_flow(model)
    for link, value in model.Network_links_Dic.items():
        model.Queue_Link_Dic[link] = (model.Network_links_Dic[link], model.Num_Queues[link].value)
    #Cola total de cada uno de los flows
    #model.Queue_total = List_queue(model)
    print("----",model.Sort_Stream_Source_Destination)
    for key_stream, value_stream in model.Sort_Stream_Source_Destination.items():
        success = False
        while not success:
            booleano ,link = Schedule_flow(key_stream, value_stream, model)
            if booleano == True:
                success = True
            else:
                Constraining_engress_port(value_stream)
                print("cuenta  ", str(model.Queue_Assignment[key_stream, link]))
                model.Queue_Assignment[key_stream, link] = model.Queue_Assignment[key_stream, link] + 1
                if (model.Queue_Assignment[key_stream, link] > model.Queue_total[key_stream]):
                    success = True

def Schedule_flow(key_stream, value_stream, model):
    for frame in range(model.Num_of_Frames_Dic[key_stream]): #tramas de cada link
        #BOUND_DIC  generamos una lsita con el lower y el upper bound
        lower_bound = 0.0
        Bound_dic = (lower_bound, model.Streams_Period[key_stream])
        #LINK, bus queda del link, del link de revivo y del envio
        a = 0
        b = 1
        # Generar un vector con el primer y segundo valor
        send_link = (model.Streams_paths_Dic[key_stream][a], model.Streams_paths_Dic[key_stream][b])
        link = send_link
        reciving_link= (model.Streams_paths_Dic[key_stream][-2], model.Streams_paths_Dic[key_stream][-1])
        
        contador=1
        while contador < len(model.Streams_paths_Dic[key_stream]):
            link_anterior = (model.Streams_paths_Dic[key_stream][a-1],model.Streams_paths_Dic[key_stream][b-1])
            key_link = next((key_stream for key_stream, value_stream in model.Network_links_Dic.items() if value_stream == link or value_stream == tuple(reversed(link))),None)

            lower_bound = Lower_bound(frame, send_link, link, link_anterior, model, key_stream, key_link)
            Bound_dic = (lower_bound, Bound_dic[1])
            tiempo = Earliest_offset  (link,Bound_dic,model, key_stream, frame, key_link)
            if flexibility_solution.get(link) is None:
                flexibility_solution[link] = [tiempo]
                
            else:
                flexibility_solution[link].append(tiempo)
            #frame_indicator = ("S", key_stream, "L", key_link, "F", frame, "Q", "queue_assignment")
            model.Latency[key_stream] += tiempo[0]
            model.Frame_Offset[key_stream, key_link, frame] = tiempo[0]
            model.Frame_Offset_up[key_stream, key_link, frame] = tiempo[-1]

            #helper = { "Task" :str(frame_indicator), "Start": tiempo[0], "Finish" : tiempo[-1], "Color" : key_link }
            #clean_offset = { "Task" :str(frame_indicator), "Start": tiempo[0] }
            #Result_offsets.append(helper)
            #Clean_offsets_collector.append(clean_offset)
            if tiempo[-1] == float('inf'):
                return False, key_link
            elif tiempo[-1] <= model.Streams_Period[key_stream]:
                Bound_dic = tiempo
                a += 1
                b += 1
                if b >= len(model.Streams_paths_Dic[key_stream]):
                    return True, key_link
                next_link = (model.Streams_paths_Dic[key_stream][a], model.Streams_paths_Dic[key_stream][b])
                link = next_link
                upper_boud_posterior = Latest_queue_available_time(link, model.Streams_Period[key_stream])

            else:
                #linea 15
                #lower_bound_anterior = #EARLIEST QUEUE AVAILABLE TIME
                a -= 1
                b -= 1
                link = [model.Streams_paths_Dic[key_stream][a], model.Streams_paths_Dic[key_stream][b]] 
            contador +=1
    return False, key_link #, Result_offsets 

def Earliest_offset(link, Bound_dic, model, stream, frame, key_link):
    #EARLIEST OFFSET
    tiempo= 0.0
    if flexibility_solution.get(link)is not None:
        #print("len ",len(flexibility_solution[link]))
        if len(flexibility_solution[link]) == 1:
            #print("value  ",flexibility_solution[link][-1])
            tiempo = (flexibility_solution[link][-1][-1], flexibility_solution[link][-1][-1]+model.Frame_Duration[stream,frame,key_link])
        else:
            #print("value  ",flexibility_solution[link][-1])
            tiempo = (flexibility_solution[link][-1][-1], flexibility_solution[link][-1][-1]+model.Frame_Duration[stream,frame,key_link])
        #print("existe",tiempo)
    else:
        tiempo = (Bound_dic[0],Bound_dic[0]+model.Frame_Duration[stream,frame,key_link])
        #print("no existe ",tiempo)
    return tiempo

def Latest_queue_available_time(link, Streams_Period):
    if flexibility_solution.get(link)is not None:
        tiempo = flexibility_solution[link][-1][-1]
        #print("existe ",tiempo)
    else:
        tiempo = Streams_Period
        #print("no existe ",tiempo)
    return tiempo

def Lower_bound(frame, send_link, link, link_anterior, model,stream, key_link):
   #print("link anterior  ",link_anterior, "frame   ",frame)
    if frame == 0 and link == send_link:
        return 0.0
    elif frame >= 1  and link == send_link:
        return flexibility_solution[link][-1][0] + model.Frame_Duration[stream,frame,key_link]
    elif frame == 0 and link != send_link:
        return flexibility_solution[link_anterior][frame-1][0] + model.Frame_Duration[stream,frame,key_link] +  model.Max_Syn_Error
    else:
        a = flexibility_solution[link][-1][0] + model.Frame_Duration[stream,frame,key_link]
        b = flexibility_solution[link_anterior][frame-1][0] + model.Frame_Duration[stream,frame,key_link] +  model.Max_Syn_Error
        return max(a,b)

#Listar colas asociadas a la clave del link
def List_queue(model):
    #print("Stream_Source_Destination_Dic ",Sort_Stream_Source_Destination)
    #print("Network_links   ", Network_links_Dic, "Num_Queues",  Num_Queues, "Streams_paths", Streams_paths)
    #print("Queue_Link_Dic  ",Queue_Link_Dic)
    Queue_total = {}

    for vector in model.Streams_paths:
        firts_value = vector[0]
        last_value = vector[-1]
        for key, value in model.Sort_Stream_Source_Destination.items():
            if value == [firts_value, last_value]:
                vector_shearch = (vector[-2], vector[-1])  # Este es el vector que deseas buscar
                for clave, valor in model.Queue_Link_Dic.items():
                    if valor[0] == vector_shearch or tuple(reversed(valor[0])) == vector_shearch:
                        model.Queue_total[key] = (valor[1])
    
    #print(Queue_total)
    model.Queue_total = {0: 2, 1: 2, 2: 2, 3: 2}
    return Queue_total

#ordenar los flows dependiendo de las reglas 
#def Sort_flow(model):
#    #Sort_Stream_Source_Destination = {}
#    #Combine the keys of all three dictionaries into a list
#    keys = sorted(set(model.Deathline_Stream.keys()) | set(model.Streams_Period.keys()) | set(model.Streams_Size_Dic.keys()))
#    #Defines a function to sort the keys based on Deathline_Stream, Streams_Period and Streams_Size_Dic
#    def sort_keys(key):
#        value1 = model.Deathline_Stream.get(key, float('inf'))
#        value2 = model.Streams_Period.get(key, float('inf'))
#        value3 = model.Streams_Size_Dic.get(key, float('-inf'))
#        #Sort first by Deathline_Stream, then by Streams_Period and finally by Streams_Size_Dic
#        return (value1, value2, -value3)
#    # Shot keys less to high
#    sort_keys = sorted(keys, key=sort_keys)
#    #print("SORT  KEYS",sort_keys)
#    # sort deadthline line dictory short
#    model.Sort_Deathline_Stream = {key: model.Deathline_Stream[key] for key in sort_keys}
#    # keys list
#    lista_de_claves = list(model.Sort_Deathline_Stream.keys())
#    #Ordenar el diccionario segun la lista de las claves
#    model.Sort_Stream_Source_Destination = {key: model.Stream_Source_Destination_Dic[key] for key in lista_de_claves}
#    model.Link_order_Descriptor = list(model.Sort_Stream_Source_Destination.values())

def Constraining_engress_port(value):
    #"bloquear value   " entre ello lo que hay que hacer
    #el eliminar lo generado en   --flexibility_solution--
    #print("NO se encontro solucion  ", flexibility_solution, "   value   ", value)
    del flexibility_solution[value]
