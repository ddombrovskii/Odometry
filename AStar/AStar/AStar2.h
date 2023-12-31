#pragma once
#include <list>
#include <algorithm>
#include <iostream>
#include <iomanip>
#include "../Point/Point2.h"
#include "../Map/WeightMap2.h"
#include "../Heuristics.h"
#include <unordered_map>

#define MIN(a, b) (((a) < (b)) ? (a) : (b))
#define MAX(a, b) (((a) > (b)) ? (a) : (b))
#define LINEAR_WEIGHT 1.0f
#define DIAGONAL_WEIGHT 1.414f

class Path2d 
{
public:
    std::list<Point2> path;
    float cost = -1.0f;
};

struct Node2
{
public:
    float total_cost() const { return dist + cost; }
    bool operator == (const Node2&  o) const { return pos == o.pos; }
    bool operator == (const Point2& o) const { return pos == o; }
    bool operator  < (const Node2&  o) const { return dist + cost < o.dist + o.cost; }
    bool operator  <= (const Node2& o) const { return dist + cost <= o.dist + o.cost; }
    Point2  pos;
    Point2 parent;
    float   dist;
    float   cost;
};

typedef std::unordered_map<int, Node2> nodes_map_2d;
// TODO
// ��������� ���������� ���������� ���������� �����
// �������� ����� ������������ ������ ���������( ��� ������ �� ��� ������������ �����������)
// ����������� �������� ������� ������(���� �� ����� ���� -> ������� ��� � ������ � ����� �������)
// ����� ��������� ������
// ������ � ���������� �������
// �������� ��������� ��� ������ � ������(�������� � �������� / ������ �������������� / )
// �� ����������� �������� ���������� ����������� ��������� ���������� � ������
// �������� �� ����� � �������������� �� �������
class AStar2
{
private:
    static Point2     _neighboursPoints[8];
    static float      _neighboursCost  [8];
    Path2d            _empty_path;
    WeightMap2*       _map;
    std::unordered_map<Points2dPairHash, Path2d*> _paths_cashe;

    bool  is_valid          (const Point2& target)const;
    bool  fill_open         (const Point2& start,  const Point2& target, const Node2& current, nodes_map_2d& _open, nodes_map_2d& _closed, Heuristic2d heuristic)const;
    const Path2d& build_path(const Point2& start,  const Point2& end,    nodes_map_2d& closed);
    const Path2d& searh_path(const Point2& start,  const Point2& end,    Heuristic2d heuristic);
	
public:

    AStar2(const int& rows, const int& cols, const float* map);
    ~AStar2();
    const WeightMap2& weights()const;
    const Path2d&     search (const Point2& start, const Point2& end, const int& heuristics = DIAGONAL);
    const Path2d&     search (const int& heuristics = DIAGONAL);
    friend std::ostream& operator <<(std::ostream& stream, const AStar2& point);
};
