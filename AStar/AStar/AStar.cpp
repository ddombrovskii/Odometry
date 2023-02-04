#include "AStar.h"
#include <cassert>

Point AStar::neighboursPoints[8] =
{
    Point(-1, -1),
    Point( 1, -1),
    Point(-1,  1),
    Point( 1,  1),
    Point( 0, -1),
    Point(-1,  0),
    Point( 0,  1),
    Point( 1,  0) 
};

bool AStar::is_valid(Point& p)const
{
    if (p.row < 0) return false;
    if (p.col < 0) return false;
    if (p.row >= weights().rows()) return false;
    if (p.col >= weights().cols()) return false;
    return true;
}

bool AStar::point_exists(const Point& point, const float cost, std::list<Node>& _open, std::list<Node>& _closed)const
{
    std::list<Node>::iterator _iterator = std::find(_open.begin(), _open.end(), point);

    if (_iterator == _open.end()) return false;

    if ((*_iterator).cost + (*_iterator).dist < cost) return true;

    _open.erase(_iterator);

    return false;
}

bool AStar::fill_open(Node& node, std::list<Node>& _open, std::list<Node>& _closed)
{
    if (node.pos == _end)return true;

    float newCost, stepWeight, distance;

    Point neighbour;

    for (int index = 0; index < 8; index++)
    {
        neighbour = node.pos + neighboursPoints[index];

        if (!is_valid(neighbour))continue;

        if (neighbour == _end)return true; 

        if (std::find(_closed.begin(), _closed.end(), neighbour) != _closed.end())continue;

        if ((stepWeight = weights()[neighbour]) >= MAX_WEIGHT)continue;

        newCost = ((index < 4) ? DIAGONAL_WEIGHT * stepWeight : LINEAR_WEIGHT * stepWeight) + node.cost;

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

void AStar::build_path(std::list<Node>& closed)
{
    _path.push_front(_end); // <-нужна ли эта точка
    
    _path_cost = closed.back().cost;
    
    _path.push_front(closed.back().pos);
    
    Point parent = closed.back().parent;

   for (std::list<Node>::reverse_iterator i = closed.rbegin(); i != closed.rend(); i++)
    {   
       if (!((*i).pos == parent))continue;

       if ((*i).pos == start()) continue;

       _path.push_front((*i).pos);

       parent = (*i).parent;
    }
    _path.push_front(_start); // <-нужна ли эта точка
}

AStar::AStar(const int rows, const int cols, const float* map)
{
    _map       = new WeightMap(rows, cols, map);
    _path_cost = 1e12f;
    _start     = Point::MinusOne;
    _end       = Point::MinusOne;
}

const Point& AStar::end()const
{
    return _end;
}

const Point& AStar::start()const
{
    return _start;
}

void AStar::set_end(const Point& pt)
{   
    if (_end == pt)return;
    _end = pt;
    _end.row = MIN(MAX(0, _end.row), weights().rows() - 1);
    _end.col = MIN(MAX(0, _end.col), weights().cols() - 1);
    _path_cost = 1e32f;
    _path.clear();
}

void AStar::set_start(const Point& pt) 
{
    if (_start == pt)return;
    _start = pt;
    _start.row = MIN(MAX(0, _start.row), weights().rows() - 1);
    _start.col = MIN(MAX(0, _start.col), weights().cols() - 1);
    _path_cost = 1e32f;
    _path.clear();
}

AStar::~AStar()
{
   if (_map != nullptr) delete _map;
}

const WeightMap& AStar::weights()const
{
    return *_map;
}

bool AStar::searh_path()
{
    if (weights()[start()] >= MAX_WEIGHT) return false;
    if (weights()[end()]   >= MAX_WEIGHT) return false;

    std::list<Node> _open;
    std::list<Node> _closed;
    
    Node node;
    node.cost   = 1.0f;
    node.dist   = (float)end().manhattan_distance(start());
    node.parent = Point::MinusOne;
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

bool AStar::search(const Point& s, const Point& e)
{
    set_end  (e);
    set_start(s);
    return searh_path();
}

bool AStar::search() 
{   
    if (start() == Point::MinusOne) set_start({ 0,0 });
    if (end()   == Point::MinusOne) set_end({ weights().rows() - 1, weights().cols() - 1 });
    return searh_path();
}

const std::list<Point>& AStar::path()const 
{
    return _path;
}

float AStar::path_cost()const
{
    return _path_cost;
}

std::ostream& operator <<(std::ostream& stream, const AStar& a_star)
{
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
    return stream;
}
