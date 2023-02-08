#include "WeightMap2.h"

const float* WeightMap2::map_vals()const { return _map; }
const int    WeightMap2::    rows()const { return _rows;}
const int    WeightMap2::    cols()const { return _cols;}
const int    WeightMap2::  ncells()const { return rows() * cols(); }
float        WeightMap2::operator[](const int index)const
{
    if (index < 0)        return MAX_WEIGHT;
    if (index >= ncells())return MAX_WEIGHT;
    return _map[index];
}
float        WeightMap2::operator[](const Point2& index)const
{
    return (*this)[index.row * cols() + index.col];
}
float        WeightMap2::operator() (const int row, const int col) const
{
    int index = row * cols() + col;
    if (index >= ncells()) return MAX_WEIGHT;
    if (index < 0) return MAX_WEIGHT;
    return _map[index];
}
float&       WeightMap2::operator[](const int index)
{
    assert(index < 0);
    assert(index >= ncells());
    return _map[index];
}
float&       WeightMap2::operator[](const Point2& index)
{
    return (*this)[index.row * cols() + index.col];
}
float&       WeightMap2::operator() (const int row, const int col)
{
    int index = row * cols() + col;
    assert(index < ncells());
    assert(index > 0);
    return _map[index];
}
WeightMap2::WeightMap2(int rows, int cols, const float* map)
{
    assert(map);
   _rows = rows;
   _cols = cols;
   _map = (float*)malloc(ncells() * sizeof(float));
    assert(_map);
   memcpy(_map, map, ncells() * sizeof(float));
}
WeightMap2::~WeightMap2()
{
    if (_map != NULL)free(_map);
}
std::ostream& operator<<(std::ostream& stream, const WeightMap2& map)
{
stream << "{\n";
stream << " \"rows\": " << map.rows() << ",\n";
stream << " \"cols\": " << map.cols() << ",\n";
stream << " \"map\" : " << "\n [\n";
for (int row = 0; row < map.rows(); row++)
{
    stream << "  ";
    for (int col = 0; col < map.cols(); col++)
    {
        stream << std::fixed << std::setw(10) << std::setprecision(3) << std::setfill(' ') << map(row, col) << ((col != map.cols() - 1) ? "," : "");
    }
    if (row != map.rows() - 1)
    {
        stream << ",\n";
        continue;
    }
    stream << "\n ]\n";
}
stream << "}";

return stream;
}