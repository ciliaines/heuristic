import json 
from datetime import datetime

def Write(input,input_timestamp, Number_of_Streams, Streams_Period, Deathline_Stream, Streams_size, Stream_Source_Destination):
    original_file = 'Inputs/'+input+'_topo.json'
    duplicate_file = 'Resultado/'+ input_timestamp + '.json'
    with open(original_file, 'r', encoding='utf-8') as file:
       data = json.load(file)
    part_duplicate = data.get('switches', {})
    flows = []
    for key_stream in range(Number_of_Streams):  
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
   
    
