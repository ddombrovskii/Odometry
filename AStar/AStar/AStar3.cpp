#include "AStar3.h"
#include <cassert>

Point3 AStar3::_neighboursPoints[26] =
{
    /// <summary>
    /// layer -1
    /// </summary>
    Point3(-1, -1, -1),
    Point3( 1, -1, -1),
    Point3(-1,  1, -1),
    Point3( 1,  1, -1),
    Point3( 0,  0, -1),
    Point3( 0, -1, -1),
    Point3(-1,  0, -1),
    Point3( 0,  1, -1),
    Point3( 1,  0, -1),
    /// <summary>
   /// layer 0
   /// </summary>
   Point3(-1, -1, 0),
   Point3( 1, -1, 0),
   Point3(-1,  1, 0),
   Point3( 1,  1, 0),
   // Point3( 0,  0, 0), <- we are here
   Point3( 0, -1, 0),
   Point3(-1,  0, 0),
   Point3( 0,  1, 0),
   Point3( 1,  0, 0),
   /// <summary>
   /// layer +1
   /// </summary>
   Point3(-1, -1, 1),
   Point3( 1, -1, 1),
   Point3(-1,  1, 1),
   Point3( 1,  1, 1),
   Point3( 0,  0, 1),
   Point3( 0, -1, 1),
   Point3(-1,  0, 1),
   Point3( 0,  1, 1),
   Point3( 1,  0, 1)
};

float AStar3::_neighboursCost[26] =
{
    /// <summary>
    /// layer -1
    /// </summary>
    DIAGONAL_3_WEIGHT * WEIGHT_DOWN,
    DIAGONAL_3_WEIGHT * WEIGHT_DOWN,
    DIAGONAL_3_WEIGHT * WEIGHT_DOWN,
    DIAGONAL_3_WEIGHT * WEIGHT_DOWN,
    LINEAR_WEIGHT     * WEIGHT_DOWN,
    DIAGONAL_2_WEIGHT * WEIGHT_DOWN,
    DIAGONAL_2_WEIGHT * WEIGHT_DOWN,
    DIAGONAL_2_WEIGHT * WEIGHT_DOWN,
    DIAGONAL_2_WEIGHT * WEIGHT_DOWN,
    /// <summary>
    /// layer 0
    /// </summary>
    DIAGONAL_2_WEIGHT,
    DIAGONAL_2_WEIGHT,
    DIAGONAL_2_WEIGHT,
    DIAGONAL_2_WEIGHT,
    // 0.0f, <- we are here
    LINEAR_WEIGHT,
    LINEAR_WEIGHT,
    LINEAR_WEIGHT,
    LINEAR_WEIGHT,
    /// <summary>
    /// layer +1
    /// </summary>
    DIAGONAL_3_WEIGHT * WEIGHT_UP,
    DIAGONAL_3_WEIGHT * WEIGHT_UP,
    DIAGONAL_3_WEIGHT * WEIGHT_UP,
    DIAGONAL_3_WEIGHT * WEIGHT_UP,
    LINEAR_WEIGHT     * WEIGHT_UP,
    DIAGONAL_2_WEIGHT * WEIGHT_UP,
    DIAGONAL_2_WEIGHT * WEIGHT_UP,
    DIAGONAL_2_WEIGHT * WEIGHT_UP,
    DIAGONAL_2_WEIGHT * WEIGHT_UP
};

bool AStar3::is_valid(Point3& p)const
{
    if (p.row   < 0) return false;
    if (p.col   < 0) return false;
    if (p.layer < 0) return false;
    if (p.row   >= weights().rows())   return false;
    if (p.col   >= weights().cols())   return false;
    if (p.layer >= weights().layers()) return false;
    return true;
}

bool AStar3::point_exists(const Point3& point, const float& cost, Nodes3& _open, Nodes3& _closed)const
{
    std::list<Node3>::iterator _iterator = std::find(_open.begin(), _open.end(), point);

    if (_iterator == _open.end()) return false;

    if ((*_iterator).cost + (*_iterator).dist < cost) return true;

    _open.erase(_iterator);

    return false;
}

bool AStar3::fill_open(const Point3& target, const Node3& current, Nodes3& _open, Nodes3& _closed, Heuristic3d heuristic)
{
    if (current.pos == target)return true;

    float newCost, stepWeight, distance;

    Point3 neighbour;

    for (int index = 0; index < 26; index++)
    {
        neighbour = current.pos + _neighboursPoints[index];

        if (!is_valid(neighbour))continue;

        if (neighbour == target)return true;

        if (std::find(_closed.begin(), _closed.end(), neighbour) != _closed.end())continue;

        if ((stepWeight = weights()[neighbour]) >= MAX_WEIGHT)continue;

        newCost = _neighboursCost[index] * stepWeight + current.cost;

        distance = heuristic(target, neighbour);

        if (point_exists(neighbour, newCost + distance, _open, _closed))continue;

        Node3 new_node;
        new_node.cost   = newCost;
        new_node.dist   = distance;
        new_node.parent = current.pos;
        new_node.pos    = neighbour;

        _open.push_back(new_node);
    }
    return false;
}

Path3d AStar3::build_path(const Point3& start, const Point3& end, Nodes3& closed)
{
    Path3d _path(new std::list<Point3>);

    _path->push_front(end); // <-нужна ли эта точка
    
    // _path_cost = closed.back().cost;
    
    _path->push_front(closed.back().pos);
    
    Point3 parent = closed.back().parent;

   for (std::list<Node3>::reverse_iterator i = closed.rbegin(); i != closed.rend(); i++)
    {   
       if (!((*i).pos == parent))continue;

       if ((*i).pos == start) continue;

       _path->push_front((*i).pos);

       parent = (*i).parent;
    }
    _path->push_front(start); // <-нужна ли эта точка
}

AStar3::AStar3(const int& rows, const int& cols, const int& layers, const float* map)
{
    _map       = new WeightMap3(rows, cols, layers, map);
}

AStar3::~AStar3()
{
   if (_map != nullptr) delete _map;
}

const WeightMap3& AStar3::weights()const
{
    return *_map;
}

Path3d AStar3::searh_path(const Point3& start, const Point3& end, Heuristic3d heuristic)
{
    if (weights()[start] >= MAX_WEIGHT) return nullptr;
    if (weights()[end]   >= MAX_WEIGHT) return nullptr;

    std::list<Node3> _open;
    std::list<Node3> _closed;
    
    Node3 node;
    node.cost   = 0.0f;
    node.dist   = heuristic(end, start);
    node.parent = Point3::MinusOne;
    node.pos    = start;
    
    _open.push_back(node);

    bool success = false;
    int cntr = 0;
    while (true)
    {
        _open.sort();
        _closed.push_back(_open.front()); //тудым...
        _open.pop_front(); //сюдым...
        if (fill_open(end, _closed.back(), _open, _closed, heuristic))
        {
            success = true;
            break;
        };
        if (cntr == weights().ncells()) break;
        if (_open.empty()) break;
        cntr++;
    }
#ifdef _DEBUG
    std::cout << "iters elapsed: " << cntr << ", while cells count is " << weights().ncells()<<'\n';
#endif // DEBUG
    if (!success) return nullptr;// Path2d(new std::list<Point2>()); // <-пустой путь
    return build_path(start, end, _closed);
}

Path3d AStar3::search(const Point3& s, const Point3& e, const int& heuristics)
{
    Point3 _start(s);
    _start.row   = MIN(MAX(0, _start.row), weights().rows() - 1);
    _start.col   = MIN(MAX(0, _start.col), weights().cols() - 1);
    _start.layer = MIN(MAX(0, _start.layer), weights().layers() - 1);

    Point3 _end(e);
    _end.row   = MIN(MAX(0, _end.row), weights().rows() - 1);
    _end.col   = MIN(MAX(0, _end.col), weights().cols() - 1);
    _end.layer = MIN(MAX(0, _end.layer), weights().layers() - 1);
    return searh_path(_start, _end, resolve_heuristics_3d(heuristics));
}

Path3d AStar3::search(const int& heuristics)
{   
    return searh_path({ 0,0,0 }, { weights().rows() - 1, weights().cols() - 1, weights().layers() - 1 }, resolve_heuristics_3d(heuristics));
}


std::ostream& operator <<(std::ostream& stream, const AStar3& a_star)
{
    std::cout << "{\n";
    std::cout << "\"map\"       :\n" << a_star.weights() << "\n}";
    return stream;
}
