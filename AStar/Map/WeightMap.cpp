#include "WeightMap.h"

const float* WeightMap::map_vals()const { return _map; }
const int    WeightMap::    rows()const { return _rows;}
const int    WeightMap::    cols()const { return _cols;}
const int    WeightMap::  ncells()const { return rows() * cols(); }
float        WeightMap::operator[](const int index)const
{
    if (index < 0)        return MAX_WEIGHT;
    if (index >= ncells())return MAX_WEIGHT;
    return _map[index];
}

float        WeightMap::operator[](const Point& index)const
{
    return (*this)[index.row * cols() + index.col];
}

WeightMap::WeightMap(int rows, int cols, const float* map)
{
    assert(map);
   _rows = rows;
   _cols = cols;
   _map = (float*)malloc(ncells() * sizeof(float));
    assert(_map);
   memcpy(_map, map, ncells() * sizeof(float));
}
WeightMap::~WeightMap()
{
    if (_map != NULL)free(_map);
}
float WeightMap::operator() (const int row, const int col) const
{
    int index = row * cols() + col;
    if (index >= ncells()) return MAX_WEIGHT;
    if (index < 0) return MAX_WEIGHT;
    return _map[index];
}
float& WeightMap::operator() (const int row, const int col)
{
    int index = row * cols() + col;
    assert(index < ncells());
    assert(index > 0);
    return _map[index];
}
std::ostream& operator<<(std::ostream& stream, const WeightMap& map)
{
    stream << "{\n \"rows\": "<< map.rows()<< ",\n"; 
    stream <<    " \"cols\": "<< map.cols()<< ",\n";
    stream <<    " \"map\" : "<<"\n [\n";
    for (int row = 0; row < map.rows(); row++) 
    {
        stream << "  ";
        for (int col = 0; col < map.cols(); col++)
        {
            stream << std::setw(4) << std::setfill(' ') << map(row, col) << ((col != map.cols() - 1) ? "," : "");
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