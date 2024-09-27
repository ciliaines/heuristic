##################################### Heuristic Strategy starts here #####################################
from pyomo.environ import *
from pyomo.opt import SolverFactory
from pyomo.core import Var
import bisect

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
        self.model.Num_Queues = Var(self.model.Links, within=NonNegativeIntegers, initialize=0)
        self.model.Latency = Var(self.model.Streams, within=Integers, initialize=0)
        self.model.Queue_Link_Dic = {}
        self.model.Frame_Offset = Var(self.model.Streams, self.model.Links, self.model.Frames, within=NonNegativeIntegers, initialize=0)
        self.model.Frame_Offset_up = Var(self.model.Streams, self.model.Links, self.model.Frames, within=NonNegativeIntegers, initialize=0)
        self.model.Streams_Offset = Var(self.model.Streams, within=NonNegativeIntegers, initialize=0 )

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
        cola =0
        while not success:
            booleano ,link = Schedule_flow(key_stream, value_stream, model, cola)
            Latency_Cal(key_stream, model)
            if booleano == True:
                success = True
                print("IF  ++++++++++++++ SOLUTION  ",model.Queue_Assignment[key_stream, link].value)
            else:
                Constraining_engress_port(model, key_stream,link,0)
                model.Queue_Assignment[key_stream, link] = model.Queue_Assignment[key_stream, link] + 1
                cola = cola+1
                print("ELSE +++++++++++++ SOLUTION  ",model.Queue_Assignment[key_stream, link].value)
                if model.Queue_Assignment[key_stream, link].value > 3:#model.Num_Queues[link].value:
                    #success = True
                    break

        #AQUI
        #primero comprobar la utilizacion
        utilizacion = 0.25
        utilizacion_hiperperiodo = utilizacion * model.Hyperperiod * 8
        #print("utilizacion hiperperiodo  ",utilizacion_hiperperiodo)
        #como compruebo la utilizacion
        count_valores = {} #cola link
        #print("flexibility_solution             ", flexibility_solution)
        for key1, subdict in flexibility_solution.items():
            for key2, lista_vectores in subdict.items(): 
                if count_valores.get(key2) is None:
                    count_valores[key2] = len(lista_vectores) * 100
                else:
                    count_valores[key2] += len(lista_vectores) * 100
        #COUNT UTILIZACION PORCENTAJE
        #print("contador de valores ",count_valores)      
        # condicion uno, media de todos los links superior x #la media de los valores ALL_VALUES SUMA DE TODOS LOS VALORES
        all_values = []
        for value in count_valores.values():
            all_values.append(value)
            # condicion dos  #cada uno de la utilicacion --> count  #si values son mas que el 20 porciento
            utilizacion_periodo = value / (model.Hyperperiod*8)
            #print(" utilizacion_periodo ", utilizacion_periodo, "  mayor 0,2")
            if utilizacion_periodo > 0.2: 
                #print("individual  SE ACABA ")
                return False           
        mean_values = sum(all_values) / len(all_values)
        #print("mean_values ", mean_values, "  mayor a la utilizacion_hiperperiodo  ", utilizacion_hiperperiodo  )
        if mean_values > utilizacion_hiperperiodo:
           #print("media SE ACABA")
           return False
        return True
        # si uno de los dos se cumpre escribir los resultado en el read --> WRITE
                                                                                                                                                                                                                                                                                                                                                                                           

def Schedule_flow(key_stream, value_stream, model,cola):
    print("  frames per stream    ", key_stream,  range(model.Frames_per_Stream[key_stream][0]))
    for frame in range(model.Frames_per_Stream[key_stream][0]):
        a = 0
        b = 1
        print("frameee ", frame)
        # Generar un vector con el primer y segundo valor
        send_link = (model.Streams_paths_Dic[key_stream][a], model.Streams_paths_Dic[key_stream][b])
        link = send_link
        key_link = next((key_stream for key_stream, value_stream in model.Network_links_Dic.items() if value_stream == link or value_stream == tuple(reversed(link))),None)
        reciving_link= (model.Streams_paths_Dic[key_stream][-2], model.Streams_paths_Dic[key_stream][-1])
        
        model.Lower_bound[key_stream, key_link, frame] = 0.0
        model.Upper_bound[key_stream, key_link, frame] = model.Streams_Period[key_stream]
        contador=1
        while contador < len(model.Streams_paths_Dic[key_stream]):
            #print("contador ", contador, len(model.Streams_paths_Dic[key_stream]))
            #Ecuacion 45
            link_anterior = (model.Streams_paths_Dic[key_stream][a-1],model.Streams_paths_Dic[key_stream][b-1])
            key_link_anterior = next((key_stream for key_stream, value_stream in model.Network_links_Dic.items() if value_stream == link_anterior or value_stream == tuple(reversed(link_anterior))),None)          
            lower_bound = Lower_bound(send_link, link, model, key_stream, frame, key_link, key_link_anterior)
            model.Lower_bound[key_stream, key_link, frame] = lower_bound
            #print(f"Lower_bound[{key_stream, key_link, frame}] = {value(model.Lower_bound[key_stream, key_link, frame])}")
            tiempo = Earliest_offset(model, frame, key_link, key_stream,cola)
            #print("tiempo  ", tiempo[0], "uuper ",  model.Upper_bound[key_stream, key_link, frame].value)
            #print("tiempo 2 ", tiempo[1])

            if model.Upper_bound[key_stream, key_link, frame].value == model.Hyperperiod.value+1:
                return False, key_link
            elif tiempo[1] <= model.Upper_bound[key_stream, key_link, frame].value:
                Add_Solution(key_link, tiempo, model, key_stream, cola)       
                model.Lower_bound[key_stream, key_link, frame] = tiempo[0]
                model.Upper_bound[key_stream, key_link, frame] = tiempo[1]
                model.Queue_Assignment[key_stream, key_link] = cola
                #print(f"Lower_bound[{key_stream, key_link, frame}] = {value(model.Lower_bound[key_stream, key_link, frame])}")
                #print(f"Upper_bound[{key_stream, key_link, frame}] = {value(model.Upper_bound[key_stream, key_link, frame])}")
                a += 1
                b += 1
                if b < len(model.Streams_paths_Dic[key_stream]):
                    next_link = (model.Streams_paths_Dic[key_stream][a], model.Streams_paths_Dic[key_stream][b])
                    link = next_link
                    key_link = next((key_stream for key_stream, value_stream in model.Network_links_Dic.items() if value_stream == link or value_stream == tuple(reversed(link))),None)
                    model.Upper_bound[key_stream, key_link, frame] = Latest_queue_available_time(key_link, model.Streams_Period[key_stream], model,cola)
                    print(f"Upper_boundlatest[{key_stream, key_link, frame}] = {value(model.Upper_bound[key_stream, key_link, frame])}")
                contador +=1
            else:
                a -= 1
                b -= 1
                link_next = (model.Streams_paths_Dic[key_stream][a], model.Streams_paths_Dic[key_stream][b])
                link = link_next
                key_link_next = next((key_stream for key_stream, value_stream in model.Network_links_Dic.items() if value_stream == link or value_stream == tuple(reversed(link))),None)
                key_link =key_link_next
                if key_link_next is not None:
                    model.Lower_bound[key_stream, key_link_next, frame] = Earliest_queue_available_time(key_link_next, model.Streams_Period[key_stream],cola)
                contador -=1
    return model.Latency[key_stream].value <= model.Deathline_Stream[key_stream], key_link

def Add_Solution(key_link, tiempo, model, key_stream, cola): #Es por las posibles repeticiones dentro de una trama 
    #print("key link ",key_link, " tiempo ", tiempo, " Hyperperiod", model.Hyperperiod.value, "period ", model.Streams_Period)
    resultado = model.Hyperperiod / model.Streams_Period[key_stream]
    i = 0
    while i < resultado:
        if flexibility_solution.get(cola) is None:
            flexibility_solution[cola] = {}
            flexibility_solution[cola][key_link] = [tiempo]
        else:
            if flexibility_solution[cola].get(key_link) is None:
                flexibility_solution[cola][key_link] = [tiempo]
            else:
                bisect.insort(flexibility_solution[cola][key_link], tiempo)
        #TIEMPO ESTE DENTRO DEL HYPERPERIODO
        tiempo = (tiempo[0] + model.Streams_Period[key_stream], tiempo[1]+model.Streams_Period[key_stream])
        i += 1

    #flexibility_solution[cola] = flexibility_solution
    #print("---cola  ",cola,"   flexibility_solution  ",flexibility_solution)

def Latency_Cal(key_stream, model):
    contador=1
    while contador < len(model.Streams_paths_Dic[key_stream]):
        link_ini = (model.Streams_paths_Dic[key_stream][0],model.Streams_paths_Dic[key_stream][1])
        link_end = (model.Streams_paths_Dic[key_stream][-2],model.Streams_paths_Dic[key_stream][-1])
        key_link_ini = next((key_stream for key_stream, value_stream in model.Network_links_Dic.items() if value_stream == link_ini or value_stream == tuple(reversed(link_ini))),None)
        key_link_end = next((key_stream for key_stream, value_stream in model.Network_links_Dic.items() if value_stream == link_end or value_stream == tuple(reversed(link_end))),None)
        model.Latency[key_stream] = model.Upper_bound[key_stream,key_link_end,0].value - model.Lower_bound[key_stream,key_link_ini,0].value
        contador +=1

def Earliest_offset(model, frame, key_link, key_stream,cola):
    tiempo= 0.0
    #print(f"Lower_bound[{key_stream, key_link, frame}] = {value(model.Lower_bound[key_stream, key_link, frame])}")
    a = model.Lower_bound[key_stream, key_link, frame].value
    if flexibility_solution.get(cola) is not None:
        if flexibility_solution.get(cola).get(key_link) is not None:
            b = Earliest_queue_available_time(key_link, model.Streams_Period[key_stream], cola)
            mayor_max = max(a, b)
            if len(flexibility_solution.get(cola)) == 1:
                tiempo = (mayor_max, flexibility_solution.get(cola)[key_link][-1][-1]+model.Frame_Duration[key_stream, frame, key_link])
            else:
                tiempo = (mayor_max, mayor_max+model.Frame_Duration[key_stream,frame,key_link])
            #print("existe",tiempo)

        else:
            tiempo = (a, a+model.Frame_Duration[key_stream,frame,key_link])
            #print("no existe ",tiempo)
    else:
        tiempo = (a, a+model.Frame_Duration[key_stream,frame,key_link])
    #print("tiempo  ", tiempo, "stream period  ",model.Streams_Period[key_stream])
    #if tiempo[0] == model.Streams_Period[key_stream]:
    #    tiempo = (-1, -1)
    return tiempo

def Latest_queue_available_time(key_link, Streams_Period,model,cola):
    values_flexibility_solution = flexibility_solution.get(cola)
    values = values_flexibility_solution.get(key_link)
    #values = {key: flexibility_solution[cola] for key in key_link}
    if values is not None:
        if values[-1][-1] == Streams_Period:
            print("1111dksfnslkdflsdnf")
            return model.Hyperperiod.value+1
        else:
            print("2222",values[-1][-1], "   ",Streams_Period)
            return max(values[-1][-1], Streams_Period)
        print("existe ", key_link)
    else:
        tiempo = Streams_Period
        print("no existe ",tiempo)
    tiempo = Streams_Period
    return tiempo

def Earliest_queue_available_time(key_link, Streams_Period, cola):
    values_flexibility_solution = flexibility_solution.get(cola)
    values = values_flexibility_solution.get(key_link)
    if values is not None:
       tiempo = values[-1][-1]
       for i in range(len(values) - 1):
            if values[i][1] != values[i + 1][0]:
                tiempo =  values[i][1]
                break
    else:
        tiempo = 0.0 #Streams_Period
    print("Earliest_queue_available_time ",tiempo)

    return tiempo

def Lower_bound(send_link, link, model, key_stream, frame, key_link, key_link_anterior):
    print("--link  ",link, "key_link ",key_link, "  send_link  ",send_link, "  key_link_anterior  ",key_link_anterior)
    #print("tiempo ", Earliest_queue_available_time(key_link, model.Streams_Period[key_st<ream]))
    if frame == 0 and link == send_link:
        return 0.0
    elif frame >= 1  and link == send_link:
    #    print("2")
        return model.Lower_bound[key_stream,key_link,frame] + model.Frame_Duration[key_stream, frame, key_link]
    elif frame == 0 and link != send_link:
        #print(" 3  ",link,"   ",send_link)
        return model.Lower_bound[key_stream,key_link_anterior, frame] + model.Frame_Duration[key_stream,frame,key_link_anterior] +  model.Max_Syn_Error
    else:
    #    print("4  ")
        a = model.Lower_bound[key_stream,key_link,frame] + model.Frame_Duration[key_stream, frame, key_link]
        b = model.Lower_bound[key_stream,key_link_anterior,frame] + model.Frame_Duration[key_stream,frame,key_link] +  model.Max_Syn_Error
        return max(a,b)

def Constraining_engress_port(model, key_stream, key_link, frame):
    #"bloquear value   " entre ello lo que hay que hacer
    #el eliminar lo generado en   --flexibility_solution--
    #print("NO se encontro solucion  ", flexibility_solution, "   value   ", value)
    #del flexibility_solution[key_link]
    model.Solution[key_stream, key_link, frame].fix(None)


##Listar colas asociadas a la clave del link
#def List_queue(model):
#    #print("Stream_Source_Destination_Dic ",Sort_Stream_Source_Destination)
#    #print("Network_links   ", Network_links_Dic, "Num_Queues",  Num_Queues, "Streams_paths", Streams_paths)
#    #print("Queue_Link_Dic  ",Queue_Link_Dic)
#    Queue_total = {}
#    for vector in model.Streams_paths:
#        firts_value = vector[0]
#        last_value = vector[-1]
#        for key, value in model.Sort_Stream_Source_Destination.items():
#            if value == [firts_value, last_value]:
#                vector_shearch = (vector[-2], vector[-1])  # Este es el vector que deseas buscar
#                for clave, valor in model.Queue_Link_Dic.items():
#                    if valor[0] == vector_shearch or tuple(reversed(valor[0])) == vector_shearch:
#                        model.Queue_total[key] = (valor[1])
#    
#    #print(Queue_total)
#    model.Queue_total = {0: 2, 1: 2, 2: 2, 3: 2}
#    return Queue_total