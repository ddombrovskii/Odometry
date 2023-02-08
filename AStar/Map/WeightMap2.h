#pragma once
#include <iostream>
#include <iomanip>
#include <cassert>
#include "../Point/Point2.h"

#define MAX_WEIGHT 1000.0f
#define MIN_WEIGHT 1.0f

struct WeightMap2
{
private:
    float* _map;
    int    _rows;
    int    _cols;
	
public:
    const float* map_vals()const;
    const int        rows()const;
    const int        cols()const;
    const int      ncells()const;
    float        operator[](const int    index)const;
    float        operator[](const Point2& index)const;
    float        operator()(const int row, const int col) const;
    float&       operator[](const int    index);
    float&       operator[](const Point2& index);
    float&       operator()(const int row, const int col);
    WeightMap2(int rows, int cols, const float* map);
    ~WeightMap2();
    friend std::ostream& operator<<(std::ostream& stream, const WeightMap2& point);
};