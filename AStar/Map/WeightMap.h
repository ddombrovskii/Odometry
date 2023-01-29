#pragma once
#include <iostream>
#include <iomanip>
#include <cassert>
#define MAX_WEIGHT 1.0
#define MIN_WEIGHT 0.0

struct WeightMap
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
    float        operator[](const int index)const;

    WeightMap(int rows, int cols, const float* map);
    
    ~WeightMap();

    float operator() (const int row, const int col) const;

    float& operator() (const int row, const int col);

    friend std::ostream& operator<<(std::ostream& stream, const WeightMap& point);
};