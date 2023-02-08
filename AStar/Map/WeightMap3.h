#pragma once
#include <iostream>
#include <iomanip>
#include <cassert>
#include "../Point/Point3.h"

#define MAX_WEIGHT 1000.0f
#define MIN_WEIGHT 1.0f

struct WeightMap3
{
private:
    float* _map;
    int    _rows;
    int    _cols;
	int    _layers;
	
public:
    const float* map_vals()const;
    const int        rows()const;
    const int        cols()const;
	const int      layers()const;
    const int      ncells()const;
    float        operator[](const int&     index)const;
    float        operator[](const Point3& index)const;
    float        operator()(const int& row, const int& col, const int& layer) const;
    float&       operator[](const int&     index);
    float&       operator[](const Point3& index);
    float&       operator()(const int& row, const int& col, const int& layer);
    WeightMap3(const int& rows,const int& cols, const int& layers, const float* map);
    ~WeightMap3();
    friend std::ostream& operator<<(std::ostream& stream, const WeightMap3& point);
};