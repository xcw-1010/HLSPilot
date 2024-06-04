#ifndef __GRAPH_H_
#define __GRAPH_H_

#include <vector>
#include <fstream>
#include <iostream>
#include <iterator>
#include <cstdlib>
#include <sstream>
#include <cmath>
#include <map>
#include <algorithm>

class Vertex {
    public:
        int idx;
        int inDeg;
        int outDeg;

        std::vector<int> inVid;
        std::vector<int> outVid;

        explicit Vertex(int _idx) {
            idx = _idx;
        }

        ~Vertex() {}
};

class Graph {
    public:
        int vertexNum;
        int edgeNum;
        std::vector<Vertex*> vertices;

        Graph(const std::string &fname);
        ~Graph() {
            for (int i = 0; i < vertexNum; i++) {
                delete vertices[i];
            }
        }

        void getRandomStartIndices(std::vector<int> &startIndices);
        void getStat();
    
    private:
        bool isUgraph;
        int getMaxIdx(const std::vector<std::vector<int>> &data);
        int getMinIdx(const std::vector<std::vector<int>> &data);
        void loadFile(
            const std::string &fName, 
            std::vector<std::vector<int>> &data
        );
};

class CSR {
    public:
        const int vertexNum;
        const int edgeNum;
        std::vector<int> rpao;
        std::vector<int> ciao;
        std::vector<int> rpai;
        std::vector<int> ciai;

        explicit CSR(const Graph &g);
        ~CSR();
};

#endif