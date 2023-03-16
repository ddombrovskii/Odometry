#pragma once
#include <iostream>

struct Point3
{
public:
    static const Point3 Zero;
    static const Point3 MinusOne;

    static std::size_t hash_points_pair(const Point3& p1, const Point3& p2);
    
    std::size_t hash()const;

    int row, col, layer;

    Point3(int _row = 0, int _col = 0, int layer = 0);

    Point3(const Point3& original);

    Point3& operator = (const Point3& point);

    bool operator ==(const Point3& point)const;

    Point3 operator+(const Point3& o)const;

    Point3 operator-(const Point3& o)const;
	
    int manhattan_distance(const Point3& o)const;

    int magnitude_sqr()const;

    int distance_sqr(const Point3& o)const;

    float magnitude_sqrf()const;

    float distance_sqrf(const Point3& o)const;

    friend std::ostream& operator <<(std::ostream& stream, const Point3& point);
};