#include "WeightMap3.h"

const float* WeightMap3::map_vals()const { return _map; }
const int    WeightMap3::    rows()const { return _rows;}
const int    WeightMap3::    cols()const { return _cols;}
const int    WeightMap3::  layers()const { return _layers;}
const int    WeightMap3::  ncells()const { return rows() * cols() * layers(); }
float        WeightMap3::operator[](const int& index)const
{
    if (index < 0)        return MAX_WEIGHT;
    if (index >= ncells())return MAX_WEIGHT;
    return _map[index];
}
float        WeightMap3::operator[](const Point3& index)const
{
    return (*this)[(index.layer * rows()  + index.row) * cols() + index.col];
}
float        WeightMap3::operator()(const int& row, const int& col, const int& layer) const
{
    int index = (layer * rows() + row) * cols() + col;
    if (index >= ncells()) return MAX_WEIGHT;
    if (index < 0) return MAX_WEIGHT;
    return _map[index];
}
float&       WeightMap3::operator[](const int& index)
{
    assert(index < 0);
    assert(index >= ncells());
    return _map[index];
}
float&       WeightMap3::operator[](const Point3& index)
{
    return (*this)[(index.layer * rows()  + index.row) * cols() + index.col];
}
float&       WeightMap3::operator()(const int& row, const int& col, const int& layer)
{
    int index = (layer * rows() + row) * cols() + col;
    assert(index < ncells());
    assert(index > 0);
    return _map[index];
}
WeightMap3::WeightMap3(const int& rows, const int& cols, const int& layers, const float* map)
{
    assert(map);
   _rows = rows;
   _cols = cols;
   _layers = layers;
   _map = (float*)malloc(ncells() * sizeof(float));
    assert(_map);
   memcpy(_map, map, ncells() * sizeof(float));
}
WeightMap3::~WeightMap3()
{
    if (_map != NULL)free(_map);
}
std::ostream& operator<<(std::ostream& stream, const WeightMap3& map)
{
stream << "{\n";
stream << " \"rows\"   : " << map.rows() << ",\n";
stream << " \"cols\"   : " << map.cols() << ",\n";
stream << " \"layers\" : " << map.layers() << ",\n";
stream << " \"map\"    : " << "\n [\n";
for (int layer = 0; layer < map.layers(); layer++)
{
    stream << "// layer " << layer << "\n";
    for (int row = 0; row < map.rows(); row++)
    {
        stream << "  ";
        for (int col = 0; col < map.cols(); col++)
        {
            stream << std::fixed << std::setw(10) << std::setprecision(3) << std::setfill(' ') << map(row, col, layer) << ((col != map.cols() - 1) ? "," : "");
        }
        if (row != map.rows() - 1)
        {
            stream << ",\n";
            continue;
        }
    }
    if (layer != map.layers() - 1)
    {
        stream << ",\n";
        continue;
    }
    stream << "\n ]\n";

    stream << "}";
}

return stream;
}