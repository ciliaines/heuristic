import subprocess

script1 = 'Heuristic_Visualizer.py'
script2 = 'Solutions_Visualizer.py'

#ejecutar x veces
#por ahora 5 veces
for i in range(20):
    print(" Proceso numero", i)
    
    #primero el heuristic 
    print(" Heuristico ")
    subprocess.run(['python', script1], timeout=600)

    #segundo el  ILP Latencia 1 cola 0
    print(" ILP  latencia 1 cola 0 ")
    subprocess.run(['python', script2, '1','0'], timeout=600)

    #tercero el  ILP Latencia 0 cola 1
    print(" ILP  latencia 0 cola 1")
    subprocess.run(['python', script2, '0','1'], timeout=600)

    #cuarto el  ILP Latencia 0.5 cola 0.5
    print(" ILP  latencia 0.5 cola 0.5")
    subprocess.run(['python', script2, '0.5','0.5'], timeout=600)

print("terminado")



