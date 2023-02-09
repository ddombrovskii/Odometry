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

bool AStar3::point_exists(const Point3& point, const float& cost, std::list<Node3>& _open, std::list<Node3>& _closed)const
{
    std::list<Node3>::iterator _iterator = std::find(_open.begin(), _open.end(), point);

    if (_iterator == _open.end()) return false;

    if ((*_iterator).cost + (*_iterator).dist < cost) return true;

    _open.erase(_iterator);

    return false;
}

bool AStar3::fill_open(Node3& node, std::list<Node3>& _open, std::list<Node3>& _closed)
{
    if (node.pos == _end)return true;

    float newCost, stepWeight, distance;

    Point3 neighbour;

    for (int index = 0; index < 26; index++)
    {
        neighbour = node.pos + _neighboursPoints[index];

        if (!is_valid(neighbour))continue;

        if (neighbour == _end)return true; 

        if (std::find(_closed.begin(), _closed.end(), neighbour) != _closed.end())continue;

        if ((stepWeight = weights()[neighbour]) >= MAX_WEIGHT)continue;

        newCost = _neighboursCost[index] * stepWeight + node.cost;

        distance = (_end.manhattan_distance(neighbour));

        if (point_exists(neighbour, newCost + distance, _open, _closed))continue;

        Node3 new_node;
        new_node.cost   = newCost;
        new_node.dist   = distance;
        new_node.parent = node.pos;
        new_node.pos    = neighbour;

        _open.push_back(new_node);
    }
    return false;
}

void AStar3::build_path(std::list<Node3>& closed)
{
    _path.push_front(_end); // <-нужна ли эта точка
    
    _path_cost = closed.back().cost;
    
    _path.push_front(closed.back().pos);
    
    Point3 parent = closed.back().parent;

   for (std::list<Node3>::reverse_iterator i = closed.rbegin(); i != closed.rend(); i++)
    {   
       if (!((*i).pos == parent))continue;

       if ((*i).pos == start()) continue;

       _path.push_front((*i).pos);

       parent = (*i).parent;
    }
    _path.push_front(_start); // <-нужна ли эта точка
}

AStar3::AStar3(const int& rows, const int& cols, const int& layers, const float* map)
{
    _map       = new WeightMap3(rows, cols, layers, map);
    _path_cost = 1e12f;
    _start     = Point3::MinusOne;
    _end       = Point3::MinusOne;
}

const Point3& AStar3::end()const
{
    return _end;
}

const Point3& AStar3::start()const
{
    return _start;
}

void AStar3::set_end(const Point3& pt)
{   
    if (_end == pt)return;
    _end = pt;
    _end.row   = MIN(MAX(0, _end.row),   weights().rows  () - 1);
    _end.col   = MIN(MAX(0, _end.col),   weights().cols  () - 1);
    _end.layer = MIN(MAX(0, _end.layer), weights().layers() - 1);
    _path_cost = 1e32f;
    _path.clear();
}

void AStar3::set_start(const Point3& pt) 
{
    if (_start == pt)return;
    _start = pt;
    _start.row   = MIN(MAX(0, _start.row),   weights().rows  () - 1);
    _start.col   = MIN(MAX(0, _start.col),   weights().cols  () - 1);
    _start.layer = MIN(MAX(0, _start.layer), weights().layers() - 1);
    _path_cost = 1e32f;
    _path.clear();
}

AStar3::~AStar3()
{
   if (_map != nullptr) delete _map;
}

const WeightMap3& AStar3::weights()const
{
    return *_map;
}

bool AStar3::searh_path()
{
    if (weights()[start()] >= MAX_WEIGHT) return false;
    if (weights()[end()]   >= MAX_WEIGHT) return false;

    std::list<Node3> _open;
    std::list<Node3> _closed;
    
    Node3 node;
    node.cost   = 1.0f;
    node.dist   = (float)end().manhattan_distance(start());
    node.parent = Point3::MinusOne;
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

bool AStar3::search(const Point3& s, const Point3& e)
{
    set_end  (e);
    set_start(s);
    return searh_path();
}

bool AStar3::search() 
{   
    if (start() == Point3::MinusOne) set_start({ 0,0,0 });
    if (end()   == Point3::MinusOne) set_end({ weights().rows() - 1, weights().cols() - 1, weights().layers() - 1 });
    return searh_path();
}

const std::list<Point3>& AStar3::path()const 
{
    return _path;
}

float AStar3::path_cost()const
{
    return _path_cost;
}

std::ostream& operator <<(std::ostream& stream, const AStar3& a_star)
{
#ifdef _DEBUG
    /// <summary>
    /// Shows map and path if exists
    /// </summary>
    std::string _str_map;
    
    char* char_map = (char*)malloc(a_star.weights().ncells() * sizeof(char) + 1);

    char_map[a_star.weights().ncells()] = '\0';

    for (int index = 0; index < a_star.weights().ncells(); index++) char_map[index] = (a_star.weights()[index] >= MAX_WEIGHT ? '#' : '_');
    
    if (a_star.path().size() != 0)for (const auto& pt : a_star.path()) char_map[(pt.layer * a_star.weights().rows() + pt.row) * a_star.weights().cols() + pt.col] = '.';

    char_map[(a_star.start().layer * a_star.weights().rows() + a_star.start().row) * a_star.weights().cols() + a_star.start().col] = '+';
    char_map[(a_star.end().  layer * a_star.weights().rows() + a_star.end().  row) * a_star.weights().cols() + a_star.end().  col] = '+';
    int layer = 0;
    for (int index = 0; index < a_star.weights().ncells(); index++)
    {
        std::cout << char_map[index];
        if (index % a_star.weights().cols() == a_star.weights().cols() - 1)std::cout << "\n";
        if (index % (a_star.weights().cols() * a_star.weights().rows()) == 0)std::cout << "\nlayer : " << (layer++) << "\n";
    }
    free(char_map);
#else
    std::cout << "{\n";
    std::cout << "\"map\"       :\n"<< a_star.weights() << ",\n";
    std::cout << "\"path_cost\" : " << a_star.path_cost() << ",\n";
    std::cout << "\"path\"      : [\n";
    const std::list<Point3>& path = a_star.path();
    int index = 1;
    for (const Point3& p : path)
    {
        std::cout << p << (index != path.size() ? ",\n" : "");
        index++;
    }
    std::cout <<"]\n}}";
#endif
    return stream;
}
