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
    std::list<Node>::iterator i;

   /* i = std::find(_closed.begin(), _closed.end(), point);
    if (i != _closed.end())
    {
        if ((*i).cost + (*i).dist < cost)
        {
            return true;
        }
        _closed.erase(i);
        return false;
    }*/
    
    i = std::find(_open.begin(), _open.end(), point);
    if (i != _open.end())
    {
        if ((*i).cost + (*i).dist < cost)
        {
            return true;
        }
        _open.erase(i);
        return false;
    }
    return false;
}

bool AStar::fill_open(Node& _node, std::list<Node>& _open, std::list<Node>& _closed)
{
    if (_node.pos == _end)return true;

    float stepWeight, /*stepCost,*/ newCost, dist;
    
    Point neighbour;

    for (int index = 0; index < 8; index++)
    {
        neighbour = _node.pos + neighboursPoints[index];

        if (!is_valid(neighbour))continue;
         
        //if(stepWeight = weights()(neighbour.row, neighbour.col) >= MAX_WEIGHT)continue;

        //  stepCost = index < 4? 1.414f: 1.0f; 
       
        newCost = (index < 4 ? 1.414f : 1.0f) * weights()(neighbour.row, neighbour.col) + _node.cost;
        
        dist =  _end.manhattan_distance(neighbour);// *stepWeight;
        
        if (point_exists(neighbour, (newCost + dist), _open, _closed))continue;

        _open.push_back({ neighbour, _node.pos, dist, newCost });

    }
    return false;
}

void AStar::build_path(std::list<Node>& closed)
{
    _path.push_front(_end);
    _path_cost = 1.0f + closed.back().cost;
    _path.push_front(closed.back().pos);
    Point parent = closed.back().parent;

    for (std::list<Node>::reverse_iterator i = closed.rbegin(); i != closed.rend(); i++)
    {
        if (!((*i).pos == parent)) continue;
        if ((*i).pos == _start) continue;

        _path.push_front((*i).pos);
        parent = (*i).parent;
    }
    _path.push_front(_start);
}

AStar::AStar(const int rows, const int cols, const float* map)
{
    _map           = new WeightMap(rows, cols, map);
    _path_cost     = 1e12f;
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
    _end = pt;
    _end.row = MIN(MAX(0, _end.row), weights().rows() - 1);
    _end.col = MIN(MAX(0, _end.col), weights().cols() - 1);
    _path_cost = 1e32f;
    _path.clear();
}

void AStar::set_start(const Point& pt) 
{
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

bool AStar::search(const Point& s, const Point& e)
{
    set_end  (e);
    set_start(s);

    std::list<Node> _open;
    std::list<Node> _closed;

    _open.push_back({ start(), Point(-1, -1), (float)end().manhattan_distance(start()), 0.0f});

    bool success = false;

    while (!_open.empty())
    {
        Node n = _open.front();
        _open.  pop_front();
        _closed.push_back(n);
        if (fill_open(n, _open, _closed))
        {
            success = true;
            break;
        };
    }
    if (success)
    {
        build_path(_closed);
    }
    return success;
}

bool AStar::search() 
{
    return search(Point(0, 0), Point(weights().rows() - 1, weights().cols() - 1));
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

    for (int index = 0; index < a_star.weights().ncells(); index++)
    {
        char_map[index] = (a_star.weights()[index] > 1.0f ? '#' : '_');
    }
    
    if (a_star.path().size() != 0)
        for (const auto& pt : a_star.path()) 
        {
            char_map[pt.row * a_star.weights().cols() + pt.col] = '.';
        }

    char_map[a_star.start().row * a_star.weights().cols() + a_star.start().col] = '+';
    char_map[a_star.end().row * a_star.weights().cols() + a_star.end().col] = '+';


    for (int index = 0; index < a_star.weights().ncells(); index++)
    {
        std::cout << char_map[index];
        if (index % a_star.weights().cols() == a_star.weights().cols() - 1)
        {
            std::cout << "\n";
        }
    }
    free(char_map);
    return stream;
}
