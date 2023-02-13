#include "AStar2.h"
#include <cassert>

Point2 AStar2::_neighboursPoints[8] =
{
    Point2(-1, -1),
    Point2( 1, -1),
    Point2(-1,  1),
    Point2( 1,  1),
    Point2( 0, -1),
    Point2(-1,  0),
    Point2( 0,  1),
    Point2( 1,  0) 
};

float AStar2::_neighboursCost[8] =
{
    DIAGONAL_WEIGHT,
    DIAGONAL_WEIGHT,
    DIAGONAL_WEIGHT,
    DIAGONAL_WEIGHT,
    LINEAR_WEIGHT,
    LINEAR_WEIGHT,
    LINEAR_WEIGHT,
    LINEAR_WEIGHT
};

bool AStar2::is_valid(const Point2& p)const
{
    if (p.row < 0) return false;
    if (p.col < 0) return false;
    if (p.row >= weights().rows()) return false;
    if (p.col >= weights().cols()) return false;
    return true;
}

bool AStar2::point_exists(const Point2& point, const float cost, nodes_map& _open, nodes_map& _closed)const
{
    std::unordered_map<int, Node2>::iterator _iterator = _open.find(point.hash());
    if (_iterator == _open.end()) return false;
    if ((*_iterator).second.cost + (*_iterator).second.dist < cost) return true;
    _open.erase(_iterator);
    return false;
}

bool AStar2::fill_open(const Point2& target, const Node2& current, nodes_map& _open, nodes_map& _closed, Heuristic2d heuristic)const
{
    if (current.pos == target) return true;

    float newCost, stepWeight, distance;

    Point2 neighbour;

    int hash;

    for (int index = 0; index < 8; index++)
    {
        neighbour = current.pos + _neighboursPoints[index];

        if (!is_valid(neighbour))continue;

        hash = neighbour.hash();
        if (_closed.find(hash) != _closed.end())continue;

        if ((stepWeight = weights()[neighbour]) >= MAX_WEIGHT)continue;

        newCost =  _neighboursCost[index] * stepWeight + current.cost;

        distance = heuristic(target, neighbour);

        if (point_exists(neighbour, newCost + distance, _open, _closed))continue;

        Node2 new_node;
        new_node.cost   = newCost;
        new_node.dist   = distance;
        new_node.pos    = neighbour;
        new_node.parent = current.pos;
        _open.insert({ hash, new_node });
    } 
    return false;
}

const Path2d& AStar2::build_path(const Point2& start, const Point2& end, nodes_map& closed)
{
   Path2d* _path = new Path2d();
   Node2 current = std::prev(closed.end())->second;
   while (!(current.parent == Point2::MinusOne))
   {
       _path->path.push_front(current.pos);
       current = closed.at(current.parent.hash());
   }
   _path->path.push_front(start);
   
   _paths_cashe.insert({ Point2::hash_points_pair(start, end), _path });
   // 
   // return *_path;
    // Path2d* _path = new Path2d();
    // 
    // _path->path.push_front(end); // <-íóæíà ëè ýòà òî÷êà
    // 
    // Node2 current = std::prev(closed.end())->second;
    // 
    // _path->path.push_front(current.pos);
    // 
    // Point2 parent = current.parent;
    // 
    // nodes_map::iterator iter = closed.end();
    // 
    // while (iter != closed.begin())
    // {
    //     iter--;
    // 
    //     if (!((*iter).second.pos == parent))continue;
    // 
    //     if ((*iter).second.pos == start) continue;
    // 
    //     _path->path.push_front((*iter).second.pos);
    // 
    //     parent = (*iter).second.parent;
    // }
    // _path->path.push_front(start);
    // _paths_cashe.insert({ Point2::hash_points_pair(start, end), _path });
    return *_path;
}

AStar2::AStar2(const int& rows, const int& cols, const float* map)
{
    _map = new WeightMap2(rows, cols, map);
}

AStar2::~AStar2()
{
   if (_map != nullptr) delete _map;
   if (_paths_cashe.size() == 0)return;
   for(auto& pair : _paths_cashe) delete pair.second;
}

const WeightMap2& AStar2::weights()const
{
    return *_map;
}

const Path2d& AStar2::searh_path(const Point2& start, const Point2& end, Heuristic2d heuristic)
{
    if (weights()[start] >= MAX_WEIGHT) return _empty_path;
    if (weights()[end]   >= MAX_WEIGHT) return _empty_path;

    Points2dPairHash p1p2_hash = Point2::hash_points_pair(start, end);
    std::unordered_map<Points2dPairHash, Path2d*>::iterator _iterator;
    if ((_iterator = _paths_cashe.find(p1p2_hash)) != _paths_cashe.end()) return *(*_iterator).second;

    nodes_map _open;
    nodes_map _clsd;

    bool  _success = false;
    int   _hash  = start.hash();
    int   _cntr  = 0;
    Node2 _node;
    _node.cost   = 0.0f;
    _node.pos    = start;
    _node.parent = Point2::MinusOne;
    _node.dist   = heuristic(end, start);
    _open.insert({ _hash, _node }); // emplace(_hash, _node);
    nodes_map::iterator it;
    
    while (true)
    {
        _node = _open.begin()->second;
        for (it = _open.begin(); it != _open.end(); it++) if ((*it).second < _node) _node = (*it).second; // поиск минимального
        _hash = _node.pos.hash(); // ключ по которому добавляем 
        _clsd.insert({ _hash, _node }); //тудым...
        _open.erase  (_hash); //сюдым...
        if (fill_open(end, _node, _open, _clsd, heuristic))
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
    if (!_success) return _empty_path;
    return build_path(start, end, _clsd);
}

const Path2d& AStar2::search(const Point2& s, const Point2& e, const int& heuristics)
{
    Point2 _start(s);
    _start.row = MIN(MAX(0, _start.row), weights().rows() - 1);
    _start.col = MIN(MAX(0, _start.col), weights().cols() - 1);

    Point2 _end(e);
    _end.row = MIN(MAX(0, _end.row), weights().rows() - 1);
    _end.col = MIN(MAX(0, _end.col), weights().cols() - 1);
    return searh_path(_start, _end, resolve_heuristics_2d(heuristics));
}

const Path2d& AStar2::search(const int& heuristics)
{   
    return searh_path({ 0,0 }, { short(weights().rows() - 1), short(weights().cols() - 1) }, resolve_heuristics_2d(heuristics));
    // return searh_path({ short(weights().rows() - 1), short(weights().cols() - 1) }, { 0,0 }, resolve_heuristic_2d(heuristics));

}

std::ostream& operator <<(std::ostream& stream, const AStar2& a_star)
{
#ifdef _DEBUG
    /// <summary>
    /// Shows map and path if exists
    /// </summary>

    std::string _str_map;
    int n_chars = a_star.weights().rows() * (a_star.weights().cols() + 1);

    char* char_map = (char*)malloc(n_chars + 1);

    char_map[n_chars] = '\0';

    for (int index = 0; index < n_chars; index++)
    {
        if (index % (a_star.weights().cols() + 1) == a_star.weights().cols())
        {
            char_map[index] = '\n';
            continue;
        }
        char_map[index] = (a_star.weights()(index / (a_star.weights().cols() + 1), index % (a_star.weights().cols() + 1)) >= MAX_WEIGHT ? '#' : '_');
    }
    for (const auto& p : a_star._paths_cashe)
    {
        for (const auto& pt : p.second->path) char_map[pt.row * (a_star.weights().cols() + 1) + pt.col] = '.';
    }
    std::cout << char_map;

    free(char_map);
#else
    std::cout << "{\n";
    std::cout << "\"map\"       :\n" << a_star.weights() << "\n}";
#endif
    return stream;
}
