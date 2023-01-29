#ifndef __PATH_FINDER_H__
#define __PATH_FINDER_H__
#define DLL_EXPORT __declspec(dllexport)
#include "AStar/AStar.h"

#ifdef __cplusplus
extern "C"
{
#endif
	struct Pt2
	{
		int row, col;
	};

	struct Path
	{
		float       cost;
		int     n_points;
		Pt2* path_points;
	};
	DLL_EXPORT AStar* a_start_new(const int rows, const int cols, const float* weights);
	DLL_EXPORT void   a_start_del(AStar* a_star);
	DLL_EXPORT Path*     path_new(const int n_points);
	DLL_EXPORT void      path_del(Path* path);
	DLL_EXPORT Path*    find_path(AStar* path_finder, const Pt2* start, const  Pt2* end);
#ifdef __cplusplus
}
#endif
#endif // __PATH_FINDER_H__