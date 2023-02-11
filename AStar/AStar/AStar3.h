#pragma once
#include <list>
#include <algorithm>
#include <iostream>
#include <iomanip>
#include "../Point/Point3.h"
#include "../Map/WeightMap3.h"
#include "../Heuristics.h"
#include <map>


#define MIN(a, b) (((a) < (b)) ? (a) : (b))
#define MAX(a, b) (((a) > (b)) ? (a) : (b))
#define MAX_WEIGHT 1000.0f
#define MIN_WEIGHT 1.0f
#define LINEAR_WEIGHT 1.0f
#define DIAGONAL_2_WEIGHT 1.414f
#define DIAGONAL_3_WEIGHT 1.732f
#define WEIGHT_UP   2.0f
#define WEIGHT_DOWN 0.5f

class Path3d
{
public:
    std::list<Point3> path;
    float cost = 0.0f;
};

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
private:
    // TODO std::list<Node>& _open, std::list<Node>& _closed -> std::map<t_int32, Node3>_open, std::map<t_int32, Node3>& _closed or somthing similar...
    static Point3     _neighboursPoints[26];
    static float      _neighboursCost  [26];
    WeightMap3*       _map;
    Path3d            _empty_path;
    std::map<Points2dPairHash, Path3d*> _paths_cashe;

    bool   is_valid         (Point3& p)const;
    bool   point_exists     (const Point3& p,      const float& cost,    std::list<Node3>& _open, std::list<Node3>& _closed)const;
    bool   fill_open        (const Point3& target, const Node3& current, std::list<Node3>& _open, std::list<Node3>& _closed, Heuristic3d heuristic);
    const Path3d& build_path(const Point3& start,  const Point3& end,    std::list<Node3>& closed);
    const Path3d& searh_path(const Point3& start,  const Point3& end,    Heuristic3d heuristic);
	
public:
    AStar3(const int& rows, const int& cols, const int& layers, const float* map);
    ~AStar3();
    const WeightMap3& weights()const;
    const Path3d& search     (const Point3& s, const Point3&, const int& heuristics = MANHATTAN_DISTANCE);
    const Path3d& search     (const int& heuristics = MANHATTAN_DISTANCE);
    friend std::ostream& operator <<(std::ostream& stream, const AStar3& point);
};
