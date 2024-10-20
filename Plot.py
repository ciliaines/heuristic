import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
import pandas as pd

# Generar un gráfico de red (network topology)
def network_info_topology(name,Sources, Destinations,Network_links, Repetition,Streams_Period, Link_order_Descriptor, Streams_links_path):
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Network Topology", "Information Box"))
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
        mode='lines',
        name="links")
                                                                                                                        
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
        textposition="top center",
        marker=dict(size=30, color='blue'),
        hoverinfo='text',
        name="edges")


    fig.add_trace(edge_trace, row=1, col=1)
    fig.add_trace(node_trace, row=1, col=1)

    text = """
    Network links:"""+str(Network_links)+""" <br>
    Frames per stream:"""+str(Repetition)+""" <br>
    Stream periods: """+str(Streams_Period)+""" <br>
    Indexed link order per stream: """+str(Link_order_Descriptor)+""" <br>
    Stream paths: """+str(Streams_links_path)+""" <br>
    """
    text_trace = go.Scatter(x=[0.5], y=[0.5], text=[text],
                             mode="text", 
                             textposition="top center",
                             name="info")

    fig.add_trace(text_trace, row=1, col=2)
    fig.update_layout(height=1200, width=1600, title_text=name,
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))       
    fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False, row=1, col=1 )                                                                                                                                                                    
    fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=False, row=1, col=1 )                                                                                                                                                                    
    fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False, row=1, col=2 )                                                                                                                                                                    
    fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=False, row=1, col=2 )                                                                                                                                                                    

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
    for repetition in Repetitions:
        for frame in Result_offsets:
            substring = "'S', " +  str(stream_index)
            if substring in frame["Task"] :
                for i in range(int(repetition)):
                    Repeated_Stream = {'Task' : frame["Task"] , 'Start' : frame["Start"] + Streams_Period[stream_index]*(i), 'Color' : color[frame["Color"]]}
                    New_offsets.append(Repeated_Stream)
        stream_index = stream_index + 1
    Result_offsets = New_offsets
    data = [[frame['Task'], frame['Start'], frame['Color']] for frame in New_offsets]
    df = pd.DataFrame(data, columns = ['Process_Name', 'Start', 'Color'])
                                                                                                                                                                                                
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[12]*len(df.Process_Name),
        y=df.Process_Name, 
        base=df.Start,
        orientation='h', 
        marker=dict(color=df.Color)))
    fig.update_layout(title="Gantt Chart", yaxis_title="Frames", xaxis_title="Times in microseconds")
                                                                                                                                                                                                                
    return fig

# Generar tablas de resultado
def result_box(Tiempo, offset, latency, queue_link, queue_stream):
    #Tablas
    fig = make_subplots(rows=1, cols=4, specs=[[{"type":"table"},{"type":"table"}, {"type":"table"}, {"type":"table"}]])
    #Tiempo
    fig.add_trace(go.Table(
        header=dict(values=['Time'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[Tiempo],
                    fill_color='lavender',
                    align='left')
        ),
        row=1,
        col=1,
    )
    #Latencia
    rows = [row for row in str(latency).strip().split("<br>") if row]
    stream=[]
    latency=[]
    for row in rows:
        if "is" in row:
            key, value = row.split(" is ")
            stream.append(key.strip())
            latency.append(value.strip())

    fig.add_trace(go.Table(
        header=dict(values=['Stream', 'Latency'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[stream,latency],
                   fill_color='lavender',
                    align='left')
        ),
        row=1,
        col=2,
    )

    #Queue
    rows = [row for row in str(queue_link).strip().split("<br>") if row]
    links=[]
    queue=[]
    total=0

    for row in rows:
        if "is" in row:
            key, value = row.split(" is ")
            total +=int(value)
            links.append(key.strip())
            queue.append(value.strip())
    links.append("Total")
    queue.append(total)

    fig.add_trace(go.Table(
        header=dict(values=['Links', 'Queue'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[links,queue],
                    fill_color='lavender',
                    align='left')
        ),
        row=1,
        col=3,
    )
    rows = [row for row in str(offset).strip().split("<br>") if row]
    stream=[]
    link=[]
    offset=[]

    for row in rows:
        if "is" in row:
            key1, key2 = row.split(" for ")
            key2, value = key2.split(" is ")
            stream.append(key1.strip())
            link.append(key2.strip())
            offset.append(value.strip())


    fig.add_trace(go.Table(
        header=dict(values=['Stream','Links', 'Offset'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[stream,link,offset],
                    fill_color='lavender',
                    align='left')
        ),
        row=1,
        col=4,
    )

    fig.update_layout(width=1000, height=600, title_text="Results Table")                     
    return fig

def combined(network_fig, gantt_fig, result_fig, file_image):
    # Guardar las figuras en un solo archivo HTML (interactivo)
    with open(file_image, "w") as f:
        f.write(network_fig.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write(gantt_fig.to_html(full_html=False, include_plotlyjs=False))
        #f.write(info_fig.to_html(full_html=False, include_plotlyjs=False))
        f.write(result_fig.to_html(full_html=False, include_plotlyjs=False))
