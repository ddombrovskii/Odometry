#include "Point2.h"

const Point2 Point2::Zero     = Point2(0, 0);
const Point2 Point2::MinusOne = Point2(-1,-1);

Point2::Point2(int _row, int _col)
{
    row = _row;
    col = _col;
}

Point2::Point2(const Point2& original)
{
    row = original.row;
    col = original.col;
}


Point2& Point2::operator = (const Point2& point)
{
    row = point.row;
    col = point.col;
    return *this;
}

bool Point2::operator ==(const Point2& point)const
{
    if (point.row != row) return false;
    if (point.col != col) return false;
    return true;
}

Point2 Point2::operator+(const Point2& o)const
{ 
    return Point2(o.row + row, o.col + col); 
}

Point2 Point2::operator-(const Point2& o)const
{
    return Point2(o.row - row, o.col - col);
}

int Point2::manhattan_distance(const Point2& o)const 
{
    return (abs(o.row - row) + abs(o.col - col));
}

int Point2::magnitude_sqr()const
{
    return row * row + col * col;
}

int Point2::distance_sqr(const Point2& o)const
{
    return (o - (*this)).magnitude_sqr();
}

float Point2::magnitude_sqrf()const
{
    return (float)(magnitude_sqr());
}

float Point2::distance_sqrf(const Point2& o)const
{
    return (float)distance_sqr(o);
}

std::ostream& operator<<(std::ostream& stream, const Point2& point)
{
    stream << "{\"row\": " << point.row << ", \"col\": " << point.col << "}";
    return stream;
}

