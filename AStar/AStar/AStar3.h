#pragma once
#include <list>
#include <algorithm>
#include <iostream>
#include <iomanip>
#include "../Point/Point3.h"
#include "../Map/WeightMap3.h"
#include "../Heuristics.h"

#define MIN(a, b) (((a) < (b)) ? (a) : (b))
#define MAX(a, b) (((a) > (b)) ? (a) : (b))
#define MAX_WEIGHT 1000.0f
#define MIN_WEIGHT 1.0f
#define LINEAR_WEIGHT 1.0f
#define DIAGONAL_2_WEIGHT 1.414f
#define DIAGONAL_3_WEIGHT 1.732f
#define WEIGHT_UP   2.0f
#define WEIGHT_DOWN 0.5f

struct Node3;

typedef std::unique_ptr<std::list<Point3>> Path3d;

typedef std::list<Node3> Nodes3;

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
    // TODO add paths cashe... ex.: std::map<std:pair<Point3, Point3>,Path3d> paths_cashe
    // TODO std::list<Node>& _open, std::list<Node>& _closed -> std::map<t_int32, Node3>_open, std::map<t_int32, Node3>& _closed or somthing similar...
    static Point3     _neighboursPoints[26];
    static float      _neighboursCost  [26];
    WeightMap3*       _map;
    // std::list<Point3> _path;
    // float             _path_cost;
    // Point3            _end, _start;

    bool   is_valid    (Point3& p)const;
    bool   point_exists(const Point3& p,      const float& cost,    Nodes3& _open, Nodes3& _closed)const;
    bool   fill_open   (const Point3& target, const Node3& current, Nodes3& _open, Nodes3& _closed, Heuristic3d heuristic);
    Path3d build_path  (const Point3& start,  const Point3& end,    Nodes3& closed);
    Path3d searh_path  (const Point3& start,  const Point3& end,    Heuristic3d heuristic);
	
public:
    AStar3(const int& rows, const int& cols, const int& layers, const float* map);

    ~AStar3();
    
    const WeightMap3& weights()const;

    Path3d search(const Point3& s, const Point3&, const int& heuristics);

    Path3d search(const int& heuristics);

    friend std::ostream& operator <<(std::ostream& stream, const AStar3& point);
};
