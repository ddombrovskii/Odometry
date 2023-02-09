#pragma once
#include <list>
#include <algorithm>
#include <iostream>
#include <iomanip>
#include "../Point/Point3.h"
#include "../Map/WeightMap3.h"
#define MIN(a, b) (((a) < (b)) ? (a) : (b))
#define MAX(a, b) (((a) > (b)) ? (a) : (b))
#define MAX_WEIGHT 1000.0f
#define MIN_WEIGHT 1.0f
#define LINEAR_WEIGHT 1.0f
#define DIAGONAL_2_WEIGHT 1.414f
#define DIAGONAL_3_WEIGHT 1.732f
#define WEIGHT_UP   2.0f
#define WEIGHT_DOWN 0.5f


struct Node3 
{
public:
    bool operator == (const Node3&  o)const { return pos == o.pos; }
    bool operator == (const Point3& o)const { return pos == o; }
    bool operator  < (const Node3&  o)const { return dist + cost < o.dist + o.cost; }
    Point3 pos;
    Point3 parent;
    float dist;
    float cost;
};


class AStar3
{
/// <summary>
///  TODO добавить кеширование запросов путей 
/// </summary>
private:
    static Point3     _neighboursPoints[26];
    static float      _neighboursCost  [26];
    WeightMap3*       _map;
    std::list<Point3> _path;
    float             _path_cost;
    Point3            _end, _start;

    bool is_valid(Point3& p)const;
    
    bool point_exists(const Point3& p, const float& cost, std::list<Node3>& _open, std::list<Node3>& _closed)const;
    
    bool fill_open(Node3& n, std::list<Node3>& _open, std::list<Node3>& _closed);
    
    void build_path(std::list<Node3>& closed);

    bool searh_path();
	
public:
    const Point3& end()const;
    const Point3& start()const;

    void set_end(const Point3& pt);
    void set_start(const Point3& pt);

    AStar3(const int& rows, const int& cols, const int& layers, const float* map);

    ~AStar3();
    
    const WeightMap3& weights()const;

    bool search(const Point3& s, const Point3& e);

    bool search();

    const std::list<Point3>& path()const;

    float path_cost()const;

    friend std::ostream& operator <<(std::ostream& stream, const AStar3& point);
};
