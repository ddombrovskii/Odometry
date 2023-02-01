#include "Point.h"

Point::Point(int _row, int _col)
{
    row = _row;
    col = _col;
}

Point& Point::operator = (const Point& point)
{
    row = point.row;
    col = point.col;
    return *this;
}

bool Point::operator ==(const Point& point)const
{
    if (point.row != row) return false;
    if (point.col != col) return false;
    return true;
}

Point Point::operator+(const Point& o)const
{ 
    return Point(o.row + row, o.col + col); 
}

Point Point::operator-(const Point& o)const
{
    return Point(o.row - row, o.col - col);
}

int Point::manhattan_distance(const Point& o)const 
{
    return abs(o.row - row) + abs(o.col - col);
}

int Point::magnitude_sqr()const
{
    return row * row + col * col;
}

int Point::distance_sqr(const Point& o)const
{
    return (o - (*this)).magnitude_sqr();
}

float Point::magnitude_sqrf()const
{
    return (float)(magnitude_sqr());
}

float Point::distance_sqrf(const Point& o)const
{
    return (float)distance_sqr(o);
}

std::ostream& operator<<(std::ostream& stream, const Point& point)
{
    stream << "{\"row\": " << point.row << ", \"col\": " << point.col << "}";
    return stream;
}

