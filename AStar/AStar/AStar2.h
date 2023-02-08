#pragma once
#include <list>
#include <algorithm>
#include <iostream>
#include <iomanip>
#include "../Point/Point2.h"
#include "../Map/WeightMap2.h"
#define MIN(a, b) (((a) < (b)) ? (a) : (b))
#define MAX(a, b) (((a) > (b)) ? (a) : (b))
#define MAX_WEIGHT 1000.0f
#define MIN_WEIGHT 1.0f
#define LINEAR_WEIGHT 1.0f
#define DIAGONAL_WEIGHT 1.414f


struct Node 
{
public:
    bool operator == (const Node&  o)const { return pos == o.pos; }
    bool operator == (const Point2& o)const { return pos == o; }
    bool operator  < (const Node&  o)const { return dist + cost < o.dist + o.cost; }
    Point2 pos;
    Point2 parent;
    float dist;
    float cost;
};


class AStar2
{
/// <summary>
///  TODO �������� ����������� �������� ����� 
/// </summary>
private:
    static Point2     _neighboursPoints[8];
    static float      _neighboursCost  [8];
    WeightMap2*       _map;
    std::list<Point2> _path;
    float             _path_cost;
    Point2            _end, _start;

    bool is_valid(Point2& p)const;
    
    bool point_exists(const Point2& p, const float cost, std::list<Node>& _open, std::list<Node>& _closed)const;
    
    bool fill_open(Node& n, std::list<Node>& _open, std::list<Node>& _closed);
    
    void build_path(std::list<Node>& closed);

    bool searh_path();
	
public:
    const Point2& end()const;
    const Point2& start()const;

    void set_end(const Point2& pt);
    void set_start(const Point2& pt);

    AStar2(const int& rows, const int& cols, const float* map);

    ~AStar2();
    
    const WeightMap2& weights()const;

    bool search(const Point2& s, const Point2& e);

    bool search();

    const std::list<Point2>& path()const;

    float path_cost()const;

    friend std::ostream& operator <<(std::ostream& stream, const AStar2& point);
};
