#pragma once
#include <list>
#include <algorithm>
#include <iostream>
#include <iomanip>
#include "../Point/Point2.h"
#include "../Map/WeightMap2.h"
#include "../Heuristics.h"
#define MIN(a, b) (((a) < (b)) ? (a) : (b))
#define MAX(a, b) (((a) > (b)) ? (a) : (b))
#define MAX_WEIGHT 1000.0f
#define MIN_WEIGHT 1.0f
#define LINEAR_WEIGHT 1.0f
#define DIAGONAL_WEIGHT 1.414f

typedef std::unique_ptr<std::list<Point2>> Path2d;


struct Node 
{
public:
    bool operator == (const Node&  o) const { return pos == o.pos; }
    bool operator == (const Point2& o)const { return pos == o; }
    bool operator  < (const Node&  o) const { return dist + cost < o.dist + o.cost; }
    Point2 pos;
    Point2 parent;
    float dist;
    float cost;
};


class AStar2
{
/// <summary>
///  TODO добавить кеширование запросов путей 
/// </summary>
private:
    // TODO add paths cashe... ex.: std::map<std:pair<Point2, Point2>,Path2d> paths_cashe
    // TODO std::list<Node>& _open, std::list<Node>& _closed -> std::map<t_int32, Node>_open, std::map<t_int32, Node>& _closed or somthing similar...
    static Point2     _neighboursPoints[8];
    static float      _neighboursCost  [8];
    WeightMap2*       _map;

    bool is_valid(Point2& p)const;
    
    bool point_exists(const Point2& p, const float cost, std::list<Node>& _open, std::list<Node>& _closed)const;
    
    bool fill_open(const Point2& target, const Node& current, std::list<Node>& _open, std::list<Node>& _closed, Heuristic2d heuristic);
    
    Path2d build_path(const Point2& start, const Point2& end, std::list<Node>& closed);

    Path2d searh_path(const Point2& start, const Point2& end, Heuristic2d heuristic);
	
public:

    AStar2(const int& rows, const int& cols, const float* map);

    ~AStar2();
    
    const WeightMap2& weights()const;

    Path2d search(const Point2& s, const Point2& e, const int& heuristics = MANHATTAN_DISTANCE);
    
    Path2d search(const int& heuristics = MANHATTAN_DISTANCE);

    friend std::ostream& operator <<(std::ostream& stream, const AStar2& point);
};
