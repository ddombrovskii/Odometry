#include "Point2.h"

const Point2 Point2::Zero     = Point2(0, 0);
const Point2 Point2::MinusOne = Point2(-1,-1);

Point2 Point2::unhash(const int& hash)
{
    return Point2(hash & 0x0000ffff, (hash >> 16) & 0x0000ffff);
}
int Point2::cross(const Point2& p1, const Point2& p2)
{
    return p1.row * p2.col - p2.row * p1.col;
}

Points2dPairHash Point2::hash_points_pair(const Point2& p1, const Point2& p2)
{
    return (((Points2dPairHash)p1.hash() << 32) | (Points2dPairHash)p2.hash());
}

void Point2::unhash_points_pair(const Points2dPairHash& pair_hash, Point2& p1, Point2& p2)
{
    p1 = unhash((pair_hash >> 32) & MASK_X_64);
    p2 = unhash(pair_hash & MASK_X_64);
}

Point2::Point2(I16 _row, I16 _col)
{
    row = _row;
    col = _col;
}

Point2::Point2(const Point2& original)
{
    row = original.row;
    col = original.col;
}

int Point2::hash()const
{
    return ((0x0000ffff & col) << 16) | (0x0000ffff & row);
    // return std::hash<int>{}(row) ^ (std::hash<int>{}(col) << 1);
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

std::ostream& operator<<(std::ostream& stream, const Point2& point)
{
    stream << "{\"row\": " << point.row << ", \"col\": " << point.col << "}";
    return stream;
}

