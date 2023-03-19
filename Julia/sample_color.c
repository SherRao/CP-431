#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdarg.h>

#include <complex.h>
#include <math.h>

#define PNG_DEBUG 3
#include <png.h>

int x, y;
#define MAX_ITER 250

int width, height;
png_byte color_type;
png_byte bit_depth;

png_structp png_ptr;
png_infop info_ptr;
int number_of_passes;
png_bytep *row_pointers;

char *file = "a.png";

void read_png_file(char *file_name)
{
    // char header[8]; // 8 is the maximum size that can be checked

    // /* open file and test for it being a png */
    // FILE *fp = fopen(file_name, "rb");
    // fread(header, 1, 8, fp);
    // if (png_sig_cmp(header, 0, 8))
    //     printf("[read_png_file] File %s is not recognized as a PNG file", file_name);
    // FILE *fp = fopen(file_name, "wb");
    // if (!fp)
    //     printf("[write_png_file] File %s could not be opened for writing", file_name);

    // Start PNG
    width = 10000;
    height = 10000;
    color_type = PNG_COLOR_TYPE_RGBA; // png_get_color_type(png_ptr, info_ptr);
    bit_depth = 8;                    // png_get_bit_depth(png_ptr, info_ptr);

    number_of_passes = 1;

    row_pointers = (png_bytep *)malloc(sizeof(png_bytep) * height);
    for (y = 0; y < height; y++)
        row_pointers[y] = (png_byte *)malloc(sizeof(png_bytep) * width);

    // CHANGE PIXELS
    for (y = 0; y < height; y++)
    {
        png_byte *row = row_pointers[y];
        for (x = 0; x < width; x++)
        {
            png_byte *ptr = &(row[x * 4]);

            /*double complex tmp = 0.0 + 0.0 * I;
            double complex c = 0.285 + 0.01 * I;
            double complex z = ((float) x) + ((float)y) * I;

            int bit = 0;

            for (int i = 0; i < MAX_ITER; i++)
            {
                float tmp = zx * zx - zy * zy + cx;
                zy = 2.0 * zx * zy + cy;
                zx = tmp;

                if ( fabs (creal(z * z) + cimag(z))  > 4.0)
                {
                    bit = 1;
                    break;
                }
            }
            */
            int bit = 0;
            float scale = 1.5;
            float cx = -0.8;
            float cy = 0.156;
            float zx = scale * (float)(width / 2 - x) / (width / 2);
            float zy = scale * (float)(height / 2 - y) / (height / 2);
            int i;
            for (i = 0; i < MAX_ITER; i++)
            {
                float tmp = zx * zx - zy * zy + cx;
                zy = 2.0 * zx * zy + cy;
                zx = tmp;
                if (zx * zx + zy * zy > 4.0)
                {
                    bit = (int) i/50;
                    break;
                }
            }

            // printf("%.2f - %.2f<> %d %d\n", creal(z), cimag(z), x, y);

            if (bit == 0){
                ptr[0] = 50;
                ptr[1] = 0;
                ptr[2] = 0;
            }
            else if(bit == 1){
                ptr[0] = 255;
                ptr[1] = 0;
                ptr[2] = 0;
            }
            else if (bit == 2)
            {
                ptr[0] = 0;
                ptr[1] = 255;
                ptr[2] = 0;
            }
            else if (bit == 3)
            {
                ptr[0] = 0;
                ptr[1] = 0;
                ptr[2] = 255;
            }
            else if (bit == 4)
            {
                ptr[0] = 100;
                ptr[1] = 70;
                ptr[2] = 0;
            }
            else if (bit == 5)
            {
                ptr[0] = 40;
                ptr[1] = 150;
                ptr[2] = 0;
            }

            ptr[3] = 255;
        } // printf("\n");
    }

    // Start File
    FILE *fp = fopen(file_name, "wb");
    if (!fp)
        printf("[write_png_file] File %s could not be opened for writing", file_name);

    /* initialize stuff */
    png_ptr = png_create_write_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);

    if (!png_ptr)
        printf("[write_png_file] png_create_write_struct failed");

    info_ptr = png_create_info_struct(png_ptr);
    if (!info_ptr)
        printf("[write_png_file] png_create_info_struct failed");

    if (setjmp(png_jmpbuf(png_ptr)))
        printf("[write_png_file] Error during init_io");

    png_init_io(png_ptr, fp);

    /* write header */
    if (setjmp(png_jmpbuf(png_ptr)))
        printf("[write_png_file] Error during writing header");

    png_set_IHDR(png_ptr, info_ptr, width, height,
                 bit_depth, color_type, PNG_INTERLACE_NONE,
                 PNG_COMPRESSION_TYPE_BASE, PNG_FILTER_TYPE_BASE);

    png_write_info(png_ptr, info_ptr);

    /* write bytes */
    if (setjmp(png_jmpbuf(png_ptr)))
        printf("[write_png_file] Error during writing bytes");

    png_write_image(png_ptr, row_pointers);

    /* end write */
    if (setjmp(png_jmpbuf(png_ptr)))
        printf("[write_png_file] Error during end of write");

    png_write_end(png_ptr, NULL);

    /* cleanup heap allocation */
    for (y = 0; y < height; y++)
        free(row_pointers[y]);
    free(row_pointers);

    fclose(fp);
}

int main(int argc, char **argv)
{

    read_png_file(file);
    return 0;
}