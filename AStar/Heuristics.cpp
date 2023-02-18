#include "Heuristics.h"

float manhattan_distance_2d(const Point2& p1, const Point2& p2)
{
	return abs(p1.row - p2.row) + abs(p1.col - p2.col);
}

float manhattan_distance_min_2d(const Point2& p1, const Point2& p2)
{
	return MIN(abs(p1.row - p2.row), abs(p1.col - p2.col));
}

float manhattan_distance_max_2d(const Point2& p1, const Point2& p2)
{
	return MAX(abs(p1.row - p2.row), abs(p1.col - p2.col));
}

float diagonal_distance_2d(const Point2& p1, const Point2& p2) 
{
	float dx = abs(p1.row - p2.row);
	float dy = abs(p1.col - p2.col);
	return  LINEAR * (dx + dy) + (DIAGONAL_2D - 2 * LINEAR) * MIN(dx, dy);
}


float euclidean_distance_sqr_2d(const Point2& p1, const Point2& p2)
{
	return (p1.row - p2.row) * (p1.row - p2.row) + (p1.col - p2.col) * (p1.col - p2.col);
}

float euclidean_distance_2d(const Point2& p1, const Point2& p2)
{
	return  sqrtf(euclidean_distance_sqr_2d(p1, p2));
}

float manhattan_distance_3d(const Point3& p1, const Point3& p2)
{
	return abs(p1.row - p2.row) + abs(p1.col - p2.col) + abs(p1.layer - p2.layer);
}

float manhattan_distance_min_3d(const Point3& p1, const Point3& p2)
{
	return MIN(MIN(abs(p1.row - p2.row), abs(p1.col - p2.col)), abs(p1.layer - p2.layer));
}

float manhattan_distance_max_3d(const Point3& p1, const Point3& p2)
{
	return MAX(MAX(abs(p1.row - p2.row), abs(p1.col - p2.col)), abs(p1.layer - p2.layer));
}

float euclidean_distance_sqr_3d(const Point3& p1, const Point3& p2)
{
	return (p1.row   - p2.row  ) * (p1.row   - p2.row) +
		   (p1.col   - p2.col  ) * (p1.col   - p2.col) +
		   (p1.layer - p2.layer) * (p1.layer - p2.layer);
}


float diagonal_distance_3d(const Point3& p1, const Point3& p2)
{
	float dx = abs(p1.row   - p2.row  );
	float dy = abs(p1.col   - p2.col  );
	float dz = abs(p1.layer - p2.layer);
	return  LINEAR * (dx + dy) + (DIAGONAL_3D - 2.0 * LINEAR) * MIN(dx, dy);  // maybe for 3d :  ... + (DIAGONAL_3D - 3.0 * LINEAR) * ... ???
}


float euclidean_distance_3d(const Point3& p1, const Point3& p2)
{
	return  sqrtf(euclidean_distance_sqr_3d(p1, p2));
}

Heuristic2d resolve_heuristic_2d(const int& heuristic)
{
	if (heuristic == MANHATTAN_DISTANCE)    return manhattan_distance_2d;
	if (heuristic == MANHATTAN_DISTANCE_MAX)return manhattan_distance_max_2d;
	if (heuristic == MANHATTAN_DISTANCE_MIN)return manhattan_distance_min_2d;
	if (heuristic == EUCLIDEAN_SQR)         return euclidean_distance_sqr_2d;
	if (heuristic == EUCLIDEAN)             return euclidean_distance_2d;
	if (heuristic == DIAGONAL)              return diagonal_distance_2d;
	return manhattan_distance_2d;
}

Heuristic3d resolve_heuristic_3d(const int& heuristic)
{
	if (heuristic == MANHATTAN_DISTANCE)    return manhattan_distance_3d;
	if (heuristic == MANHATTAN_DISTANCE_MAX)return manhattan_distance_max_3d;
	if (heuristic == MANHATTAN_DISTANCE_MIN)return manhattan_distance_min_3d;
	if (heuristic == EUCLIDEAN_SQR)         return euclidean_distance_sqr_3d;
	if (heuristic == EUCLIDEAN)             return euclidean_distance_3d;
	if (heuristic == DIAGONAL)              return diagonal_distance_3d;
	return manhattan_distance_3d;
}