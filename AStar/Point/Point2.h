#pragma once
#include <iostream>
#define I16 short int
#define Points2dPairHash long long int
#define MASK_X_64 ((Points2dPairHash)0xffffffff)

struct Point2
{
public:
    I16 row, col;

    static const Point2 Zero;
    static const Point2 MinusOne;
    static Point2 unhash(const int& hash);
    static int cross(const Point2& p1, const Point2& p2);
    static Points2dPairHash hash_points_pair(const Point2& p1, const Point2& p2);
    static void unhash_points_pair(const Points2dPairHash& pair_hash, Point2& p1, Point2& p2);

    int hash()const;

    Point2(I16 _row = 0, I16 _col = 0);

    Point2(const Point2& original);

    Point2& operator = (const Point2& point);

    bool operator ==(const Point2& point)const;

    Point2 operator+(const Point2& o)const;

    Point2 operator-(const Point2& o)const;

    friend std::ostream& operator <<(std::ostream& stream, const Point2& point);
};