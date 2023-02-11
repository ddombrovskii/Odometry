#ifndef __PATH_FINDER_H__
#define __PATH_FINDER_H__
#include "AStar/AStar2.h"
#include "AStar/AStar3.h"

#ifdef _WIN32
	#define DLL_EXPORT  __declspec( dllexport )
#else
	#define DLL_EXPORT
#endif

#ifdef __cplusplus
extern "C"
{
#endif
	struct Pt2
	{
		int row, col;
	};

	struct Pt3
	{
		int row, col, layer;
	};

	struct Path2
	{
		float       cost;
		int     n_points;
		Pt2* path_points;
	};

	struct Path3
	{
		float       cost;
		int     n_points;
		Pt3* path_points;
	};

	struct Map2
	{
		int cols, rows;
		const float* weights;
	};
	
	struct Map3
	{
		int cols, rows, layers;
		const float* weights;
	};

	DLL_EXPORT Map2* map_2_new(const int rows, const int cols, const float* map);
	DLL_EXPORT void  map_2_del(Map2* map);
	DLL_EXPORT Map3* map_3_new(const int rows, const int cols, const int layers, const float* map);
	DLL_EXPORT void  map_3_del(Map3* map);


	DLL_EXPORT Path2*   path_2_new(const int n_points);
	DLL_EXPORT void     path_2_del(Path2* path);
	DLL_EXPORT Path2*  find_path_2(const Map2* map, const Pt2* start, const  Pt2* end, int heuristics);


	DLL_EXPORT Path3*   path_3_new(const int n_points);
	DLL_EXPORT void     path_3_del(Path3* path);
	DLL_EXPORT Path3*  find_path_3(const Map3* map, const Pt3* start, const Pt3* end, int heuristics);
	// DLL_EXPORT void     print_map2(const Map2* map);
#ifdef __cplusplus
}
#endif
#endif // __PATH_FINDER_H__