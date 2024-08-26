import subprocess

script1 = 'Heuristic_Visualizer.py'
script2 = 'Solutions_Visualizer.py'
#ejecutar x veces
#por ahora 5 veces
for i in range(5):
    print(" Proceso numero", i)
    #primero el heuristic Visualization
    print(" Heuristico ")
    subprocess.run(['python', script1])

    #cuando acabe ejecuto el solution Visualization
    print(" ILP  ")
    subprocess.run(['python', script2])

print("terminado")



