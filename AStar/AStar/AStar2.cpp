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

bool AStar2::is_valid(Point2& p)const
{
    if (p.row < 0) return false;
    if (p.col < 0) return false;
    if (p.row >= weights().rows()) return false;
    if (p.col >= weights().cols()) return false;
    return true;
}

bool AStar2::point_exists(const Point2& point, const float cost, std::list<Node>& _open, std::list<Node>& _closed)const
{
    std::list<Node>::iterator _iterator = std::find(_open.begin(), _open.end(), point);

    if (_iterator == _open.end()) return false;

    if ((*_iterator).cost + (*_iterator).dist < cost) return true;

    _open.erase(_iterator);

    return false;
}

bool AStar2::fill_open(const Point2& target, const Node& current, std::list<Node>& _open, std::list<Node>& _closed, Heuristic2d heuristic)
{
    if (current.pos == target)return true;

    float newCost, stepWeight, distance;

    Point2 neighbour;

    for (int index = 0; index < 8; index++)
    {
        neighbour = current.pos + _neighboursPoints[index];

        if (!is_valid(neighbour))continue;

        if (neighbour == target)return true;

        if (std::find(_closed.begin(), _closed.end(), neighbour) != _closed.end())continue;

        if ((stepWeight = weights()[neighbour]) >= MAX_WEIGHT)continue;

        newCost = _neighboursCost[index] * stepWeight + current.cost;

        distance = heuristic(target, neighbour); 

        if (point_exists(neighbour, newCost + distance, _open, _closed))continue;

        Node new_node; 
        new_node.cost   = newCost;
        new_node.dist   = distance;
        new_node.parent = current.pos;
        new_node.pos    = neighbour;

        _open.push_back(new_node);
    }
    return false;
}

Path2d AStar2::build_path(const Point2& start, const Point2& end, std::list<Node>& closed)
{
    Path2d _path(new std::list<Point2>);

    _path->push_front(end); // <-нужна ли эта точка
    
    _path->push_front(closed.back().pos);
    
    Point2 parent = closed.back().parent;

   for (std::list<Node>::reverse_iterator i = closed.rbegin(); i != closed.rend(); i++)
    {   
       if (!((*i).pos == parent))continue;

       if ((*i).pos == start) continue;

       _path->push_front((*i).pos);

       parent = (*i).parent;
    }
   _path->push_front(start); // <-нужна ли эта точка
  
   return _path;
}

AStar2::AStar2(const int& rows, const int& cols, const float* map)
{
    _map = new WeightMap2(rows, cols, map);
}

AStar2::~AStar2()
{
   if (_map != nullptr) delete _map;
}

const WeightMap2& AStar2::weights()const
{
    return *_map;
}

Path2d AStar2::searh_path(const Point2& start, const Point2& end, Heuristic2d heuristic)
{
    if (weights()[start] >= MAX_WEIGHT) return nullptr;
    if (weights()[end]   >= MAX_WEIGHT) return nullptr;

    std::list<Node> _open;
    std::list<Node> _closed;
    
    Node node;
    node.cost   = 1.0f;
    node.dist   = heuristic(end, start); // (float)end().manhattan_distance(start());
    node.parent = Point2::MinusOne;
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

Path2d AStar2::search(const Point2& s, const Point2& e, const int& heuristics)
{
    Point2 _start(s);
    _start.row = MIN(MAX(0, _start.row), weights().rows() - 1);
    _start.col = MIN(MAX(0, _start.col), weights().cols() - 1);

    Point2 _end(e);
    _end.row = MIN(MAX(0, _end.row), weights().rows() - 1);
    _end.col = MIN(MAX(0, _end.col), weights().cols() - 1);
    return searh_path(_start, _end, resolve_heuristics_2d(heuristics));
}

Path2d AStar2::search(const int& heuristics)
{   
    return searh_path({ 0,0 }, { weights().rows() - 1, weights().cols() - 1 }, resolve_heuristics_2d(heuristics));
}

std::ostream& operator <<(std::ostream& stream, const AStar2& a_star)
{
    std::cout << "{\n";
    std::cout << "\"map\"       :\n" << a_star.weights() << "\n}";
    return stream;
}
