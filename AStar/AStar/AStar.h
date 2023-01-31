#pragma once
#include <list>
#include <algorithm>
#include <iostream>
#include <iomanip>
#include "../Point/Point.h"
#include "../Map/WeightMap.h"
#define MIN(a, b) (((a) < (b)) ? (a) : (b))
#define MAX(a, b) (((a) > (b)) ? (a) : (b))
#define MAX_WEIGHT 1000.0f
#define MIN_WEIGHT 1.0f

struct Node 
{
public:
    bool operator == (const Node&  o)const { return pos == o.pos; }
    bool operator == (const Point& o)const { return pos == o; }
    bool operator  < (const Node&  o)const { return dist + cost < o.dist + o.cost; }
    Point pos;
    Point parent;
    float dist;
    float cost;
};

class AStar 
{

private:
    static Point neighboursPoints[8];
    // Point*           _neighbours;
    WeightMap*       _map;
    std::list<Point> _path;
    float            _path_cost;
    Point _end, _start;

    bool is_valid(Point& p)const;

    bool point_exists(const Point& p, const float cost, std::list<Node>& _open, std::list<Node>& _closed)const;

    bool fill_open(Node& n, std::list<Node>& _open, std::list<Node>& _closed);

    void build_path(std::list<Node>& closed);
	
public:
    const Point& end()const;
    const Point& start()const;

    void set_end(const Point& pt);
    void set_start(const Point& pt);

    AStar(const int rows, const int cols, const float* map);

    ~AStar();
    
    const WeightMap& weights()const;

    bool search(const Point& s, const Point& e);

    bool search();

    const std::list<Point>& path()const;

    float path_cost()const;

    friend std::ostream& operator <<(std::ostream& stream, const AStar& point);
};
