#pragma once
#include <iostream>

struct Point 
{

public:
    static const Point Zero;
    static const Point MinusOne;

    int row, col;

    Point(int _row = 0, int _col = 0);

    Point& operator = (const Point& point);

    bool operator ==(const Point& point)const;

    Point operator+(const Point& o)const;

    Point operator-(const Point& o)const;
	
    int manhattan_distance(const Point& o)const;

    int magnitude_sqr()const;

    int distance_sqr(const Point& o)const;

    float magnitude_sqrf()const;

    float distance_sqrf(const Point& o)const;

    friend std::ostream& operator <<(std::ostream& stream, const Point& point);
};