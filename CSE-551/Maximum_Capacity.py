import pandas as pd
import networkx as nx

class CapacityModel:

    def __init__(self, path='flight_data.csv'):

        self.flights = self.getData(path)
        self.flights = self.dataPreProcessing(self.flights)
        self.graph = self.graphGenerate(self.flights)
        self.min_capacity = float('inf')
        self.visited = []

    def getData(self, path):
        flights = pd.read_csv(path)
        return flights

    def graphGenerate(self, flights: pd.DataFrame):

        '''
        :param flights: pd.DataFrame
        :return: nx.MultiDiGraph
        '''

        graph = nx.MultiDiGraph()
        graph.add_nodes_from(['LAX', 'SFO', 'PHX', 'SEA', 'DEN', 'ATL', 'ORD', 'BOS', 'IAD', 'JFK'])
        edge_list=[]

        for rows in flights.iterrows():
            dept = rows[1]['departure']
            arr = rows[1]['arrival']
            data = {}
            data['dept'] = rows[1]['dept_time']
            data['arr'] = rows[1]['arr_time']
            data['capacity'] = rows[1]['capacity']
            edge_list.append((dept, arr, data))

        for x in edge_list:
            graph.add_edge(x[0], x[1], dept=x[2]['dept'], arr=x[2]['arr'], capacity=x[2]['capacity'])


        return graph

    def roundoffTime(self, time: str):

        '''
        :param time: str
        :return: str
        '''

        minutes = time.split(':')[1]
        hour = time.split(':')[0]

        if minutes <= '30':
            time = hour + ':' '00'
        else:
            if (int(hour)+1)%25 < 10:
                time = '0' + str((int(hour)+1)%25) + ':' + '00'
            else:
                time = str((int(hour)+1)%25) + ':' + '00'

        return time


    def dataPreProcessing(self, flights: pd.DataFrame):

        flights['dept_time'] = flights['dept_time'].apply(self.roundoffTime)
        flights['arr_time'] = flights['arr_time'].apply(self.roundoffTime)

        return flights



    def getMinCapacity(self, edge, deptTime, visited_nodes):

        '''
        Modified Ford Fulkerson approach
        '''

        print(edge)
        print(deptTime)

        if deptTime >= 24:
            self.min_capacity = 0
            self.visited.append(edge)
            return self.min_capacity

        if edge[1] == "JFK":

            if self.min_capacity > edge[2]['capacity']:
                self.min_capacity = edge[2]['capacity']

            edge[2]['capacity'] = edge[2]['capacity'] - self.min_capacity

            if edge[2]['capacity'] == 0:
                self.visited.append(edge)

            return self.min_capacity


        new_neighbors = []
        neighbors = []

        for e in self.graph.edges(edge[1], data=True):
            if e[2]['dept'] >= edge[2]['arr']:
                if e not in self.visited:
                     if e[0] not in visited_nodes:
                        neighbors.append(e)

        new_edge = []
        for e in neighbors:
            if e[2]['capacity'] > 0:
                new_edge.append(e)

        if len(new_edge)==0:
            self.min_capacity = 0
            self.visited.append(edge)
            return self.min_capacity
        if self.min_capacity > edge[2]['capacity']:
            self.min_capacity = edge[2]['capacity']

        t1 = int(new_edge[0][2]['arr'].split(":")[0])
        t2 = int(edge[2]['arr'].split(":")[0])

        if t1<t2:
            t2 = 24 - t2
            t1 = t2+t1
        else:
            t1= t1-t2

        deptTime = deptTime + (t1)
        visited_nodes.append(new_edge[0][0])
        self.getMinCapacity(new_edge[0], deptTime,visited_nodes)

        edge[2]['capacity'] = edge[2]['capacity'] - self.min_capacity

        if edge[2]['capacity'] == 0:
            self.visited.append(edge)

        return self.min_capacity


    def countCapacity(self):

        '''
        :return: int capacity
        '''

        final_capacity = 0
        neighbors = [edge for edge in self.graph.edges("LAX", data=True)]
        i  = 0
        n = len(neighbors)
        visited_nodes=[]
        nodes=["LAX","temp"]

        while(i < n):

            if neighbors[i] not in self.visited:

                t1 = int(neighbors[i][2]['arr'].split(":")[0])
                t2 = int(neighbors[i][2]['dept'].split(":")[0])

                if t1<t2:
                    t2 = 24 - t2
                    t1 = t2+t1
                else:
                    t1= t1-t2

                visited_nodes=[]
                visited_nodes.append("LAX")

                if neighbors[i][1] not in nodes:
                    nodes.pop()
                    nodes.append(neighbors[i][1])
                    self.visited=[]

                temp = self.getMinCapacity(neighbors[i],t1,visited_nodes)
                final_capacity = final_capacity + temp
                self.min_capacity = 10000

            else:
                i = i+1
                continue

        return final_capacity


if __name__ == '__main__':

    model = CapacityModel('flight_data.csv')
    print ("Maximum Capacity: ",model.countCapacity())
