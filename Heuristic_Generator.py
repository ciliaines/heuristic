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

        self.model = AbstractModel()
        self.model.Streams = Set(initialize= range(self.Number_of_Streams)) 
        self.model.Repetitions = Set(initialize= range(int(max(Repetitions) + 1))) # This is the maximum number of Repetitions
        self.model.Frames = Set(initialize= frozenset(range(Max_frames))) # Maximum number of streams = [1,1,1]
        self.model.Links = Set(initialize = frozenset(range(len(Network_links)))) # Links Ids

        # Parameters
        self.model.Hyperperiod = Param(initialize=Hyperperiod)
        self.model.Max_Syn_Error = Param(initialize=0)
        self.model.Frame_Duration = Param(self.model.Streams, self.model.Frames, self.model.Links, initialize = self.Frame_Duration)
        self.model.Model_Descriptor = Param(self.model.Streams, self.model.Frames, self.model.Links, initialize= Model_Descriptor)
        self.model.Deathline_Stream = Param(self.model.Streams, initialize = Deathline_Stream)
        self.model.Period = Param(self.model.Streams, initialize=Streams_Period)
        #self.model.Num_of_Frames = Param(self.model.Streams, initialize=Num_of_Frames)

        self.model.Frames_per_Stream = self.Frames_per_Stream
        self.model.Stream_Source_Destination = self.Stream_Source_Destination
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
        self.model.Streams_Offset = Var(self.model.Streams, within=NonNegativeIntegers, initialize=0 )

        #self.model.Queue_total = Var(self.model.Streams,within=NonNegativeIntegers, initialize=4)
        self.model.Sort_Deathline_Stream = {}
        self.model.Queue_Assignment = Var(self.model.Streams, self.model.Links, within=NonNegativeIntegers, initialize=0)
        self.model.Solution = Var(self.model.Streams, self.model.Links, self.model.Frames, within=NonNegativeIntegers, initialize=0)
        self.model.Lower_bound = Var(self.model.Streams, self.model.Links, self.model.Frames, within=NonNegativeIntegers, initialize=0)
        self.model.Upper_bound = Var(self.model.Streams, self.model.Links, self.model.Frames, within=NonNegativeIntegers, initialize=0)

        ### This part is the creation of the instance in the ilp system
        opt = SolverFactory('gurobi')
        #opt = SolverFactory('glpk')
        #opt = SolverFactory('gurobi', solver_io="python")
        self.instance = self.model.create_instance()
        self.results = opt.solve(self.instance)
        self.instance.solutions.load_from(self.results)

def Greedy_Heuristic(model):
    for key_stream in model.Streams:
        value_stream = (0,0)
        success = False
        while not success:
            booleano ,link = Schedule_flow(key_stream, value_stream, model)
            Latency_Cal(key_stream, model)
            if booleano == True:
                success = True
                print("IF  ++++++++++++++ SOLUTION")
            else:
                #print("----------------------99999999999999999999999999999999--------------------------")
                Constraining_engress_port(model, key_stream,link,0)

                model.Queue_Assignment[key_stream, link] = model.Queue_Assignment[key_stream, link] + 1
                #model.Num_Queues[link] = model.Num_Queues[link] + 1

                if model.Queue_Assignment[key_stream, link].value > model.Num_Queues[link].value:
                    print("ELSE ++++++++++++++ SOLUTION")
                    #success = True

def Schedule_flow(key_stream, value_stream, model):
    #for frame in range(model.Num_of_Frames_Dic[key_stream]): #tramas de cada link
    print("eeeeee ",model.Frames_per_Stream[key_stream])
    for frame in range(model.Frames_per_Stream[key_stream][0]):
        a = 0
        b = 1
        # Generar un vector con el primer y segundo valor
        send_link = (model.Streams_paths_Dic[key_stream][a], model.Streams_paths_Dic[key_stream][b])
        #key_send_link = next((key_stream for key_stream, value_stream in model.Network_links_Dic.items() if value_stream == send_link or value_stream == tuple(reversed(send_link))),None)
        link = send_link
        key_link = next((key_stream for key_stream, value_stream in model.Network_links_Dic.items() if value_stream == link or value_stream == tuple(reversed(link))),None)
        reciving_link= (model.Streams_paths_Dic[key_stream][-2], model.Streams_paths_Dic[key_stream][-1])
        
        model.Lower_bound[key_stream, key_link, frame] = 0.0
        model.Upper_bound[key_stream, key_link, frame] = model.Streams_Period[key_stream]
        #lower_bound = 0.0
        #Bound_dic = (lower_bound, model.Streams_Period[key_stream])
        #print(f"Lower_bound[{key_send_link}] = {value(model.Lower_bound[key_send_link])}")
        #print(f"Upper_bound[{key_send_link}] = {value(model.Upper_bound[key_send_link])}")

        contador=1
        #while contador < len(model.Streams_paths_Dic[key_stream]):
        while link != reciving_link:
            print("contador ", contador, len(model.Streams_paths_Dic[key_stream]))
            #Ecuacion 45
            link_anterior = (model.Streams_paths_Dic[key_stream][a-1],model.Streams_paths_Dic[key_stream][b-1])
            key_link_anterior = next((key_stream for key_stream, value_stream in model.Network_links_Dic.items() if value_stream == link_anterior or value_stream == tuple(reversed(link_anterior))),None)          
            lower_bound = Lower_bound(send_link, link, model, key_stream, frame, key_link, key_link_anterior)
            model.Lower_bound[key_stream, key_link, frame] = lower_bound
            #print(f"Lower_bound[{key_stream, key_link, frame}] = {value(model.Lower_bound[key_stream, key_link, frame])}")
            #Bound_dic = (lower_bound, Bound_dic[1])
            
            #Earliest_offset
            tiempo = Earliest_offset(model, frame, key_link, key_stream)
            #print("stream   ",key_stream,"   key link  ",key_link, "  a  ", a , "  b  ",b)
            #print("tiempo   ", tiempo, "     Bound_dic   ",Bound_dic, "flexibility_solution   ",flexibility_solution.get(key_link))
            
            #model.Solution[key_stream, key_link, frame] = tiempo[0]
            #print(f"Solution[{key_stream}, {key_link}, {frame}] = {value(model.Solution[key_stream, key_link, frame])}")
            print("tiempo  ", tiempo[0], "upper ", model.Upper_bound[key_stream, key_link, frame].value)
            print("tiempo 2 ", tiempo[1])

            #if value(model.Solution[key_stream, key_link, frame]) == float('inf'):
            if tiempo[0] == float('inf'):
                return False, key_link

            #elif value(model.Solution[key_stream, key_link, frame]) <= value(model.Upper_bound[key_link]):

            elif tiempo[0] <= model.Upper_bound[key_stream, key_link, frame].value:
                #model.Streams_Period[key_stream]: #//no esta bien compara el tiempo escogido con el bound dic 
                Add_Solution(key_link, tiempo, model, key_stream)
                                
                model.Lower_bound[key_stream, key_link, frame] = tiempo[0] #model.Solution[key_stream, key_link, frame]
                model.Upper_bound[key_stream, key_link, frame] = tiempo[1] #model.Solution[key_stream, key_link, frame]+100
                #print(f"Lower_bound[{key_link}] = {value(model.Lower_bound[key_link])}")
                #print(f"Upper_bound[{key_link}] = {value(model.Upper_bound[key_link])}")

                #model.Ocupacion_Queue[key_link,model.Queue_Assignment[key_stream, key_link]] = tiempo
                #Bound_dic = tiempo
                a += 1
                b += 1
                #print("****************************111 else if a  ",a," b ",b," len ",len(model.Streams_paths_Dic[key_stream]))
                if b < len(model.Streams_paths_Dic[key_stream]):
                    next_link = (model.Streams_paths_Dic[key_stream][a], model.Streams_paths_Dic[key_stream][b])
                    link = next_link
                    key_link = next((key_stream for key_stream, value_stream in model.Network_links_Dic.items() if value_stream == link or value_stream == tuple(reversed(link))),None)
                    model.Upper_bound[key_stream, key_link, frame] = Latest_queue_available_time(key_link, model.Streams_Period[key_stream])
                    #print(f"Upper_bound[{key_stream, key_link, frame}] = {value(model.Upper_bound[key_stream, key_link, frame])}")
                contador +=1
            else:
                print("22222 else   ")
                a -= 1
                b -= 1
                link_next = (model.Streams_paths_Dic[key_stream][a], model.Streams_paths_Dic[key_stream][b])
                link = link_next
                key_link_next = next((key_stream for key_stream, value_stream in model.Network_links_Dic.items() if value_stream == link or value_stream == tuple(reversed(link))),None)
                print("**********  link_next  ",link_next, "  key_link_next  ",key_link_next)
                if key_link_next is not None:
                    model.Lower_bound[key_stream, key_link_next, frame] = Earliest_queue_available_time(key_link_next, model.Streams_Period[key_stream])
                contador -=1

    return True, key_link #, Result_offsets 

def Add_Solution(key_link, tiempo, model, key_stream): #Es por las posibles repeticiones dentro de una trama 
    #print("-----------")
    #print("key link ",key_link)
    #print("timepo ", tiempo)
    #print("Hyperperiod", model.Hyperperiod.value)
    #print("period ", model.Streams_Period)
    #resultado = model.Hyperperiod / model.Streams_Period[key_link]
    resultado = 1
    i = 0
    while i < resultado:
        if flexibility_solution.get(key_link) is None:
            flexibility_solution[key_link] = [tiempo]
        else:
            flexibility_solution[key_link].append(tiempo)
        tiempo = (tiempo[0] + model.Streams_Period[key_stream], tiempo[1]+model.Streams_Period[key_stream])
        i += 1

def Latency_Cal(key_stream, model):
    contador=1
    while contador < len(model.Streams_paths_Dic[key_stream]):
        link_ini = (model.Streams_paths_Dic[key_stream][0],model.Streams_paths_Dic[key_stream][1])
        link_end = (model.Streams_paths_Dic[key_stream][-2],model.Streams_paths_Dic[key_stream][-1])
        key_link_ini = next((key_stream for key_stream, value_stream in model.Network_links_Dic.items() if value_stream == link_ini or value_stream == tuple(reversed(link_ini))),None)
        key_link_end = next((key_stream for key_stream, value_stream in model.Network_links_Dic.items() if value_stream == link_end or value_stream == tuple(reversed(link_end))),None)
        #print("key_link_ini  ",key_link_ini, "  key_link_end  ",key_link_end)
        #print("frame offset ini  ",model.Frame_Offset[key_stream,key_link_ini,0].value,"    frame offset end   ",model.Frame_Offset_up[key_stream,key_link_end,0].value)
        model.Latency[key_stream] = model.Frame_Offset_up[key_stream,key_link_end,0].value - model.Frame_Offset[key_stream,key_link_ini,0].value
        contador +=1

def Earliest_offset(model, frame, key_link, key_stream):
    #EARLIEST OFFSET
    tiempo= 0.0
    #print("link  ", link,"Streams  ",stream)
    #print("Bound_dic   ",Bound_dic[0])
    print("flexibility_solution   ",flexibility_solution.get(key_link))
    #if model.Ocupacion_Queue[key_link, model.Queue_Assignment[key_stream, key_link]] is not None:
    #link_order = tuple(sorted(link))
    print(f"Lower_bound[{key_stream, key_link, frame}] = {value(model.Lower_bound[key_stream, key_link, frame])}")
    a = model.Lower_bound[key_stream, key_link, frame].value
    if flexibility_solution.get(key_link)is not None:
        b = int(flexibility_solution[key_link][-1][-1])
        mayor_max = max(a, b)
        #print(mayor_max)
        print(" ----------- mayor   ",mayor_max)
        #print("len ",len(flexibility_solution[link]))
        if len(flexibility_solution[key_link]) == 1:
            #print("value  ",flexibility_solution[link][-1])
            tiempo = (mayor_max, flexibility_solution[key_link][-1][-1]+model.Frame_Duration[key_stream, frame, key_link])
        else:
            #print("value  ",flexibility_solution[link][-1])
            tiempo = (mayor_max, mayor_max+model.Frame_Duration[key_stream,frame,key_link])
        #print("existe",tiempo)

    else:
        tiempo = (a, a+model.Frame_Duration[key_stream,frame,key_link])
        #print("no existe ",tiempo)
    return tiempo

def Latest_queue_available_time(key_link, Streams_Period):
    if flexibility_solution.get(key_link)is not None:
        tiempo = flexibility_solution[key_link][-1][-1]
        print("existe ",tiempo, key_link)
    else:
        tiempo = Streams_Period
        #print("no existe ",tiempo)
    return tiempo

def Earliest_queue_available_time(key_link, Streams_Period):
    if flexibility_solution.get(key_link)is not None:
        tiempo = flexibility_solution[key_link][-1][-1]
        #print("existe ",tiempo)
    else:
        tiempo = Streams_Period
    return tiempo

def Lower_bound(send_link, link, model, key_stream, frame, key_link, key_link_anterior):
    print("--link  ",link, "frame   ",frame, "  send_link  ",send_link, "  key_link_anterior  ",key_link_anterior)
    if frame == 0 and link == send_link:
        return 0.0
    elif frame >= 1  and link == send_link:
    #    print("2")
        return flexibility_solution[key_link][-1][0] + model.Frame_Duration[key_stream, frame, key_link]
    elif frame == 0 and link != send_link:
        #print(" 3  ",link,"   ",send_link)
        #print("flexi  ",flexibility_solution[key_link_anterior])
        return flexibility_solution[key_link_anterior][-1][0] + model.Frame_Duration[key_stream,frame,key_link] +  model.Max_Syn_Error    
    else:
    #    print("4  ")
        a = flexibility_solution[key_link][-1][0] + model.Frame_Duration[key_stream,frame,key_link]
        b = flexibility_solution[key_link_anterior][frame-1][0] + model.Frame_Duration[key_stream,frame,key_link] +  model.Max_Syn_Error
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

def Constraining_engress_port(model, key_stream, key_link, frame):
    #"bloquear value   " entre ello lo que hay que hacer
    #el eliminar lo generado en   --flexibility_solution--
    #print("NO se encontro solucion  ", flexibility_solution, "   value   ", value)
    #del flexibility_solution[value]
    model.Solution[key_stream, key_link, frame].fix(None)
