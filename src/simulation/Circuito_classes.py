from program import pre_solve
import networkx as nx
import matplotlib.pyplot as plt

class Barra:
    def __init__(self, id_barra, voltage, name):
        self.id = id_barra
        self.voltage = voltage
        self.name = name

    def __repr__(self):
        return f"Barra({self.id})"


class Conexão:
    def __init__(self, destino):
        self.destino = destino
    
    def __repr__(self):
        return f"Conexão(destino={self.destino})"
    
def pre_ACO() -> tuple[dict[int,list], dict[int,Barra]]:
    dss = pre_solve()
    
    dss_buses = dss.circuit.buses_names
    print("Buses in the circuit:", dss_buses)
    barras = {}
    for idx,b in enumerate(dss_buses):
        
        dss.circuit.set_active_bus(b)
        kv_base = dss.bus.kv_base
        barras[idx] = Barra(idx, kv_base*1000, b)
    
    
    lines = [l.replace("p","").split("_") for l in dss.lines.names]
    ## a estrutura atual de linhas é uma lista de listas, onde cada sublista contém os IDs das barras conectadas por aquela linha, onde as barras estão representadas por strings. quero que seja int
    connections = [[0,1]]+[[int(l[0]), int(l[1])] for l in lines]

    rede = {}
    ## Transforme a variável rede em um dicionário onde as chaves são os IDs das barras e os valores são listas de conexões (destinos)
    for l in connections:
        if l[0] not in rede:
            rede[l[0]] = []
        if l[1] not in rede:
            rede[l[1]] = []
        rede[l[0]].append(Conexão(l[1]))
        rede[l[1]].append(Conexão(l[0]))
    print("Rede:")
    print(rede)
    ## Imprima as barras
#     G = nx.Graph()
#
# # Adicionar nós com rótulo do nome (pode ser barra.name se quiser o nome do DSS)
#     for id_barra, barra in barras.items():
#         G.add_node(id_barra, label=barra.name)
#
#     # Adicionar arestas com base na rede
#     for origem, conexoes in rede.items():
#         for conexao in conexoes:
#             destino = conexao.destino
#             # Evitar duplicar arestas no grafo não-direcionado
#             if not G.has_edge(origem, destino):
#                 G.add_edge(origem, destino)
#
#     # Layout automático (spring ou planar se for radial)
#     pos = nx.spring_layout(G, seed=42)
#
#     # Desenhar nós
#     nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=700)
#
#     # Desenhar arestas
#     nx.draw_networkx_edges(G, pos)
#
#     # Desenhar rótulos dos nós com os nomes (ou use str(id_barra))
#     labels = {node: barras[node].name for node in G.nodes}
#     nx.draw_networkx_labels(G, pos, labels=labels, font_size=9, font_weight='bold')
#
#     # Mostrar
#     plt.title("Rede de Distribuição - Visualização das Barras e Conexões")
#     plt.axis('off')
#     plt.tight_layout()
#     plt.show()

    return rede,barras