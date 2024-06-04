#include "graph.h"

#include <cstdlib>
#include <iostream>
#include <fstream>

void Graph::loadFile(
    const std::string &gName, 
    std::vector<std::vector<int>> &data
) {
    std::ifstream fhandle(gName.c_str());
    if (!fhandle.is_open()) {
        std::cout << "Failed to open " << gName << std::endl;
    }

    std::string line;
    while (std::getline(fhandle, line)) {
        std::istringstream iss(line);
        data.push_back(
            std::vector<int>(
                std::istream_iterator<int>(iss), 
                std::istream_iterator<int>()
            )  
        );
    }
    fhandle.close();
}

int Graph::getMaxIdx(const std::vector<std::vector<int>> &data) {
    int maxIdx = data[0][0];
    for (auto it1 = data.begin(); it1 != data.end(); it1++) {
        for (auto it2 = it1->begin(); it2 != it1->end(); it2++) {
            if (maxIdx <= (*it2)) {
                maxIdx = *it2;
            }
        }
    }
    return maxIdx;
}

int Graph::getMinIdx(const std::vector<std::vector<int>> &data) {
    int minIdx = data[0][0];
    for (auto it1 = data.begin(); it1 != data.end(); it1++) {
        for (auto it2 = it1->begin(); it2 != it1->end(); it2++) {
            if (minIdx <= (*it2)) {
                minIdx = *it2;
            }
        }
    }
    return minIdx;
}

Graph::Graph(const std::string &gName) {
    // Check if it is undirectional graph
    auto found = gName.find("ungraph", 0);
    if (found != std::string::npos) {
        isUgraph = true;
    } else {
        isUgraph = false;
    }

    std::vector<std::vector<int>> data;
    loadFile(gName, data);
    vertexNum = getMaxIdx(data) + 1;
    edgeNum = (int) data.size();

    std::cout << "vertex num: " << vertexNum << std::endl;
    std::cout << "edge num: " << edgeNum << std::endl;

    for (int i = 0; i < vertexNum; i++) {
        Vertex* v = new Vertex(i);
        vertices.push_back(v);
    }

    for (auto it = data.begin(); it != data.end(); it++) {
        int srcIdx = (*it)[0];
        int dstIdx = (*it)[1];

        vertices[srcIdx]->outVid.push_back(dstIdx);
        vertices[dstIdx]->inVid.push_back(srcIdx);

        if (isUgraph && srcIdx != dstIdx) {
            vertices[dstIdx]->outVid.push_back(srcIdx);
            vertices[srcIdx]->inVid.push_back(dstIdx);
        }
    }

    for (auto it = vertices.begin(); it != vertices.end(); it++) {
        (*it)->inDeg = (int)(*it)->inVid.size();
        (*it)->outDeg = (int)(*it)->outVid.size();
    }
}

CSR::CSR(const Graph &g) : vertexNum(g.vertexNum), edgeNum(g.edgeNum) {
    rpao.resize(vertexNum + 1);
    rpai.resize(vertexNum + 1);
    rpao[0] = 0;
    rpai[0] = 0;
    for (int i = 0; i < vertexNum; i++) {
        rpao[i + 1] = rpao[i] + g.vertices[i]->outDeg;
        rpai[i + 1] = rpai[i] + g.vertices[i]->inDeg;
    }

    // Sort the input and output vertex
    for (int i = 0; i < vertexNum; i++) {
        std::sort(g.vertices[i]->outVid.begin(), g.vertices[i]->outVid.end());
        std::sort(g.vertices[i]->inVid.begin(), g.vertices[i]->inVid.end());
        for (auto id : g.vertices[i]->outVid) {
            ciao.push_back(id);
        }
        for (auto id : g.vertices[i]->inVid) {
            ciai.push_back(id);
        }
    }
}