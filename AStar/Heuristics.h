#pragma once
#include "Point/Point2.h"
#include "Point/Point3.h"
#define MANHATTAN_DISTANCE 0
#define MANHATTAN_DISTANCE_MIN 1
#define MANHATTAN_DISTANCE_MAX 2
#define EUCLIDEAN_SQR 3
#define EUCLIDEAN 4
#define DIAGONAL 5
#define LINEAR 1.0f
#define DIAGONAL_2D 1.4142135623730951f
#define DIAGONAL_3D 1.7320508075688772f
#define MIN(a, b) (((a) < (b)) ? (a) : (b))
#define MAX(a, b) (((a) > (b)) ? (a) : (b))

typedef float (*Heuristic2d)(const Point2& p1, const Point2& p2);
typedef float (*Heuristic3d)(const Point3& p1, const Point3& p2);

float manhattan_distance_2d     (const Point2& p1, const Point2& p2);
float manhattan_distance_min_2d (const Point2& p1, const Point2& p2);
float manhattan_distance_max_2d (const Point2& p1, const Point2& p2);
float diagonal_distance_2d      (const Point2& p1, const Point2& p2);
float euclidean_distance_sqr_2d (const Point2& p1, const Point2& p2);
float euclidean_distance_2d     (const Point2& p1, const Point2& p2);
float manhattan_distance_3d     (const Point3& p1, const Point3& p2);
float manhattan_distance_min_3d (const Point3& p1, const Point3& p2);
float manhattan_distance_max_3d (const Point3& p1, const Point3& p2);
float diagonal_distance_3d      (const Point3& p1, const Point3& p2);
float euclidean_distance_sqr_3d (const Point3& p1, const Point3& p2);
float euclidean_distance_3d     (const Point3& p1, const Point3& p2);
Heuristic2d resolve_heuristic_2d(const int& heuristic);
Heuristic3d resolve_heuristic_3d(const int& heuristic);