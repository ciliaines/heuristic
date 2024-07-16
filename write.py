import json 

def Write(input,Number_of_Streams, Streams_Period, Deathline_Stream, Streams_size, Stream_Source_Destination):
    #dic 1 switches
    #duplicar fichero json 
    original_file = 'Inputs/'+input+'_topo.json'
    duplicate_file = 'Resultado/'+input+'.json'

    with open(original_file, 'r', encoding='utf-8') as file:
       data = json.load(file)
    part_duplicate = data.get('switches', {})
    #with open(duplicate_file, 'w', encoding='utf-8') as file:
    #   json.dump(part_duplicate, file, ensure_ascii=False, indent=4)


    #PASO 1 crear un diccionarios con los datos 

    #dic 2 devices
    flows = []
    for key_stream in range(Number_of_Streams):
        print("key stream   ",key_stream)
    
        flow ={
                "name" : key_stream,
                "period" : Streams_Period[key_stream],
                "deathline" : Deathline_Stream[key_stream],
                "packetSize" : Streams_size[key_stream],
                "sourceDevice" : Stream_Source_Destination[key_stream][0],
                "endDevices" : Stream_Source_Destination[key_stream][1]
            }

                
        flows.append(flow)
    #PASO 2, escribirlo en un archivo json 
    datos = {
        "switches" : part_duplicate,
        "flows" : flows
    }
    with open(duplicate_file, 'w', encoding='utf-8') as file:
        json.dump(datos, file, ensure_ascii=False, indent=4 )
   
    
