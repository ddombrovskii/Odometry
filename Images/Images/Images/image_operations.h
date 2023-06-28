#ifndef __IMAGE_OPERATIONS_H__
#define __IMAGE_OPERATIONS_H__
#include "stb_image.h"
#include "stb_image_write.h"
#include "Transform.h"


#ifdef __cplusplus
extern "C"
{
#endif

typedef I32(*Interplator)(F32, F32, const Image*);

CSTR get_filename_ext(CSTR filename);

DLL_EXPORT Image*     image_new (I32 rows, I32 cols, I8 bpp);
	       
DLL_EXPORT void       image_del (Image* image);
	       
DLL_EXPORT Image*     image_load(CSTR src) ;
	       
DLL_EXPORT I8         image_save(const Image* image, CSTR dst) ;

DLL_EXPORT void image_clear_color(Image* image, I32 color);

UI8 between(F32 x, F32 min, F32 max);

I32 red  (UI8 r);

I32 green(UI8 r);

I32 blue (UI8 r);

I32 alpha(UI8 r);

I32 rgb  (UI8 r, UI8 g, UI8 b);

I32 rgba (UI8 r, UI8 g, UI8 b, UI8 a);

I32 redf (F32 r);

I32 greenf(F32 r);

I32 bluef (F32 r);

I32 alphaf(F32 r);

I32 rgbf  (F32 r, F32 g, F32 b);

I32 rgbaf (F32 r, F32 g, F32 b, F32 a);

Interplator  resolve_inerp_function(UI8 interpolation_method);

F32 cubic_poly    (F32 x,   F32 y,   const F32* coefficients);

UI8 channel       (I32 row, I32 col, const Image* image, UI8 layer);
			      
I32 channelI32    (I32 row, I32 col, const Image* image, UI8 layer);
			      
F32 channelF32    (I32 row, I32 col, const Image* image, UI8 layer);

F32 x_derivative  (I32 row, I32 col, const Image* image, UI8 layer);
				  
F32 y_derivative  (I32 row, I32 col, const Image* image, UI8 layer);
				  
F32 xy_derivative (I32 row, I32 col, const Image* image, UI8 layer);

DLL_EXPORT I32 nearest32 (F32 x, F32 y, const Image* image);

DLL_EXPORT I32 bilinear32(F32 x, F32 y, const Image* image);

DLL_EXPORT I32 bicubic32 (F32 x, F32 y, const Image* image);

void expand_bounds(const Mat3& tm, const Image& src, I32& width, I32& height);

DLL_EXPORT Image* transform(const F32* transform, const Image* src, const  UI8 interp_f, const UI8 expand);

DLL_EXPORT Image* rescale (const F32* transform,  const Image* src, const  UI8 interp_f, const UI8 expand);
					     
DLL_EXPORT I32  get_pix  (I32 row, I32 col, const Image* img);

DLL_EXPORT I32  get_uv   (F32 row, F32 col, const Image* img, const UI8 interp_f);
					     
DLL_EXPORT I8   set_pix  (I32 color, I32 row, I32 col, Image* img);

#ifdef __cplusplus
}
#endif
#endif // __MAIN_H__