#include "Point3.h"

const Point3 Point3::Zero     = Point3( 0, 0, 0);
const Point3 Point3::MinusOne = Point3(-1,-1,-1);

Point3::Point3(int _row, int _col, int _layer)
{
    row   = _row;
    col   = _col;
	layer = _layer;
}

Point3& Point3::operator = (const Point3& point)
{
    row   = point.row;
    col   = point.col;
	layer = point.layer;
	return *this;
}

bool Point3::operator ==(const Point3& point)const
{
    if (point.row   != row)   return false;
    if (point.col   != col)   return false;
	if (point.layer != layer) return false;
    return true;
}

Point3 Point3::operator+(const Point3& o)const
{ 
    return Point3(o.row + row, o.col + col, o.layer + layer); 
}

Point3 Point3::operator-(const Point3& o)const
{
    return Point3(o.row - row, o.col - col, o.layer - layer);
}

int Point3::manhattan_distance(const Point3& o)const 
{
    return (abs(o.row - row) + abs(o.col - col) + abs(o.layer - layer));
}

int Point3::magnitude_sqr()const
{
    return row * row + col * col + layer * layer;
}

int Point3::distance_sqr(const Point3& o)const
{
    return (o - (*this)).magnitude_sqr();
}

float Point3::magnitude_sqrf()const
{
    return (float)(magnitude_sqr());
}

float Point3::distance_sqrf(const Point3& o)const
{
    return (float)distance_sqr(o);
}

std::ostream& operator<<(std::ostream& stream, const Point3& point)
{
    stream << "{\"row\": " << point.row << ", \"col\": " << point.col <<", \"layer\": " << point.layer << "}";
    return stream;
}

