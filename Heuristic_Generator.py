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
Clean_offsets_collector = []
Feasibility_indicator = 0
flexibility_solution = {}


def Greedy_Heuristic(Stream_Source_Destination, Deathline_Stream, Streams_Period, Streams_size, Network_links, 
    Links, Num_Queues, Streams_paths, Num_of_Frames):

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
        print("-----------   value  -----------   ",value)
        while not success:
            booleano = Schedule_flow(Num_of_Frames_Dic[key], key, value, Deathline_Stream[key],Streams_paths_Dic[key],Streams_Period[key], Network_links_Dic)
            #Result_offsets.append(Result_offsets_gen)

            if booleano == True:
                #resultado del "algoritmo principal"
                print("SOLO ENTRA SI ES TRUE")
                success = True
            else:
                Constraining_engress_port()
                #linea 12 
                queue_assignment += 1
                #Ver si aun queda cola disponible
                if (queue_assignment > Queue_total[key]):
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
            lower_bound = Lower_bound(frame, send_link, link, link_anterior)
            Bound_dic = (lower_bound, Bound_dic[1])
            print("Bound_dic   ",Bound_dic)

            tiempo = Earliest_offset  (link,Bound_dic)
            print("tiempo schedule flow  ",tiempo)
            #MATRIX OFFSET, añadir valores
            #no se rellena correctamente 
            if flexibility_solution.get(link) is None:
                flexibility_solution[link] = [tiempo]
            else:
                flexibility_solution[link].append(tiempo)
            print("flexibility_solution ",flexibility_solution)

            #FRAME_INDICATOR 
            #print("///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////")
            #print("link   ",link, "   rever   ",tuple(reversed(link)))
            #@¶print("Network_links_Dic   ",Network_links_Dic)
            key_link = next((key for key, value in Network_links_Dic.items() if value == link or value == tuple(reversed(link))),None)
            frame_indicator = ("S", key, "L", key_link, "F", frame)
            #print("frane_indicator ", frame_indicator)

            helper = { "Task" :str(frame_indicator), "Start": tiempo[0], "Finish" : tiempo[-1], "Color" : key_link }
            clean_offset = { "Task" :str(frame_indicator), "Start": tiempo[0] }

            #print("helper    ",helper)
            Result_offsets.append(helper)
            Clean_offsets_collector.append(clean_offset)


            print("Result offset  ",Result_offsets)

            #print("///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////")

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
                upper_boud_posterior = Latest_queue_available_time(link, Streams_Period)
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

def Earliest_offset(link, Bound_dic):
    #EARLIEST OFFSET
    tiempo= 0.0
    if flexibility_solution.get(link)is not None:
        #print("len ",len(flexibility_solution[link]))
        if len(flexibility_solution[link]) == 1:
            print("value  ",flexibility_solution[link][-1])
            tiempo = (flexibility_solution[link][-1][-1], flexibility_solution[link][-1][-1]+100)
        else:
            print("value  ",flexibility_solution[link][-1])
            tiempo = (flexibility_solution[link][-1][-1], flexibility_solution[link][-1][-1]+100)
        print("existe",tiempo)
    else:
        tiempo = (Bound_dic[0],Bound_dic[0]+100)
        print("no existe ",tiempo)
    return tiempo

def Latest_queue_available_time(link, Streams_Period):
    if flexibility_solution.get(link)is not None:
        tiempo = flexibility_solution[link][-1][-1]
        print("existe ",tiempo)
    else:
        tiempo = Streams_Period
        print("no existe ",tiempo)
    return tiempo

def Lower_bound(frame, send_link, link, link_anterior):
   #print("link anterior  ",link_anterior, "frame   ",frame)
    if frame == 1 and link == send_link:
        print("1-lower_bound ",0.0)
        return 0.0
    elif frame >= 2  and link == send_link:
        #offset periodico --> producido anterior  +    #duracion de transmision ( 100 )
        print("2-lower_bound ",flexibility_solution[link][-1][0]+100)
        return flexibility_solution[link][-1][0] + 100 
    elif frame == 1 and link != send_link:
        #print(flexibility_solution[link_anterior][frame-1])
        print("3-lower_bound ",flexibility_solution[link_anterior][frame-1][0] + 100 +  0.8)
        return flexibility_solution[link_anterior][frame-1][0] + 100 +  0.8
    else:
        a = flexibility_solution[link][-1][0] + 100
        b = flexibility_solution[link_anterior][frame-1][0] + 100 +  0.8
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
    #"bloquear value   " entre ello lo que hay que hacer
    #el eliminar lo generado en   --flexibility_solution--
    print("NO se encontro solucion  ", flexibility_solution)
    del flexibility_solution[value]


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



#cfor n in [4]:
#c    
#c    #self.Network_links = Network_links
#c    Network_links = [(0, 1), (1, 3), (2, 3), (3, 0), (4, 3)]
#c    #self.Max_frames = Max_frames
#c    Max_frames = 1

#c    for i in range(1):
#c        # Evaluation_Function(number_of_nodes, connection_probability, number of streams)
#c        Evaluation_function_generator(2, 1, n)#, instance.Links, instance.Num_Queues)
        








