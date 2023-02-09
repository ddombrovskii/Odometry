#pragma once
#include <iostream>

struct Point2
{

public:
    static const Point2 Zero;
    static const Point2 MinusOne;

    int row, col;

    Point2(int _row = 0, int _col = 0);

    Point2& operator = (const Point2& point);

    bool operator ==(const Point2& point)const;

    Point2 operator+(const Point2& o)const;

    Point2 operator-(const Point2& o)const;
	
    int manhattan_distance(const Point2& o)const;

    int magnitude_sqr()const;

    int distance_sqr(const Point2& o)const;

    float magnitude_sqrf()const;

    float distance_sqrf(const Point2& o)const;

    friend std::ostream& operator <<(std::ostream& stream, const Point2& point);
};