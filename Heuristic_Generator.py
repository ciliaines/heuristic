##################################### Heuristic Strategy starts here #####################################
#

from read import *
from Djikstra_Path_Calculator import *
from ILP_Generator import *
from RandStream_Parameters import *
from Preprocessing import *

from pyomo.environ import *
from pyomo.opt import SolverFactory
from pyomo.core import Var

Result_offsets = []

def Evaluation_function_generator(Number_of_edges, Connection_probability,Number_of_Streams):
    Number_of_edges, Number_of_Streams, Network_nodes, Network_links, Adjacency_Matrix, plot_network, Sources, Destinations, Stream_Source_Destination = Read()
    Streams_size , Streams_Period, Streams_Period_list, Deathline_Stream, Number_of_Streams = Read2(Number_of_Streams)
    network = Network_Topology(Adjacency_Matrix) 
    all_paths_matrix = all_paths_matrix_generator(Network_nodes, network)
    Streams_paths = Streams_paths_generator(all_paths_matrix, Stream_Source_Destination)

    scheduler = Clase_test(Network_links)
    instance, results = scheduler.instance, scheduler.results

    Frames_per_Stream, Max_frames, Num_of_Frames = Frames_per_Stream_generator(Streams_size)
    Num_of_Frames = [1,1,1]
    #print("---frames---",Num_of_Frames,"---",Max_frames)
    Streams_size=[10,20,30]

    Frame_Duration = Frame_Duration_Generator(Number_of_Streams, Max_frames, Network_links )
    #print("Frame_duration ", Frame_Duration)


    Greedy_Heuristic(Stream_Source_Destination, Deathline_Stream, Streams_Period, Streams_size, Network_links, instance.Links, instance.Num_Queues, 
        Streams_paths, Num_of_Frames) # aqui se convierte en flows

    return Result_offsets, Num_of_Frames, Streams_Period

def Greedy_Heuristic(Stream_Source_Destination, Deathline_Stream, Streams_Period, Streams_size, Network_links, 
    Links, Num_Queues, Streams_paths, Num_of_Frames):
    Result_offsets = []

    #Ordenar los flows para su tratamiento
    Sort_Stream_Source_Destination = Sort_flow(Stream_Source_Destination, Deathline_Stream, Streams_Period, Streams_size)
    #print("SHORT STREAMS   ",Sort_Stream_Source_Destination)
    #print("Streams_Period   ",Streams_Period)
    Num_of_Frames_Dic = {key: value for key, value in enumerate(Num_of_Frames)}
    #print("num of frames dic " ,Num_of_Frames_Dic)
    Streams_paths_Dic = {key: value for key, value in enumerate(Streams_paths)}
    #print("stream path  dic  ", Streams_paths_Dic)
    
    Network_links_Dic = {key: value for key, value in enumerate(Network_links)}
    Queue_Link_Dic = {}
    for key, value in Network_links_Dic.items():
        Queue_Link_Dic[key] = (Network_links_Dic[key], Num_Queues[key].value)
    #print("Queue_Link_Dic ",Queue_Link_Dic)

    #Cola total de cada uno de los flows
    Queue_total = List_queue(Sort_Stream_Source_Destination, Network_links_Dic, Queue_Link_Dic, Num_Queues, Streams_paths)
    for key, value in Sort_Stream_Source_Destination.items():
        success = False
        queue_assignment = 1

        while not success:
            booleano= Schedule_flow(Num_of_Frames_Dic[key], key, value, Deathline_Stream[key],Streams_paths_Dic[key],Streams_Period[key], Network_links_Dic)
            #Result_offsets.append(Result_offsets_gen)

            if booleano == True:
                #resultado del "algoritmo principal"
                print("SOLO ENTRA SI ES TRUE")
                success = True
            else:
                #linea 12 
                queue_assignment += 1
                #Ver si aun queda cola disponible
                if (queue_assignment > Queue_total[key] ):
                    #print("total cola  ", Queue_total[key])
                    #print("cuenta  ", queue_assignment)
                    success = True
    #return Result_offsets



def Schedule_flow(Num_of_Frames, key, value, Deathline, Streams_paths, Streams_Period, Network_links_Dic):
    #Definir uns estrucutre que enlace 
    #ENLACE(STEAMPATHS[A],STREAMPATHS[B])- (LOWERBOUND,UPPERBOUND)
    print("---------------------------------------------------------------------------------------------------")
    print("Streams_Period  ", Streams_Period)
    print("Num_of_Frames  ",Num_of_Frames)
    print("Streams_paths   ",Streams_paths)
    matriz_offset = {}

    for frame in range(Num_of_Frames): #tramas de cada link
        frame = frame + 1
        print("")
        print("Frames  ",frame)

        #BOUND_DIC  generamos una lsita con el lower y el upper bound
        lower_bound = 0.0
        Bound_dic = (lower_bound, Streams_Period)
        print("Bound_dic   ",Bound_dic)
        

        #LINK, bus queda del link, del link de revivo y del envio
        a = 0
        b = 1
        # Generar un vector con el primer y segundo valor
        send_link = (Streams_paths[a], Streams_paths[b])
        link = send_link
        reciving_link= (Streams_paths[-2], Streams_paths[-1])
        
        contador=1
        while contador < len(Streams_paths):
            print("")
           
            link_anterior = (Streams_paths[a-1],Streams_paths[b-1])
            lower_bound = Lower_bound(frame, send_link, link, link_anterior, matriz_offset)
            Bound_dic = (lower_bound, Bound_dic[1])
            print("Bound_dic   ",Bound_dic)

            tiempo, matriz_offset = Earliest_offset(link, matriz_offset,Bound_dic)
            print("tiempo schedule flow  ",tiempo)
            #MATRIX OFFSET, añadir valores
            #no se rellena correctamente 
            if matriz_offset.get(link) is None:
                matriz_offset[link] = [tiempo]
            else:
                matriz_offset[link].append(tiempo)
            print("matriz_offset ",matriz_offset)

            #FRAME_INDICATOR 
            print("///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////")
            print("link   ",link, "   rever   ",tuple(reversed(link)))
            print("Network_links_Dic   ",Network_links_Dic)
            key_link = next((key for key, value in Network_links_Dic.items() if value == link or value == tuple(reversed(link))),None)
            frame_indicator = ("S", key, "L", key_link, "F", frame)
            print("frane_indicator ", frame_indicator)

            helper = { "Task" :str(frame_indicator), "Start": tiempo[0], "Finish" : tiempo[-1], "Color" : key_link }
            print("helper    ",helper)
            Result_offsets.append(helper)
            print("Result offset  ",Result_offsets)
            print("///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////")

            if tiempo[-1] == float('inf'):
                return False
            elif tiempo[-1] <= Streams_Period:
                print("Tiempo elif  ",tiempo)
                #linea 11
                Bound_dic = tiempo
                print("Bound_dic",Bound_dic)

                a += 1
                b += 1
                if b >= len(Streams_paths):
                    break
                next_link = (Streams_paths[a], Streams_paths[b])
                print("next link ",next_link)
                link = next_link
                #linea 12 
                upper_boud_posterior = Latest_queue_available_time(link, Streams_Period,matriz_offset)
                print("Latest queue available time", upper_boud_posterior)

            else:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                #linea 15
                #lower_bound_anterior = #EARLIEST QUEUE AVAILABLE TIME
                a -= 1
                b -= 1
                link = [Streams_paths[a], Streams_paths[b]] 
            contador +=1
    return False#, Result_offsets 

def Earliest_offset(link, matriz_offset,Bound_dic):
    #EARLIEST OFFSET
    tiempo= 0.0
    if matriz_offset.get(link)is not None:
        #print("len ",len(matriz_offset[link]))
        if len(matriz_offset[link]) == 1:
            print("value  ",matriz_offset[link][-1])
            tiempo = (matriz_offset[link][-1][-1], matriz_offset[link][-1][-1]+100)
        else:
            print("value  ",matriz_offset[link][-1])
            tiempo = (matriz_offset[link][-1][-1], matriz_offset[link][-1][-1]+100)
        print("existe",tiempo)
    else:
        tiempo = (Bound_dic[0],Bound_dic[0]+100)
        print("no existe ",tiempo)
    return tiempo,matriz_offset

def Latest_queue_available_time(link, Streams_Period, matriz_offset):
    if matriz_offset.get(link)is not None:
        tiempo = matriz_offset[link][-1][-1]
        print("existe ",tiempo)
    else:
        tiempo = Streams_Period
        print("no existe ",tiempo)
    return tiempo

def Lower_bound(frame, send_link, link, link_anterior, matriz_offset):
   #print("link anterior  ",link_anterior, "frame   ",frame)
    if frame == 1 and link == send_link:
        print("1-lower_bound ",0.0)
        return 0.0
    elif frame >= 2  and link == send_link:
        #offset periodico --> producido anterior  +    #duracion de transmision ( 100 )
        print("2-lower_bound ",matriz_offset[link][-1][0]+100)
        return matriz_offset[link][-1][0] + 100 
    elif frame == 1 and link != send_link:
        #print(matriz_offset[link_anterior][frame-1])
        print("3-lower_bound ",matriz_offset[link_anterior][frame-1][0] + 100 +  0.8)
        return matriz_offset[link_anterior][frame-1][0] + 100 +  0.8
    else:
        a = matriz_offset[link][-1][0] + 100
        b = matriz_offset[link_anterior][frame-1][0] + 100 +  0.8
        print("4-lower_bound ",a,b, max(a,b))
        return max(a,b)

#Listar colas asociadas a la clave del link
def List_queue(Sort_Stream_Source_Destination, Network_links_Dic, Queue_Link_Dic, Num_Queues, Streams_paths):
    #print("Stream_Source_Destination_Dic ",Sort_Stream_Source_Destination)
    #print("other",Network_links, Num_Queues, Streams_paths)
    Queue_total = {}

    for vector in Streams_paths:
        firts_value = vector[0]
        last_value = vector[-1]
        for key, value in Sort_Stream_Source_Destination.items():
            if value == [firts_value, last_value]:
                vector_shearch = (vector[-2], vector[-1])  # Este es el vector que deseas buscar
                for clave, valor in Queue_Link_Dic.items():
                    if valor[0] == vector_shearch or tuple(reversed(valor[0])) == vector_shearch:
                        Queue_total[key] = (valor[1])
    
    #print(Queue_total)
    return Queue_total

#ordenar los flows dependiendo de las reglas 
def Sort_flow(Stream_Source_Destination, Deathline_Stream, Streams_Period, Streams_size):
    print(Streams_size)
    #Generate a diccionary  generar un diccionario del stream source destination para asi mantener al informcaion 
    Stream_Source_Destination_Dic = {key: value for key, value in enumerate(Stream_Source_Destination)}
    #Generate a diccionaty with the list Stream_size
    Streams_Size_Dic = {key: value for key, value in enumerate(Streams_size)}

    #Combine the keys of all three dictionaries into a list
    keys = sorted(set(Deathline_Stream.keys()) | set(Streams_Period.keys()) | set(Streams_Size_Dic.keys()))
    #Defines a function to sort the keys based on Deathline_Stream, Streams_Period and Streams_Size_Dic
    def sort_keys(key):
        value1 = Deathline_Stream.get(key, float('inf'))
        value2 = Streams_Period.get(key, float('inf'))
        value3 = Streams_Size_Dic.get(key, float('-inf'))
        #Sort first by Deathline_Stream, then by Streams_Period and finally by Streams_Size_Dic
        return (value1, value2, -value3)
    
    # Shot keys less to high
    sort_keys = sorted(keys, key=sort_keys)
    #print("SORT  KEYS",sort_keys)
    # sort deadthline line dictory short
    Sort_Deathline_Stream = {key: Deathline_Stream[key] for key in sort_keys}
    # keys list
    lista_de_claves = list(Sort_Deathline_Stream.keys())
    #Ordenar el diccionario segun la lista de las claves
    Sort_Stream_Source_Destination = {key: Stream_Source_Destination_Dic[key] for key in lista_de_claves}


    return Sort_Stream_Source_Destination

def Constraining_engress_port():
    return False

class Clase_test :
    
    def __init__(self, Network_links):

        self.Network_links = Network_links
        self.model = AbstractModel()

        self.model.Links = Set(initialize = frozenset(range(len(Network_links)))) # Links Ids
        self.model.Num_Queues = Var(self.model.Links, within=NonNegativeIntegers, initialize=1)

        self.model.Frames = Set(initialize= frozenset(range(Max_frames))) # Maximum number of streams

        ### This part is the creation of the instance in the ilp system
        opt = SolverFactory('gurobi')
        #opt = SolverFactory('gurobi', solver_io="python")
        self.instance = self.model.create_instance()
        self.results = opt.solve(self.instance)
        self.instance.solutions.load_from(self.results)



for n in [4]:
    
    #self.Network_links = Network_links
    Network_links = [(0, 1), (1, 3), (2, 3), (3, 0), (4, 3)]
    #self.Max_frames = Max_frames
    Max_frames = 1

    for i in range(1):
        # Evaluation_Function(number_of_nodes, connection_probability, number of streams)
        Evaluation_function_generator(2, 1, n)#, instance.Links, instance.Num_Queues)
        








