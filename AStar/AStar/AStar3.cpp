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
 

bool AStar3::fill_open(const Point3& start, const Point3& target, const Node3& current, nodes_map_3d& _open, nodes_map_3d& _closed, Heuristic3d heuristic)const
{
    if (current.pos == target)return true;
    int    hash;
    float  stepCost;
    float  stepWeight;
    Point3 neighbour;
    nodes_map_3d::iterator _iterator;

    for (int index = 0; index < 26; index++)
    {
        neighbour = current.pos + _neighboursPoints[index];

        if (!is_valid(neighbour))continue;

        if (_closed.find(hash) != _closed.end())continue;

        if ((stepWeight = weights()[neighbour]) >= MAX_WEIGHT)continue;

        stepCost = _neighboursCost[index] * stepWeight + current.cost;

        Node3 new_node;
        new_node.cost = stepCost;
        new_node.dist = heuristic(target, neighbour);// +abs(Point2::cross(neighbour - target, start - target)) * 0.001f;
        new_node.pos = neighbour;
        new_node.parent = current.pos;

        if ((_iterator = _open.find(hash)) == _open.end())
        {
            _open.emplace(hash, new_node);
            continue;
        }
        if ((*_iterator).second.cost < stepCost) { continue; }
        _open[hash] = new_node;
        _open.insert({ hash, new_node });
    }
    return false;
}

const Path3d& AStar3::build_path(const Point3& start, const Point3& end, nodes_map_3d& closed)
{
    Path3d* _path = new Path3d();
    Node3 current = closed.at(end.hash());

    while (!(current.parent == Point3::MinusOne))
    {
        _path->path.insert(_path->path.begin(), current.pos);
        current = closed.at(current.parent.hash());
    }
    _path->path.insert(_path->path.begin(), start);

    _paths_cashe.insert({ Point3::hash_points_pair(start, end), _path });

    return *_path;
}

AStar3::AStar3(const int& rows, const int& cols, const int& layers, const float* map)
{
    _map = new WeightMap3(rows, cols, layers, map);
}

AStar3::~AStar3()
{
   if (_map != nullptr) delete _map;
   if (_paths_cashe.size() == 0)return;
   for (auto& pair : _paths_cashe) delete pair.second;

}

const WeightMap3& AStar3::weights()const
{
    return *_map;
}

const Path3d& AStar3::searh_path(const Point3& start, const Point3& end, Heuristic3d heuristic)
{
    if (weights()[start] >= MAX_WEIGHT) return _empty_path;
    if (weights()[end]   >= MAX_WEIGHT) return _empty_path;

    nodes_map_3d _open;
    nodes_map_3d _clsd;
    
    bool  _success = false;
    int   _hash = start.hash();
    int   _cntr = 0;
    Node3 _node;
    _node.cost = 0.0f;
    _node.pos = start;
    _node.parent = Point3::MinusOne;
    _node.dist = heuristic(end, start);
    _open.emplace( _hash, _node);
    nodes_map_3d::iterator it;

    while (true)
    {
        _node = _open.begin()->second;
        for (it = _open.begin(); it != _open.end(); it++) if ((*it).second <= _node) _node = (*it).second; // поиск минимального
        _hash = _node.pos.hash(); // ключ по которому добавляем 
        _open.erase(_hash); //сюдым...
        _clsd.emplace( _hash, _node); //тудым...
        if (fill_open(start, end, _node, _open, _clsd, heuristic))
        {
            _success = true;
            break;
        };
        if (_cntr == weights().ncells()) break;
        if (_open.empty()) break;
        _cntr++;
    }
#ifdef _DEBUG
    std::cout << "iters elapsed: " << _cntr << ", while cells count is " << weights().ncells()<<'\n';
#endif // DEBUG
    if (!_success) return _empty_path;// Path2d(new std::list<Point2>()); // <-пустой путь
    return build_path(start, end, _clsd);
}

const Path3d& AStar3::search(const Point3& s, const Point3& e, const int& heuristics)
{
    Point3 _start(s);
    _start.row   = MIN(MAX(0, _start.row), weights().rows() - 1);
    _start.col   = MIN(MAX(0, _start.col), weights().cols() - 1);
    _start.layer = MIN(MAX(0, _start.layer), weights().layers() - 1);

    Point3 _end(e);
    _end.row   = MIN(MAX(0, _end.row), weights().rows() - 1);
    _end.col   = MIN(MAX(0, _end.col), weights().cols() - 1);
    _end.layer = MIN(MAX(0, _end.layer), weights().layers() - 1);
    return searh_path(_start, _end, resolve_heuristic_3d(heuristics));
}

const Path3d& AStar3::search(const int& heuristics)
{   
    return searh_path({ 0,0,0 }, { weights().rows() - 1, weights().cols() - 1, weights().layers() - 1 }, resolve_heuristic_3d(heuristics));
}

std::ostream& operator <<(std::ostream& stream, const AStar3& a_star)
{
    std::cout << "{\n";
    std::cout << "\"map\"       :\n" << a_star.weights() << "\n}";
    return stream;
}
