import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import pandas as pd

# Generar un gráfico de red (network topology)
def network_topology(Sources, Destinations):
    # Crear una red simple con NetworkX
    
    df = pd.DataFrame({'from':Sources, 'to':Destinations})
    G = nx.from_pandas_edgelist(df,'from','to')
    
    pos = nx.spring_layout(G)
    edge_x = []
    edge_y = []
                                    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)
                                                                                                                
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=4, color='black'),
        hoverinfo='none',
        mode='lines')
                                                                                                                        
    node_x = []
    node_y = []
                                                                                                                                
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
                                                                                                                                                                
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=list(G.nodes),
        textposition="bottom center",
        marker=dict(size=30, color='blue'),
        hoverinfo='text')
                                                                                                                                                                            
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(title="Network Topology", showlegend=False,
            xaxis=dict(
                showgrid=False,  # Quitar líneas de la grilla en el eje x
                zeroline=False,  # Quitar línea del origen en el eje x
                showticklabels=False,  # Quitar etiquetas en el eje x
            ),
            yaxis=dict(
                showgrid=False,  # Quitar líneas de la grilla en el eje y
                zeroline=False,  # Quitar línea del origen en el eje y
                showticklabels=False,  # Quitar etiquetas en el eje y
            )
    )
                                                                                                                                                                                    
    return fig

# Generar un gráfico de Gantt
def gantt_chart(Result_offsets, Repetitions, Streams_Period):

    data = [[frame['Task'], frame['Start']] for frame in Result_offsets]
    Repetitions = [repetition + 1 for repetition in Repetitions]
    color=['black', 'red', 'green', 'blue', 'cyan', 'magenta', 'yellow', 'grey', 'orange', 'pink','fuchsia']
    # This set of code is for generating the repetitions values in the dataset
    # For printing the full gant Chart
    New_offsets = []
    stream_index = 0
    for repetition in Repetitions :
        for frame in Result_offsets:
            substring = "'S', " +  str(stream_index)
            if substring in frame["Task"] :
                for i in range(int(repetition)) :
                    Repeated_Stream = {'Task' : frame["Task"] , 'Start' : frame["Start"] + Streams_Period[stream_index]*(i), 'Color' : color[frame["Color"]]}
                    New_offsets.append(Repeated_Stream)
        stream_index = stream_index + 1
    Result_offsets = New_offsets
    data = [[frame['Task'], frame['Start'], frame['Color']] for frame in New_offsets]
    df = pd.DataFrame(data, columns = ['Process_Name', 'Start', 'Color'])

    #df = px.data.gapminder().query("year == 2007").sort_values(by="gdpPercap", ascending=False)
                                                                                                                                                                                                
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[12]*len(df.Process_Name),
        y=df.Process_Name, 
        base=df.Start,
        orientation='h', 
        marker=dict(color=df.Color)))
    fig.update_layout(title="Gantt Chart", yaxis_title="Frames", xaxis_title="Times in microseconds")
                                                                                                                                                                                                                
    return fig

# Generar un cuadro de información
def info_box(Tiempo, Network_links, Repetition,Streams_Period, Link_order_Descriptor, Streams_links_path, offset, latency, queue_link, queue_stream):
    text = """
    Time:"""+str(Tiempo)+""" <br>
    Network links:"""+str(Network_links)+""" <br>
    Frames per stream:"""+str(Repetition)+""" <br>
    Stream periods: """+str(Streams_Period)+""" <br>
    Indexed link order per stream: """+str(Link_order_Descriptor)+""" <br>
    Stream paths: """+str(Streams_links_path)+""" <br>
    Offset: """+str(offset)+""" <br>
    Latency: """+str(latency)+""" <br>
    Queue link: """+str(queue_link)+""" <br>
    Queue stream: """+str(queue_stream)+""" <br>
    """
                                                                                                                                                                                                                                            
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0.5], y=[0.5], text=[text],
                             mode="text",
                             textposition="middle right"))
    fig.update_layout(title="Information Box", showlegend=False,
                      xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                      yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                      margin=dict(l=10, r=10, t=10, b=10))
    return fig

def combined(network_fig, gantt_fig, info_fig, file_image):
    # Guardar las figuras en un solo archivo HTML (interactivo)
    with open(file_image, "w") as f:
        f.write(network_fig.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write(gantt_fig.to_html(full_html=False, include_plotlyjs=False))
        f.write(info_fig.to_html(full_html=False, include_plotlyjs=False))
    
   
    
# Crear las tres figuras
#network_fig = create_network_topology()
#gantt_fig = create_gantt_chart()
#info_fig = create_info_box()


# Guardar una de las figuras como PNG
#network_fig.write_image("network_topology.png")
#gantt_fig.write_image("gantt_chart.png")
#info_fig.write_image("info_box.png")

