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

bool AStar2::fill_open(Node& node, std::list<Node>& _open, std::list<Node>& _closed)
{
    if (node.pos == _end)return true;

    float newCost, stepWeight, distance;

    Point2 neighbour;

    for (int index = 0; index < 8; index++)
    {
        neighbour = node.pos + _neighboursPoints[index];

        if (!is_valid(neighbour))continue;

        if (neighbour == _end)return true; 

        if (std::find(_closed.begin(), _closed.end(), neighbour) != _closed.end())continue;

        if ((stepWeight = weights()[neighbour]) >= MAX_WEIGHT)continue;

        newCost = _neighboursCost[index] * stepWeight + node.cost;

        distance = (_end.manhattan_distance(neighbour));

        if (point_exists(neighbour, newCost + distance, _open, _closed))continue;

        Node new_node; 
        new_node.cost   = newCost;
        new_node.dist   = distance;
        new_node.parent = node.pos;
        new_node.pos    = neighbour;

        _open.push_back(new_node);
    }
    return false;
}

void AStar2::build_path(std::list<Node>& closed)
{
    _path.push_front(_end); // <-нужна ли эта точка
    
    _path_cost = closed.back().cost;
    
    _path.push_front(closed.back().pos);
    
    Point2 parent = closed.back().parent;

   for (std::list<Node>::reverse_iterator i = closed.rbegin(); i != closed.rend(); i++)
    {   
       if (!((*i).pos == parent))continue;

       if ((*i).pos == start()) continue;

       _path.push_front((*i).pos);

       parent = (*i).parent;
    }
    _path.push_front(_start); // <-нужна ли эта точка
}

AStar2::AStar2(const int& rows, const int& cols, const float* map)
{
    _map       = new WeightMap2(rows, cols, map);
    _path_cost = 1e12f;
    _start     = Point2::MinusOne;
    _end       = Point2::MinusOne;
}

const Point2& AStar2::end()const
{
    return _end;
}

const Point2& AStar2::start()const
{
    return _start;
}

void AStar2::set_end(const Point2& pt)
{   
    if (_end == pt)return;
    _end = pt;
    _end.row = MIN(MAX(0, _end.row), weights().rows() - 1);
    _end.col = MIN(MAX(0, _end.col), weights().cols() - 1);
    _path_cost = 1e32f;
    _path.clear();
}

void AStar2::set_start(const Point2& pt) 
{
    if (_start == pt)return;
    _start = pt;
    _start.row = MIN(MAX(0, _start.row), weights().rows() - 1);
    _start.col = MIN(MAX(0, _start.col), weights().cols() - 1);
    _path_cost = 1e32f;
    _path.clear();
}

AStar2::~AStar2()
{
   if (_map != nullptr) delete _map;
}

const WeightMap2& AStar2::weights()const
{
    return *_map;
}

bool AStar2::searh_path()
{
    if (weights()[start()] >= MAX_WEIGHT) return false;
    if (weights()[end()]   >= MAX_WEIGHT) return false;

    std::list<Node> _open;
    std::list<Node> _closed;
    
    Node node;
    node.cost   = 1.0f;
    node.dist   = (float)end().manhattan_distance(start());
    node.parent = Point2::MinusOne;
    node.pos    = start();
    
    _open.push_back(node);

    bool success = false;
    int cntr = 0;
    while (true)
    {
        _open.sort();
        _closed.push_back(_open.front()); //тудым...
        _open.pop_front(); //сюдым...
        if (fill_open(_closed.back(), _open, _closed))
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

    if (success)
    {
        build_path(_closed);
    }
    return success;
}

bool AStar2::search(const Point2& s, const Point2& e)
{
    set_end  (e);
    set_start(s);
    return searh_path();
}

bool AStar2::search() 
{   
    if (start() == Point2::MinusOne) set_start({ 0,0 });
    if (end()   == Point2::MinusOne) set_end({ weights().rows() - 1, weights().cols() - 1 });
    return searh_path();
}

const std::list<Point2>& AStar2::path()const 
{
    return _path;
}

float AStar2::path_cost()const
{
    return _path_cost;
}

std::ostream& operator <<(std::ostream& stream, const AStar2& a_star)
{
#ifdef _DEBUG
    /// <summary>
    /// Shows map and path if exists
    /// </summary>

    std::string _str_map;
    
    char* char_map = (char*)malloc(a_star.weights().ncells() * sizeof(char) + 1);

    char_map[a_star.weights().ncells()] = '\0';

    for (int index = 0; index < a_star.weights().ncells(); index++) char_map[index] = (a_star.weights()[index] >= MAX_WEIGHT ? '#' : '_');
    
    if (a_star.path().size() != 0)for (const auto& pt : a_star.path()) char_map[pt.row * a_star.weights().cols() + pt.col] = '.';

    char_map[a_star.start().row * a_star.weights().cols() + a_star.start().col] = '+';
    char_map[a_star.end().row * a_star.weights().cols() + a_star.end().col] = '+';

    for (int index = 0; index < a_star.weights().ncells(); index++)
    {
        std::cout << char_map[index];
        if (index % a_star.weights().cols() == a_star.weights().cols() - 1)std::cout << "\n";
    }
    free(char_map);
#else
    std::cout << "{\n";
    std::cout << "\"map\"       :\n"<< a_star.weights() << ",\n";
    std::cout << "\"path_cost\" : " << a_star.path_cost() << ",\n";
    std::cout << "\"path\"      : [\n";
    const std::list<Point2>& path = a_star.path();
    int index = 1;
    for (const Point2& p : path)
    {
        std::cout << p << (index != path.size() ? ",\n" : "");
        index++;
    }
    std::cout <<"]\n}}";
#endif
    return stream;
}
